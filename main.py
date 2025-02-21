from enum import Enum
import cv2
import json
import os
import numpy as np
import base64
import torch
import matplotlib.pyplot as plt
import kornia as K
import kornia.feature as KF 
from kornia_moons.viz import draw_LAF_matches
from fastapi import FastAPI, Form, UploadFile, File
from pydantic import BaseModel
from fastapi.responses import FileResponse, JSONResponse
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional


#setting up device
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

#initializing api insance
app = FastAPI()
print("API is ready to use")

# Add CORS middleware
app.add_middleware(
  CORSMiddleware,
  allow_origins=["http://localhost:5173", "https://topomatch.surge.sh", "https://jedrula.github.io"],
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"],
)

# this could help with warping
# https://huggingface.co/spaces/Realcat/image-matching-webui
# https://github.com/Vincentqyw/image-matching-webui

# this has some basic code, maybe useful: https://learnopencv.com/homography-examples-using-opencv-python-c/
# https://github.com/Eric-Canas/Homography.js - this might be awesome - it's on the frontend!

#Load model
matcher = KF.LoFTR(pretrained=None)
matcher.load_state_dict(torch.load("./models/loftr_outdoor.ckpt")['state_dict'])
matcher = matcher.to(device).eval()

class RegionData(BaseModel):
  region_name: str
  crags: Optional[List] = []

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(
        status_code=422,
        content=jsonable_encoder({"detail": exc.errors(), "body": exc.body}),
    )

#bytes-image to tensor
def get_tensor_image(img_bytes):
  img = np.asarray(bytearray(img_bytes), dtype="uint8")
  img = cv2.imdecode(img, cv2.IMREAD_COLOR)
  original_h, original_w = img.shape[0], img.shape[1]
  print(f"Original image size: {original_w}x{original_h}")
  scale = 840 / max(original_w, original_h) 
  w = int(img.shape[1] * scale)
  h = int(img.shape[0] * scale)
  img = cv2.resize(img, (w, h))
  img = K.image_to_tensor(img, False).float() /255.
  img = K.color.bgr_to_rgb(img)
  return {"img": img.to(device), "w": w, "h": h, "original_w": original_w, "original_h": original_h}

async def process_matching(img1, img2):
  input_dict = {"image0": K.color.rgb_to_grayscale(img1),
    "image1": K.color.rgb_to_grayscale(img2)}

  with torch.no_grad():
    correspondences = matcher(input_dict)

  mkpts0 = correspondences['keypoints0'].cpu().numpy()
  mkpts1 = correspondences['keypoints1'].cpu().numpy()
  _, inliers = cv2.findFundamentalMat(mkpts0, mkpts1, cv2.USAC_MAGSAC, 0.5, 0.999999, 10000)
  inliers = (inliers > 0).flatten()

  # Generate a colormap for the lines
  colormap = plt.cm.get_cmap('hsv', len(inliers))

  fig, ax = draw_LAF_matches(
      KF.laf_from_center_scale_ori(torch.from_numpy(mkpts0).view(1, -1, 2),
                                   torch.ones(mkpts0.shape[0]).view(1, -1, 1, 1),
                                   torch.ones(mkpts0.shape[0]).view(1, -1, 1)),
      KF.laf_from_center_scale_ori(torch.from_numpy(mkpts1).view(1, -1, 2),
                                   torch.ones(mkpts1.shape[0]).view(1, -1, 1, 1),
                                   torch.ones(mkpts1.shape[0]).view(1, -1, 1)),
      torch.arange(mkpts0.shape[0]).view(-1, 1).repeat(1, 2),
      K.tensor_to_image(img1),
      K.tensor_to_image(img2),
      inliers,
      draw_dict={'inlier_color': None,  # Disable default inlier color
                 'tentative_color': None,
                 'feature_color': (0.2, 0.5, 1), 'vertical': False}, return_fig_ax=True)

  # Draw lines with varying colors
  for i, (pt0, pt1) in enumerate(zip(mkpts0[inliers], mkpts1[inliers])):
      color = colormap(i / len(inliers))[:3]  # Get RGB color from colormap
      ax.plot([pt0[0], pt1[0] + img1.shape[3]], [pt0[1], pt1[1]], color=color)

  ax.axis('off')
  plt.savefig('output.jpg', bbox_inches='tight')
  return FileResponse("./output.jpg", media_type="image/jpeg")


