import cv2
import numpy as np
import os
import shutil

rgb_image_directory_path = "trainA"
nir_image_directory_path = "trainB"
ndvi_directory_path = "rgb_nir_aerial_imagery/train_B"
new_rgb_directory_path = "rgb_nir_aerial_imagery/train_A"
stride = 128
size = 256
val_split_percentage = 0.10


def create_patches(bgr_image, ndvi_image, image_name):
    """pass rgb and ndvi image and save as patches based on stride and size"""
    count = 0
    for i in range(0, bgr_image.shape[0], stride):
        for j in range(0, bgr_image.shape[1], stride):
            try:
                cropped_rgb_region = bgr_image[i:i+size, j:j+size, :]
                cropped_nir = ndvi_image[i:i+size, j:j+size]
                if cropped_rgb_region.shape[0] >= size and cropped_rgb_region.shape[1] >= size:
                    cv2.imwrite(f"{new_rgb_directory_path}/{count}_{image_name}", cropped_rgb_region)
                    cv2.imwrite(f"{ndvi_directory_path}/{count}_{image_name}", cropped_nir)
                count += 1
            except Exception:
                pass


def create_nir_image_save_patches(image_name):
    """save ndvi image to specifi folder"""
    os.makedirs(ndvi_directory_path, exist_ok=True)
    os.makedirs(new_rgb_directory_path, exist_ok=True)
    # read rgb image using opencv
    bgr_image = cv2.imread(os.path.join(rgb_image_directory_path, image_name))
    nir_image = cv2.imread(os.path.join(rgb_image_directory_path, image_name), 0)
    create_patches(bgr_image=bgr_image, ndvi_image=nir_image, image_name=image_name)


def split_train_val():
    """take 20 images from train and move to validation dataset"""
    image_paths = os.listdir(ndvi_directory_path)
    valid_images = np.random.choice(image_paths, int(len(image_paths)* val_split_percentage), replace=False)
    os.makedirs(f"{ndvi_directory_path.split('/')[0]}/val_B", exist_ok=True)
    os.makedirs(f"{ndvi_directory_path.split('/')[0]}/val_A", exist_ok=True)
    for image in valid_images:
        shutil.move(f"{ndvi_directory_path}/{image}", f"rgb_nir_aerial_imagery/val_B/{image}")
        shutil.move(f"{new_rgb_directory_path}/{image}", f"rgb_nir_aerial_imagery/val_A/{image}")


def main():
    """create ndvi image, then split the patches and save"""
    image_names = os.listdir(rgb_image_directory_path)
    for image_name in image_names:
        if image_name.endswith(".png"):
            create_nir_image_save_patches(image_name=image_name)
            # break
    split_train_val()

if __name__ == '__main__':
    main()
    
