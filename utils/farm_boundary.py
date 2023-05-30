import cv2
from segment_anything import sam_model_registry, SamPredictor
import matplotlib.pyplot as plt
import numpy as np
import torch
import time
import os


sam_checkpoint = "model/sam_vit_h_4b8939.pth"
model_type = "vit_h"
device = device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

sam = sam_model_registry[model_type](checkpoint=sam_checkpoint)
sam.to(device)
predictor = SamPredictor(sam)


def get_final_farm_boundary(image_path: str, x_coordinate: int, y_coordinate: int):
    final_farm_mask = None
    if os.path.exists(image_path):
        image = cv2.imread(image_path)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        predictor.set_image(image)
        input_point = np.array([[x_coordinate, y_coordinate]])
        input_label = np.array([1])
        masks, scores, _ = predictor.predict(
            point_coords=input_point,
            point_labels=input_label,
            multimask_output=True,
        )
        if len(masks) > 0:
            mask = masks[np.argmax(scores)]
            contours, _ = cv2.findContours(mask.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            if len(contours) > 0:
                final_farm_mask = (255 * mask).astype(np.uint8)
                final_contour = max(contours, key=cv2.contourArea)
                cv2.drawContours(image, final_contour, -1, (0,0,255), 3)
                cv2.circle(image, (x_coordinate,y_coordinate), 3, (0,255,255), 2)
                
    return image, final_farm_mask

