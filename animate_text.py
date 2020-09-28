import bpy
#update text in each frame according to year
years = [obj.name for obj in bpy.data.collections.get('shapes').all_objects]

nr_frames = 330
step = 2
frame_range = range(0,nr_frames,step)
frame_year = dict(zip(frame_range,years))

def update(self):
    text = bpy.data.objects['Text']
    frame = bpy.context.scene.frame_current
    if frame % 2 ==0:
        text.data.body = frame_year[frame]
    else:
        text.data.body = frame_year[frame]

bpy.app.handlers.frame_change_post.append(update)