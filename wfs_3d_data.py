#!/usr/bin/env python
# coding: utf-8

# In[ ]:


from owslib.wfs import WebFeatureService
import geopandas as gpd
import pandas as pd
import os
import json
import urllib.request
import numpy as np
from glob import glob
from geopandas.tools import sjoin
from shapely.geometry import Polygon
import rasterio as rio
from rasterio.plot import reshape_as_raster

import warnings
warnings.filterwarnings('ignore', 'GeoSeries.notna', UserWarning)

def get_roads(shape,outf):
    #get roads 
    url = 'https://geodata.nationaalgeoregister.nl/nwbwegen/wfs?request=GetCapabilities'
    wfs = WebFeatureService(url=url, version='2.0.0')
    layer = list(wfs.contents)[0]
    
    response = wfs.getfeature(typename=layer,bbox=tuple(shape.total_bounds)).read()
    fname = outf.replace('shp','gml')
    with open(fname, 'wb') as file:
        file.write(response)
        
    gdf_road = gpd.read_file(fname)[['gml_id','geometry']]
    gdf_road['label'] = 0
    gdf_road = gdf_road.dissolve('label')
    if os.path.exists(fname):
        os.remove(fname)
        
    return gdf_road
        
def get_3d(shape,thr=0):
    #get 3d buildings
    url = 'http://3dbag.bk.tudelft.nl/data/wfs?request=getcapabilities'
    wfs = WebFeatureService(url=url, version='2.0.0')
    layer = list(wfs.contents)[0]

    response = wfs.getfeature(typename=layer,outputFormat='JSON',bbox=tuple(shape.total_bounds)).read()
    total_feats = json.loads(response)['totalFeatures']
    
    factor = 10**(len(str(total_feats))-1)
    total_feats_round = round(total_feats/factor)*factor
    total_pages = range(0,total_feats_round,1000)
    
    gdf_bags = []
    for page in total_pages:
        response = wfs.getfeature(typename=layer,startindex=page,
                                  outputFormat='JSON',
                                  bbox=tuple(shape.total_bounds)).read()
        features = json.loads(response)['features']
        gdf_bag = gpd.GeoDataFrame.from_features(features,crs='EPSG:28992')
        gdf_bags.append(gdf_bag)
    gdf_bags = pd.concat(gdf_bags,0)[['bouwjaar','roof-0.99','geometry']]
    gdf_bags = gdf_bags[gdf_bags['roof-0.99']>thr].reset_index(drop=True)
    gdf_bags.loc[:,'bouwjaar'] = gdf_bags['bouwjaar'].str.split('-').str[0].astype(int)
    gdf_bags.columns = ['year','height','geometry']
    return gdf_bags

def close_holes(poly):
    if poly.interiors:
        return Polygon(list(poly.exterior.coords))
    else:
        return poly
    
def poly_within(gdf_a,gdf_b):
    match = sjoin(gdf_a, gdf_b, op='within', how='inner').drop('index_right',1)
    return match.reset_index(drop=True)

def year_to_decade(year_pd_series):
    cent = divmod(year_pd_series,100)[0]
    decade = (((year_pd_series-(cent*100))//10)*10).astype(str)
    decade[decade=='0'] = '00'
    return cent.astype(str)+decade.astype(str)+'s'

