"""Render the Blender speech frame for the progressive hero artwork."""
from pathlib import Path
from math import radians
from mathutils import Vector
import bpy

ROOT = Path(__file__).resolve().parents[1]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(ROOT/'dist/media/3d/speech-frame.glb'))
frame = next(obj for obj in bpy.context.scene.objects if obj.type == 'MESH')
frame.rotation_euler = (radians(2), radians(-8), radians(-15))
scene = bpy.context.scene
scene.render.engine = 'CYCLES'
scene.cycles.samples = 32
scene.cycles.use_denoising = False
scene.render.film_transparent = True
scene.render.resolution_x = scene.render.resolution_y = 1000
scene.render.resolution_percentage = 100
scene.render.image_settings.color_mode = 'RGBA'
scene.world = bpy.data.worlds.new('Navy studio')
scene.world.use_nodes = True
scene.world.node_tree.nodes['Background'].inputs[0].default_value = (.18,.29,.48,1)
scene.world.node_tree.nodes['Background'].inputs[1].default_value = .5
for name,position,color,power,size in [
    ('Key',(-3,-4,6),(.9,.96,1),850,5),
    ('Cyan rim',(4,2,3),(.1,.6,1),1100,4),
    ('Front strip',(4,-5,.5),(.7,.85,1),600,3),
]:
    bpy.ops.object.light_add(type='AREA',location=position)
    light=bpy.context.object
    light.name=name
    light.data.energy=power
    light.data.color=color
    light.data.size=size
    light.rotation_euler=(-light.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(0,-10,.25))
camera=bpy.context.object
camera.data.type='ORTHO'
camera.data.ortho_scale=5.1
camera.rotation_euler=(Vector((0,0,0))-camera.location).to_track_quat('-Z','Y').to_euler()
scene.camera=camera
destination = ROOT/'art/generated'
destination.mkdir(exist_ok=True)
scene.render.filepath=str(destination/'speech-frame.png')
bpy.ops.render.render(write_still=True)
