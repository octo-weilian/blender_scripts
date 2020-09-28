import bpy, bmesh
import os
from glob import glob
import math
import collections
import xml.etree.ElementTree as et
import numpy as np


f = r'E:\blender_spatial\data\erasmusbrug_rotterdam\buildings.shp'
fname = f.split('\\')[-1].split('.')[0]

fcmap = r'E:\blender_spatial\data\erasmusbrug_rotterdam\style_erasmusbrug.qml'

z_scale = 100
if not bpy.data.collections.get(fname):
    
    bpy.ops.importgis.shapefile(filepath=f,
                                shpCRS='EPSG:4326',
                                separateObjects=True,
                                fieldObjName='gid')
    
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.extrude_region_move(TRANSFORM_OT_translate={"value":(0, 0, 1/z_scale)})
    bpy.ops.object.mode_set(mode='OBJECT')
    
    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='MEDIAN')

    
years = [obj.values()[1] for obj in bpy.data.collections.get(fname).all_objects]
years = np.unique(np.array(years)).astype(int).astype(str)

#get colorramp and sort colors based on symbols names
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

start_frame = 0
step = 2

for y in years:
    
    bpy.ops.object.select_all(action='DESELECT')
    
    #unique material for each year
    mat = bpy.data.materials.new('mat')
    mat.diffuse_color = colors[y]
    
    for obj in bpy.data.collections.get(fname).all_objects:
        if y == str(int(obj.values()[1])):
            
            #assign material
            bpy.data.objects[obj.name].active_material = mat
            
            #keyframing
            obj.keyframe_insert(data_path="scale",frame=start_frame)
            obj.scale[2] = obj.values()[2]*z_scale
            obj.keyframe_insert(data_path="scale", frame=start_frame+step)
            
            #merging
            obj.select_set(True)
            bpy.context.view_layer.objects.active = obj
            
    bpy.ops.object.join()      
    start_frame += step
    
bpy.context.scene.frame_start = 0
bpy.context.scene.frame_end = start_frame
print('Total frames: ',start_frame)

    