async def getMatchingMatrix(img1, img2):
  input_dict = {"image0": K.color.rgb_to_grayscale(img1),
    "image1": K.color.rgb_to_grayscale(img2)}

  with torch.no_grad():
    correspondences = matcher(input_dict)

  mkpts0 = correspondences['keypoints0'].cpu().numpy()
  mkpts1 = correspondences['keypoints1'].cpu().numpy()
  _, inliers = cv2.findFundamentalMat(mkpts0, mkpts1, cv2.USAC_MAGSAC, 0.5, 0.999999, 10000)
  inliers = (inliers > 0).flatten()

  matched_points = []
  for pt0, pt1, inlier in zip(mkpts0, mkpts1, inliers):
    if inlier:
      matched_points.append({
        "point1": {"x": pt0[0], "y": pt0[1]},
        "point2": {"x": pt1[0], "y": pt1[1]}
      })

  return matched_points

class ImageData(BaseModel):
    image_data: str
    folder_path: str

class TwoImagesData(BaseModel):
    image1: str
    image2: str

class CragData(BaseModel):
    name: str
    image: str


@app.post("/find_matching_matrix")
async def find_matching_matrix(data: ImageData):
  img_bytes = base64.b64decode(data.image_data)
  tensor1 = get_tensor_image(img_bytes)
  img1 = tensor1['img']
  found_images = findFolderImages(f"./images/{regionNameToPath(data.folder_path)}")
  compare_images = [img['path'] for img in found_images]

  best_match = None
  best_score = -1
  best_matched_points = None
  best_tensor_match = None

  for img in compare_images:
    tensor2 = get_tensor_image(open(img, "rb").read())
    img2 = tensor2['img']
    matched_points = await getMatchingMatrix(img1, img2)
    score = len(matched_points)

    if score > best_score:
      best_score = score
      best_match = img
      best_matched_points = matched_points
      best_tensor_match = tensor2

  # Calculate homography matrix
  mkpts0 = np.array([[pt["point1"]["x"], pt["point1"]["y"]] for pt in best_matched_points])
  mkpts1 = np.array([[pt["point2"]["x"], pt["point2"]["y"]] for pt in best_matched_points])
  H, inliers = cv2.findHomography(mkpts0, mkpts1, cv2.RANSAC, 5.0)

  # Convert homography matrix to the required format
  homography_matrix = H.flatten().tolist()

  # Calculate the inverse of the homography matrix
  H_inv = np.linalg.inv(H)
  homography_matrix_inv = H_inv.flatten().tolist()

  # Replace the extension with .json in a smart way
  base, _ = os.path.splitext(best_match)
  best_match_json_path = f"{base}.json"
  try:
    best_match_json_content = json.load(open(best_match_json_path))
  except FileNotFoundError:
    best_match_json_content = None

  # Map the points in the path property of each crag
  if best_match_json_content and "crags" in best_match_json_content:
      for crag in best_match_json_content["crags"]:
          if "path" in crag:
              crag["path"] = [
                  [
                      point[0] * best_tensor_match['w'] / best_tensor_match['original_w'],
                      point[1] * best_tensor_match['h'] / best_tensor_match['original_h']
                  ]
                  for point in crag["path"]
              ]

  return {
    "matched_points": [
      {
        "point1": {"x": float(pt["point1"]["x"]), "y": float(pt["point1"]["y"])},
        "point2": {"x": float(pt["point2"]["x"]), "y": float(pt["point2"]["y"])}
      }
      for pt in best_matched_points
    ],
    "image1": {
      "width": int(tensor1['w']),
      "height": int(tensor1['h']),
    },
    "image2": {
      "width": int(best_tensor_match['w']),
      "height": int(best_tensor_match['h']),
      "original_width": int(best_tensor_match['original_w']),
      "original_height": int(best_tensor_match['original_h']),
      "path": best_match
    },
    "best_match_json_content": best_match_json_content,
    "homography_matrix": homography_matrix,
    "homography_matrix_inverse": homography_matrix_inv
  }

@app.post("/get_matching")
async def get_matching(data: TwoImagesData):
    # Convert base64 strings to tensors
    tensor1 = get_tensor_image(base64.b64decode(data.image1))
    img1 = tensor1['img']
    tensor2 = get_tensor_image(base64.b64decode(data.image2))
    img2 = tensor2['img']

    # Get matching points
    matched_points = await getMatchingMatrix(img1, img2)

    # Calculate homography matrix
    mkpts0 = np.array([[pt["point1"]["x"], pt["point1"]["y"]] for pt in matched_points])
    mkpts1 = np.array([[pt["point2"]["x"], pt["point2"]["y"]] for pt in matched_points])
    H, inliers = cv2.findHomography(mkpts0, mkpts1, cv2.RANSAC, 5.0)

    # Convert homography matrix to the required format
    homography_matrix = H.flatten().tolist()

    # Calculate the inverse of the homography matrix
    H_inv = np.linalg.inv(H)
    homography_matrix_inv = H_inv.flatten().tolist()

    return {
        "matched_points": [
            {
                "point1": {"x": float(pt["point1"]["x"]), "y": float(pt["point1"]["y"])},
                "point2": {"x": float(pt["point2"]["x"]), "y": float(pt["point2"]["y"])}
            }
            for pt in matched_points
        ],
        "image1": {
            "width": int(tensor1['w']),
            "height": int(tensor1['h']),
        },
        "image2": {
            "width": int(tensor2['w']),
            "height": int(tensor2['h']),
        },
        "homography_matrix": homography_matrix,
        "homography_matrix_inverse": homography_matrix_inv
    }



