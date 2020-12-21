#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import geopandas as gpd
from owslib.wms import WebMapService
from PIL import Image
import urllib.request
import rasterio as rio
import numpy as np

# Download high res rgb NL
def dl_wms_highres(shape,fname,res=2000,rgb = True,padding=100):
    bounds = shape.total_bounds

    if rgb:
        url = f'https://service.pdok.nl/hwh/luchtfotorgb/wms/v1_0?&request=GetCapabilities&service=wms'
        lyr_name = 'Actueel_ortho25'
    else:
        url = f'https://service.pdok.nl/hwh/luchtfotocir/wms/v1_0?&request=GetCapabilities&service=wms'
        lyr_name = 'Actueel_ortho25IR'
    wms = WebMapService(url, version='1.3.0')
    data = wms.getmap(layers=[lyr_name], styles=['default'], srs=str(shape.crs),
                       bbox=tuple(bounds), size=(res, res), format='image/png')
    
    img = Image.open(urllib.request.urlopen(data.geturl())).convert('RGB')
    raster = reshape_as_raster(np.asarray(img))
    
    transform = rio.transform.from_bounds(bounds[0],bounds[1],bounds[2],bounds[3],
                                          raster.shape[1],raster.shape[2])

    profile = {'driver':'GTiff','dtype': 'uint8', 'nodata': None, 
           'width': raster.shape[1], 'height': raster.shape[2], 'count': raster.shape[0], 
           'crs': str(shape.crs),'transform':transform}
    with rio.open(fname,'w',**profile) as dst: 
        dst.write(raster)

