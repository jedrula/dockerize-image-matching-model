from enum import Enum
import cv2
import os
import numpy as np
import torch
import matplotlib.pyplot as plt
import kornia as K
import kornia.feature as KF 
from kornia_moons.viz import draw_LAF_matches
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

#setting up device
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

#initializing api insance
app = FastAPI()
print("API is ready to use")

# Add CORS middleware
app.add_middleware(
  CORSMiddleware,
  allow_origins=["http://localhost:5173"],  # Allow this origin
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"],
)

#Load model
matcher = KF.LoFTR(pretrained=None)
matcher.load_state_dict(torch.load("./models/loftr_outdoor.ckpt")['state_dict'])
matcher = matcher.to(device).eval()

#bytes-image to tensor
def get_tensor_image(img_bytes):
  img = np.asarray(bytearray(img_bytes), dtype="uint8")
  img = cv2.imdecode(img, cv2.IMREAD_COLOR)
  scale = 840 / max(img.shape[0], img.shape[1]) 
  w = int(img.shape[1] * scale)
  h = int(img.shape[0] * scale)
  img = cv2.resize(img, (w, h))
  img = K.image_to_tensor(img, False).float() /255.
  img = K.color.bgr_to_rgb(img)
  return {"img": img.to(device), "w": w, "h": h}

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
  inliers = inliers > 0

  matched_points = []
  for pt0, pt1, inlier in zip(mkpts0, mkpts1, inliers):
    if inlier:
      matched_points.append({
        "point1": {"x": pt0[0], "y": pt0[1]},
        "point2": {"x": pt1[0], "y": pt1[1]}
      })

  return matched_points

# image1: UploadFile = File(...), image2: UploadFile = File(...)
@app.post("/get_matching_matrix")
async def get_matching_matrix():
  img1_path = os.path.join('./images', 'szczytna', 'widokowa', 'widokowa2.png')
  tensor1 = get_tensor_image(open(img1_path, "rb").read());
  img1 = tensor1['img']
  img2_path = os.path.join('./test-user-images', 'szczytnik_gdzies1.jpeg')
  tensor2 = get_tensor_image(open(img2_path, "rb").read());
  img2 = tensor2['img']
  matched_points = await getMatchingMatrix(img1, img2)
  return {"matched_points": matched_points, "image1": {"width": tensor1['w'], "height": tensor1['h'], "path": img1_path}, "image2": {"width": tensor2['w'], "height": tensor2['h'], "path": img2_path}}


@app.post("/get_matching_with")
async def get_matching_with(image1: UploadFile = File(...), image_path: str = ""):
  img1 = get_tensor_image(await image1.read())['img']
  img2 = get_tensor_image(open(image_path, "rb").read())['img']
  return await process_matching(img1, img2)

@app.post("/get_matching")
async def get_matching(image1: UploadFile = File(...), image2: UploadFile = File(...)):
  img1 = get_tensor_image(await image1.read())['img']
  img2 = get_tensor_image(await image2.read())['img']
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
    if filename.endswith(".jpg") or filename.endswith(".png"):
      images.append(os.path.join(folder_path, filename))
  return images

class RegionName(str, Enum):
  stokowka = "stokowka"
  szczytna_widokowa = "szczytna_widokowa"

def regionNameToPath(region_name):
  return region_name.replace("_", "/")

# possible files we match against are in ./images/stokowka folder. File names are pologa.jpg, przewiecha.jpg, zachodnia.jpg
@app.post("/find_match")
async def find_match(folder_path: RegionName, image1: UploadFile = File(...)):
  img1 = get_tensor_image(await image1.read())['img']
  compare_images = findFolderImages(f"./images/{regionNameToPath(folder_path)}")

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
  

@app.get("/ui")
async def get_ui():
  return FileResponse("./ui/index.html", media_type="text/html")
