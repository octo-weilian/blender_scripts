import bpy, bmesh
from mathutils  import Vector
import os
from glob import glob
import math
import collections
import xml.etree.ElementTree as et
import numpy as np
import re


#shape = bpy.data.objects['buildings']
#shape.select_set(True)
#bpy.ops.object.mode_set( mode   = 'EDIT'   )

#me = shape.data

#bm = bmesh.from_edit_mesh(me)
#bm.faces.ensure_lookup_table()

##bm.faces[8].select = True  
##bpy.ops.mesh.select_similar(type='NORMAL', threshold=0.01)
##bmesh.update_edit_mesh(me, True)
#bpy.ops.object.mode_set( mode   = 'OBJECT'   )



f = r'E:\blender_spatial\projects\erasmusbrug_rotterdam\buildings.shp'
fname = f.split('\\')[-1].split('.')[0]
#bpy.ops.importgis.shapefile(filepath=f,shpCRS='EPSG:28992',separateObjects=False,
#                            fieldExtrudeName='roof-0.99')
bpy.ops.importgis.shapefile(filepath=f,shpCRS='EPSG:28992',separateObjects=False) 
                                                    
bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='MEDIAN')

shape = bpy.data.objects['buildings']
shape.select_set(True)
me = shape.data
bpy.ops.object.mode_set( mode   = 'EDIT'   )
bm = bmesh.from_edit_mesh(me)
bm.faces.ensure_lookup_table()

vectors_arr = np.array([bm.faces[i].calc_center_median() for i in range(len(bm.faces))])

data_pair = {}
f = os.path.join(os.getcwd(),'buildings.dbf')
with open(f,'rb') as src:
    data = src.read().decode('iso-8859-1')
    data = re.sub(r"[^.a-zA-Z0-9]+", ' ', data).split()[9:]
    arr = np.array(data).reshape(-1,3)[:,1:]
    years = np.unique(arr[:,0])

    for year in years:
        ix = np.where(arr[:,0]==year)[0]
        height = arr[ix,1]
        vectors = vectors_arr[ix]
        values = np.array([ix,height]).astype(float)
        data_pair[year] = values

#for year,values in data_pair.items():
#    if year == '2018':
#        ix, height = values  
#        for i in range(len(ix)):
#            bm.faces[int(ix[i])].select = True
#            bpy.ops.transform.translate(value=(0,0,height[i]-0.01))
#            bpy.ops.mesh.select_all(action='DESELECT')
#            print(len(bm.faces))
#bmesh.update_edit_mesh(me)
            
#bpy.ops.object.mode_set( mode   = 'OBJECT'   )        



