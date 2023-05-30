"""
Downloading Tiles from Google Maps (tile server can be changed)
"""

import urllib.request
import os
from osgeo import gdal
from math import degrees, atan, sinh
from math import log, tan, radians, cos, pi, floor
import urllib.request

tile_server = "https://mt.google.com/vt/lyrs=s&x={x}&y={y}&z={z}"

def createdir(identifier):
    """
    Create directories for storing tiles and merged image"""
    temp_dir = str(identifier)
    newdir=(temp_dir+'/mergedtile')
    print(temp_dir)
    os.makedirs(temp_dir, exist_ok=True)
    os.makedirs(newdir, exist_ok=True)
    print("directory done")

    return temp_dir, newdir


def download_tile(x, y, z, temp_dir, 
                  tile_server="https://mt.google.com/vt/lyrs=s&x={x}&y={y}&z={z}"):
    url = tile_server.replace(
        "{x}", str(x)).replace(
        "{y}", str(y)).replace(
        "{z}", str(z))
    path = f"{temp_dir}/{x}_{y}_{z}.png"
    urllib.request.urlretrieve(url, path)
    return(path)


def sec(x):
    return(1/cos(x))


def latlon_to_xyz(lat, lon, z):
    tile_count = pow(2, z)
    x = (lon + 180) / 360
    y = (1 - log(tan(radians(lat)) + sec(radians(lat))) / pi) / 2
    return(tile_count*x, tile_count*y)
    
def bbox_to_xyz(lon_min, lon_max, lat_min, lat_max, z):
    x_min, y_max = latlon_to_xyz(lat_min, lon_min, z)
    x_max, y_min = latlon_to_xyz(lat_max, lon_max, z)
    return(floor(x_min), floor(x_max),
           floor(y_min), floor(y_max))

def x_to_lon_edges(x, z):
    tile_count = pow(2, z)
    unit = 360 / tile_count
    lon1 = -180 + x * unit
    lon2 = lon1 + unit
    return(lon1, lon2)

def y_to_lat_edges(y, z):
    tile_count = pow(2, z)
    unit = 1 / tile_count
    relative_y1 = y * unit
    relative_y2 = relative_y1 + unit
    lat1 = mercatorToLat(pi * (1 - 2 * relative_y1))
    lat2 = mercatorToLat(pi * (1 - 2 * relative_y2))
    return(lat1, lat2)

def mercatorToLat(mercatorY):
    return(degrees(atan(sinh(mercatorY))))

def tile_edges(x, y, z):
    lat1, lat2 = y_to_lat_edges(y, z)
    lon1, lon2 = x_to_lon_edges(x, z)
    return[lon1, lat1, lon2, lat2]

def georeference_raster_tile(x, y, z, path):
    bounds = tile_edges(x, y, z)
    filename, extension = os.path.splitext(path)
    gdal.Translate(filename + '.tif',
                   path,
                   outputSRS='EPSG:4326',
                   outputBounds=bounds)


def calldownloadfun(zoom_level, lon_min, lon_max, lat_min, lat_max, identifier, boundary=False):
    """
    zoom_level: zoom level int
    lon_min: min longitude
    lon_max: max longitude
    lat_min, lat_max: min & max latitude
    """
    x_min, x_max, y_min, y_max = bbox_to_xyz(lon_min, lon_max, lat_min, lat_max, zoom_level)

    tempdirpath, newdirpath = createdir(identifier)

    for x in range(x_min, x_max + 1):
        for y in range(y_min, y_max + 1):
            png_path = download_tile(x, y, zoom_level, tempdirpath,
                                     tile_server="https://mt.google.com/vt/lyrs=s&x={x}&y={y}&z={z}")

            georeference_raster_tile(x, y, zoom_level, png_path)

    return tempdirpath, newdirpath


#need to read files in the tempstac folder
def mergetiles(root_dir):
    rootdir = root_dir
    ftifnames=[]

    for subdir, dirs, files in os.walk(rootdir):
        for file in files:

            filepath = subdir + os.sep + file

            if filepath.endswith(".tif"):

                ftifnames.append(filepath)

    print("mergingStarted")
    files_to_mosaic = ftifnames 
    finpath=root_dir+"/mergedtile/mergedOut.tif"
    g = gdal.Warp(root_dir+"/mergedtile/mergedOut.tif", files_to_mosaic, format="GTiff",
                options=["COMPRESS=NONE", "TILED=YES",]) 
    g = None # Close file and flush to disk
    print("merging Done")

    return finpath

#for geoJSON processing and clipping

def downloadShpfile(plotid,newdir):
    linkstart="https://fasal-public-bucket.s3.amazonaws.com/"
    shpURLs3="gis/shapefile_"+plotid
    urllib.request.urlretrieve(linkstart+shpURLs3+"/features.shp", newdir+"features.shp")
    urllib.request.urlretrieve(linkstart+shpURLs3+"/features.dbf", newdir+"features.dbf")
    urllib.request.urlretrieve(linkstart+shpURLs3+"/features.prj", newdir+"features.prj")
    urllib.request.urlretrieve(linkstart+shpURLs3+"/features.shx", newdir+"features.shx")

    print('shapefile downloaded from s3')
    return str(newdir+"features.shp")


    

    


