from PIL import Image
import numpy as np
import math
import glob

def NDVIimagepng(imArrayNDVI):
    
    imNDVI = Image.fromarray(imArrayNDVI)
    generalHealthImage = imNDVI.convert("RGBA")

    totalAreaOfPlot = 0

    for x in range(0, (generalHealthImage.size[0])):

        for y in range(0, (generalHealthImage.size[1])):

            if imArrayNDVI[y][x] == 0:
                generalHealthImage.putpixel((x, y), (0, 0, 0, 0))

            elif math.isnan(imArrayNDVI[y][x]):
                # totalAreaOfPlot = totalAreaOfPlot + 1 #nan values not part of cloud test
                generalHealthImage.putpixel((x, y), (230, 230, 230, 0))

            elif imArrayNDVI[y][x] < -0.1:
                generalHealthImage.putpixel((x, y), (61, 78, 157))

            elif -0.1 < imArrayNDVI[y][x] < 0.20:
                greenCode = int(25 + ((imArrayNDVI[y][x] + 0.1) * 510))
                redCode = int(51 + ((imArrayNDVI[y][x] + 0.1) * 680))
                generalHealthImage.putpixel((x, y),
                                            (redCode, greenCode, 0))

            elif 0.20 < imArrayNDVI[y][x] < 0.30:
                greenCode = int(178 +
                                ((imArrayNDVI[y][x] - 0.2) * 770))
                generalHealthImage.putpixel((x, y),
                                            (255, greenCode, 0))

            elif 0.30 < imArrayNDVI[y][x] < 0.45:
                redCode = int(255 - ((imArrayNDVI[y][x] - 0.3) * 520))
                generalHealthImage.putpixel((x, y), (redCode, 255, 0))

            elif imArrayNDVI[y][x] > 0.45:
                greenCode = int(255 -
                                ((imArrayNDVI[y][x] - 0.45) * 560))
                generalHealthImage.putpixel((x, y), (0, greenCode, 0))


    generalHealthImagePath = 'generalHealthImagePath'

    generalHealthImage.save(generalHealthImagePath + '.tif')

    for name in glob.glob(generalHealthImagePath + '.tif'):
        loadImage = Image.open(name)
        loadImage.save(generalHealthImagePath + '.png', 'PNG')

def convert_nir_to_ndvi(red_channel_image, nir_image):
    """convert nir band to ndvi ndvi = (NIR-RED)/ (NIR+RED)"""
    return (nir_image.astype(float)-red_channel_image.astype(float))/(nir_image+red_channel_image)