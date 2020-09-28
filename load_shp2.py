import bpy, bmesh
from mathutils  import Vector
import os
from glob import glob
import math
import collections
import xml.etree.ElementTree as et
import numpy as np
import re


#load data
if not bpy.data.collections.get('shapes'):
    
    #create collection to store shapes
    collection = bpy.data.collections.new("shapes")
    bpy.context.scene.collection.children.link(collection)
    c_ix =  [i+1 for i in range(len(bpy.data.collections)) if bpy.data.collections[i].name =='shapes'][0]
    
    #loop over shapefiles

    for f in glob(r'./shapes/*.shp'):
        fname = f.split('\\')[-1].split('.')[0]
        if fname !='buildings':
            bpy.ops.importgis.shapefile(filepath=f,shpCRS='EPSG:28992',
                                        separateObjects=False,
                                        fieldExtrudeName='roof-0.99')
                             
            #set object z location and scale to 0                            
            bpy.context.object.location.z = 0
            bpy.ops.transform.resize(value=(1, 1, 0), 
                                    orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), 
                                    orient_matrix_type='GLOBAL', constraint_axis=(False, False, True), mirror=True, 
                                    use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, 
                                    use_proportional_connected=False, use_proportional_projected=False)        #move object to collection
            bpy.ops.object.move_to_collection(collection_index=c_ix)
    
#    #add ancillary shapefiles (e.g. roads, waterways, trees, etc.)
#    for f in glob(r'./*.shp'):
#            bpy.ops.importgis.shapefile(filepath=f,shpCRS='EPSG:28992',separateObjects=False)
#            bpy.context.object.location.z = 0
        
        
#get colorramp and sort colors based on symbol names
fcmap = r'E:\blender_spatial\projects\erasmusbrug_rotterdam\style_erasmusbrug.qml'
root = et.parse(fcmap).getroot()
colors = {}
for symbol in root.find('renderer-v2/symbols'):
    #get rgba scaled to 1
    sym_rgba = tuple([int(v)/255 for v in symbol[0][1].attrib['v'].split(',')])
    sym_name = symbol.attrib['name']
    for cat in root.find('renderer-v2/categories'):
        if cat.attrib['symbol']==sym_name:
            colors[cat.attrib['value']]= sym_rgba
colors =  collections.OrderedDict(sorted(colors.items()))

#add color and keyframe to objects                     
start_frame = 0
step = 2

for obj in bpy.data.collections.get('shapes').all_objects:
    #assign princinpled BSDF material and color
    if not bpy.data.objects[obj.name].active_material:
        mat = bpy.data.materials.new(f'mat_{obj.name}')
        mat.diffuse_color = colors[obj.name]
        bpy.data.objects[obj.name].active_material = mat

    #add keyframe
    obj.keyframe_insert(data_path="scale",frame=start_frame)
    obj.scale.z = 1
    obj.keyframe_insert(data_path="scale", frame=start_frame+step)
    start_frame += step
    
#set start and frame of scene
bpy.context.scene.frame_start = 0
bpy.context.scene.frame_end = start_frame
  



