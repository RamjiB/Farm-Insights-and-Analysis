import cv2
import rasterio
import numpy as np
from PIL import Image

from utils.tile_download import calldownloadfun, mergetiles
from utils.rgb_to_nir import RGB_TO_NDVI_MODEL, rgb_to_nir
from utils.farm_boundary import get_final_farm_boundary 
from utils.ndvi_utils import convert_nir_to_ndvi, NDVIimagepng

import warnings
warnings.filterwarnings("ignore")

rgb_to_nir_model_path = f"model/rgb_nir_model.pth"
latitude = 19.5127667
longitude = 75.045835
buffer=0.0009

# loading model 
rgb_nir_model = RGB_TO_NDVI_MODEL(rgb_to_nir_model_path)

# download tile image from sentinel 2 passing latitude and longitude
latmin,latmax,lonmin,lonmax= latitude-buffer, latitude+buffer,longitude-buffer,longitude+buffer
temp_dir_path, merged_tile_dir_path = calldownloadfun(18, lonmin, lonmax, latmin, latmax, f"{latitude}_{longitude}")
print("Download done")

# merge tiles 
image_path = mergetiles(temp_dir_path)
print("Meging done")

with rasterio.open(image_path) as src:
    rows, cols = rasterio.transform.rowcol(src.transform, longitude, latitude)
    src.close()
print("rowscols",rows,cols) 

#detect the farm boundary
detected_farm_boundary, mask = get_final_farm_boundary(image_path, cols, rows)
cv2.imwrite("farm_bounday.png", detected_farm_boundary)
cv2.imwrite("farm_bounday_mask.png", mask)

# get nir band
nir_band, red_channel_image, o_image_size = rgb_to_nir(image_path=image_path, model=rgb_nir_model)
print(nir_band.shape)
nir_band = cv2.resize(nir_band, (o_image_size[1], o_image_size[0]))
print(nir_band.shape)

ndvi_image = convert_nir_to_ndvi(red_channel_image, nir_band)
NDVIimagepng(ndvi_image)


