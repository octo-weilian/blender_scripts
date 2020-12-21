#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import os
import pandas as pd
from glob import glob
import urllib.request
import math

import numpy as np
import rasterio as rio

from rasterio.features import sieve
from rasterio.plot import reshape_as_image 
from rasterio.features import shapes
from shapely.geometry import shape
from shapely.geometry import Polygon
import geopandas as gpd
from osgeo import gdal
gdal.UseExceptions() 

def download_tile(x,y,z,token,tile_server,temp_dir):
    """
    Download xyz tile to a temporary directory 
    """
    url = tile_server.replace(
        "{x}", str(x)).replace(
        "{y}", str(y)).replace(
        "{z}", str(z)).replace(
        "{token}",str(token))
    path = f'{temp_dir}/{x}_{y}_{z}.png'
    if not os.path.exists(path):
        return urllib.request.urlretrieve(url,path)[0]
    else:
        return path
    
def deg2num(lat_deg, lon_deg, z):
    """
    Convert latlon to xy tile numbers
    https://wiki.openstreetmap.org/wiki/Slippy_map_tilenames
    """
    lat_rad = math.radians(lat_deg)
    n = 2.0 ** z
    xtile = int((lon_deg + 180.0) / 360.0 * n)
    ytile = int((1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n)
    return xtile, ytile

def num2deg(xtile, ytile, zoom):
    """
    Convert xy tile numbers to latlon
    https://wiki.openstreetmap.org/wiki/Slippy_map_tilenames
    """
    n = 2.0 ** zoom
    lon_deg = xtile / n * 360.0 - 180.0
    lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * ytile / n)))
    lat_deg = math.degrees(lat_rad)
    return lon_deg,lat_deg

def georef_tile(in_path,x, y, z, bounds):
    """
    Georeference tile to WGS84 based on boundary [ulx,uly,lrx,lry]
    """
    out_path = os.path.splitext(in_path)[0]+'.tif'
    g = gdal.Translate(out_path,in_path,outputSRS='EPSG:4326',outputBounds=bounds,rgbExpand='rgb')
    g = None
    return out_path
            
def merge_tiles(input_pattern,out_path,crs=4326,nodata=0):
    """
    Merge tiles into a single image
    """
    tile_paths = glob(input_pattern)
    g = gdal.Warp(out_path, tile_paths,dstNodata=nodata,dstSRS=f'EPSG:{crs}') 
    g = None
    return out_path

def clip_geotiff(in_path,out_path,bounds):
    """
    Clip geotif based on boundary [ulx,uly,lrx,lry]
    """
    g = gdal.Translate(out_path,in_path,projWin = bounds)
    g = None
    return out_path

def binarize_geotiff(in_path,out_path,channel,values):
    """
    Select a RGB channel and binarize the image
    """
    with rio.open(in_path) as src:
        green_channel = src.read(channel)
        profile = src.profile.copy()
        
        binary_img = np.array([np.where(green_channel==v,1,0) for v in values]).sum(0).astype(green_channel.dtype)
        binary_img_sieved = np.array([sieve(binary_img,size=100, connectivity=8)])*255     #remove isolated pixels and scale to 8 bit value range
        profile.update({'count':1,'nodata':None})
        with rio.open(out_path,'w',**profile) as dst:
            dst.write(binary_img_sieved)
            
def close_holes(poly):
    if poly.interiors:
        return Polygon(list(poly.exterior.coords))
    else:
        return poly
    
def polygonize_geotiff(in_path,close_hole=True):
    mask = None
    outh_path = os.path.splitext(in_path)[0]+'.shp'
    with rio.open(in_path) as src:
        image = src.read(1) 
        results = ({'properties': {'raster_val': v}, 'geometry': s} 
                   for i, (s, v) in enumerate(shapes(image, mask=mask, transform=src.transform)))
        geoms = list(results)
        data  = gpd.GeoDataFrame.from_features(geoms,crs=str(src.crs))
        data = data[data['raster_val']!=0]
        if close_hole:
            data.geometry = data.geometry.apply(lambda x: close_holes(x))
        data = data.dissolve('raster_val')
        data.to_file(outh_path)
    os.remove(in_path)

