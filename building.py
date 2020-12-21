import bpy, os
from glob import glob

def load_shapes(fdir,input_pattern,crs,scale=(1,1,1)):
    
    #function to load building shapefiles 
    files = glob(fdir+input_pattern)
    dir_name =  os.path.basename(fdir)
    if not bpy.data.collections.get(dir_name):
        #create collection
        collection = bpy.data.collections.new(dir_name)
        bpy.context.scene.collection.children.link(collection)
        
        #load shapes
        for i in range(len(files)):
            bpy.ops.importgis.shapefile(filepath=os.path.abspath(files[i]),fieldExtrudeName='height',shpCRS=crs)
            bpy.ops.object.origin_set(type='ORIGIN_CURSOR', center='MEDIAN')
            bpy.context.object.pass_index = i
            bpy.context.object.scale = scale
            bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        
            bpy.ops.object.move_to_collection(collection_index=len(bpy.data.collections))
        bpy.ops.object.select_all(action='DESELECT')
    else:
        print(f'Collection "{dir_name}" already exists.')
    
def animate_shapes(col_name,scale_multiplier = 1,fps=6):
    #function to animate building objects
    if bpy.data.collections.get(col_name):
        #flatten shapes
        for obj in bpy.data.collections.get(col_name).all_objects:
            obj.scale.z = 0
        #keyframe objects (unflatten)
        start_frame = 0
        for obj in bpy.data.collections.get(col_name).all_objects:
            obj.keyframe_insert(data_path="scale",frame=start_frame)
            obj.scale.z = 1 * scale_multiplier
            obj.keyframe_insert(data_path="scale", frame=start_frame+fps)
            start_frame += fps
        #set start and frame of scene
        bpy.context.scene.frame_start = 0
        bpy.context.scene.frame_end = start_frame
        print(start_frame)
    else:
        print(f'Collection "{dir_name}" does not exist.') 

def load_geotiff(fdir,input_pattern,crs,scale=(1,1,1)):
    file = os.path.abspath(glob(fdir+input_pattern)[0])
    fname = os.path.basename(file).split('.')[0]
    if not bpy.context.scene.objects.get(fname):
        bpy.ops.importgis.georaster(filepath=file,rastCRS=crs)
        bpy.ops.object.origin_set(type='ORIGIN_CURSOR', center='MEDIAN')
        bpy.context.object.scale = scale
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    
def load_shape(fdir,input_pattern,crs,scale=(1,1,1)):
    file = os.path.abspath(glob(fdir+input_pattern)[0])
    fname = os.path.basename(file).split('.')[0]
    if not bpy.context.scene.objects.get(fname):
        bpy.ops.importgis.shapefile(filepath=file, shpCRS=crs)
        bpy.ops.object.origin_set(type='ORIGIN_CURSOR', center='MEDIAN')
        bpy.context.object.scale = scale
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

def animate_text(col_name,text_name,frame_start,frame_end,fps):

    #animate text
    col_objects = bpy.data.collections[col_name].all_objects
    frames = range(frame_start,frame_end,fps)
    texts = [y.name for y in col_objects]
    frames_texts = dict(zip(frames, texts ))

    def update(self):
        try:
            frame = bpy.context.scene.frame_current
            bpy.data.objects[text_name].data.body = frames_texts[frame]
            bpy.data.objects[text_name].pass_index = frame/fps
        except KeyError:
            pass
        
    bpy.app.handlers.frame_change_post.clear()
    bpy.app.handlers.frame_change_post.append(update)