@app.post("/get_matching_with")
async def get_matching_with(image1: UploadFile = File(...), image_path: str = ""):
  img1 = get_tensor_image(await image1.read())['img']
  img2 = get_tensor_image(open(image_path, "rb").read())['img']
  return await process_matching(img1, img2)

async def getSimilarityScore(tensorImage1, tensorImage2):
  input_dict = {"image0": K.color.rgb_to_grayscale(tensorImage1),
      "image1": K.color.rgb_to_grayscale(tensorImage2)}
  
  with torch.no_grad():
    correspondences = matcher(input_dict)
    mkpts0 = correspondences['keypoints0'].cpu().numpy()
    mkpts1 = correspondences['keypoints1'].cpu().numpy()
    Fm, inliers = cv2.findFundamentalMat(mkpts0, mkpts1, cv2.USAC_MAGSAC, 0.5, 0.999999, 10000)
    inliers = inliers > 0

  return inliers.sum()
  
def findFolderImages(folder_path):
  images = []
  for filename in os.listdir(folder_path):
    if filename.endswith(".jpg"):
      images.append({
        "path": os.path.join(folder_path, filename),
        # name without extension
        "name": os.path.splitext(filename)[0]
      })
  return images

def regionNameToPath(region_name):
  return region_name.replace("_", "/")

@app.post("/find_match")
async def find_match(folder_path: str, image1: UploadFile = File(...)):
  img1 = get_tensor_image(await image1.read())['img']
  found_images = findFolderImages(f"./images/{regionNameToPath(folder_path)}")
  compare_images = [img['path'] for img in found_images]

  scores = []

  for img in compare_images:
    img2 = get_tensor_image(open(img, "rb").read())['img']
    score = await getSimilarityScore(img1, img2)
    scores.append(int(score))  # Convert NumPy int64 to native Python int

  best_match_index = scores.index(max(scores))
  best_match = compare_images[best_match_index]
  best_score = scores[best_match_index]  # Already converted to Python int

  all_scores = dict(zip(compare_images, scores))

  return {"best_match": best_match, "score": best_score, "all_scores": all_scores}

@app.get("/images/{rest_of_path:path}")
async def get_image(rest_of_path: str):
  return FileResponse(f"./images/{rest_of_path}", media_type="image/jpeg")

@app.get("/region/{region_name}")
async def get_region(region_name: str):
  folder_path = f"./images/{regionNameToPath(region_name)}"
  found = findFolderImages(folder_path)
  return found

@app.post("/region")
async def post_region(region_data: RegionData):
    folder_path = f"./images/{regionNameToPath(region_data.region_name)}"
    os.makedirs(folder_path, exist_ok=False)
    return {"status": "ok"}

@app.get("/crag/{region_name}/{crag_name}")
async def get_crag(region_name: str, crag_name: str):
  folder_path = f"./images/{regionNameToPath(region_name)}"
  json_path = f"{folder_path}/{crag_name}.json"
  try:
    data = json.load(open(json_path))
  except FileNotFoundError:
    data = None
  return {
    "data": data,
    "image": f"{folder_path}/{crag_name}.jpg"
  }

@app.put("/crag/{region_name}/{crag_name}")
async def put_crag(region_name: str, crag_name: str, data: dict):
  folder_path = f"./images/{regionNameToPath(region_name)}"
  json_path = f"{folder_path}/{crag_name}.json"
  with open(json_path, "w") as f:
    json.dump(data, f)
  return {"status": "ok"}

@app.post("/region/{region_name}/crag")
async def add_crag(region_name: str, crag_data: CragData):
    folder_path = f"./images/{regionNameToPath(region_name)}"
    json_path = f"{folder_path}/{crag_data.name}.json"
    image_path = f"{folder_path}/{crag_data.name}.jpg"

    os.makedirs(folder_path, exist_ok=True)

    crag_data_dict = {
        "name": crag_data.name,
        "path": []
    }

    with open(json_path, "w") as f:
        json.dump(crag_data_dict, f)

    img_bytes = base64.b64decode(crag_data.image)
    with open(image_path, "wb") as img_file:
        img_file.write(img_bytes)

    return {"status": "ok"}