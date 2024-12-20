from enum import Enum
import cv2
import numpy as np
import torch
import matplotlib.pyplot as plt
import kornia as K
import kornia.feature as KF 
from kornia_moons.viz import draw_LAF_matches
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse

#setting up device
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(device)

#initializing api insance
app = FastAPI()
print("API is ready to use")

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
    return img.to(device)

@app.post("/get_matching")
async def get_matching(image1: UploadFile = File(...), image2: UploadFile = File(...)):
    img1 = get_tensor_image(await image1.read())
    img2 = get_tensor_image(await image2.read())

    input_dict = {"image0": K.color.rgb_to_grayscale(img1), 
              "image1": K.color.rgb_to_grayscale(img2)}

    with torch.no_grad():
        correspondences = matcher(input_dict)

    mkpts0 = correspondences['keypoints0'].cpu().numpy()
    mkpts1 = correspondences['keypoints1'].cpu().numpy()
    Fm, inliers = cv2.findFundamentalMat(mkpts0, mkpts1, cv2.USAC_MAGSAC, 0.5, 0.999999, 10000)
    inliers = inliers > 0   

    # Determine the number of matches to display
    num_matches = min(mkpts0.shape[0], 20)

    # Select a random subset of 20 matches if there are more than 20 matches
    if mkpts0.shape[0] > 20:
        selected_indices = torch.randperm(mkpts0.shape[0])[:num_matches]
    else:
        selected_indices = torch.arange(mkpts0.shape[0])

    # Use the selected indices to filter matches
    filtered_mkpts0 = mkpts0[selected_indices]
    filtered_mkpts1 = mkpts1[selected_indices]
    filtered_inliers = inliers[selected_indices] if inliers is not None else None

    # Now, use the filtered matches in draw_LAF_matches
    fig, ax = draw_LAF_matches(
        KF.laf_from_center_scale_ori(torch.from_numpy(filtered_mkpts0).view(1, -1, 2),
                                    torch.ones(num_matches).view(1, -1, 1, 1),
                                    torch.ones(num_matches).view(1, -1, 1)),
        KF.laf_from_center_scale_ori(torch.from_numpy(filtered_mkpts1).view(1, -1, 2),
                                    torch.ones(num_matches).view(1, -1, 1, 1),
                                    torch.ones(num_matches).view(1, -1, 1)),
        torch.arange(num_matches).view(-1,1).repeat(1,2),  # Adjusted indices for drawing
        K.tensor_to_image(img1),
        K.tensor_to_image(img2),
        filtered_inliers,  # Use the filtered inliers
        draw_dict={'inlier_color': (0.2, 1, 0.2),
                  'tentative_color': None,
                  'feature_color': (0.2, 0.5, 1), 'vertical': False}, return_fig_ax=True)

    ax.axis('off')
    plt.savefig('output.jpg', bbox_inches='tight')
    return FileResponse("./output.jpg", media_type="image/jpeg")

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
    import os
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
    img1 = get_tensor_image(await image1.read())
    compare_images = findFolderImages(f"./images/{regionNameToPath(folder_path)}")

    scores = []

    for img in compare_images:
        # img2 = get_tensor_image(open(f"./images/stokowka/{img}", "rb").read())
        img2 = get_tensor_image(open(img, "rb").read())
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
    
