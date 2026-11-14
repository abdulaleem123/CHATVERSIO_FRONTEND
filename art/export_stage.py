"""Export the original Blender props and a sculptural speech frame for the live hero."""
from pathlib import Path
import runpy
import sys
import tempfile
from math import pi, sin, cos

import bpy

ROOT = Path(__file__).resolve().parents[1]
destination = ROOT/'dist/media/3d'
destination.mkdir(parents=True, exist_ok=True)

sys.argv = ['render.py', '--', '--only', 'geometry', '--shots', str(Path(tempfile.gettempdir())/'chatversio-stage')]
kit = runpy.run_path(str(ROOT/'art/render.py'))
objects = kit['products']
rig = kit['rig']

def export(name, simplify=.45):
    bpy.ops.object.select_all(action='DESELECT')
    geometry = [obj for obj in objects if obj.type in ('MESH','CURVE','FONT')]
    for obj in geometry:
        obj.select_set(True)
    bpy.context.view_layer.objects.active=geometry[0]
    bpy.ops.object.convert(target='MESH')
    bpy.ops.object.join()
    model=bpy.context.object
    model.name=name
    bpy.context.scene.cursor.location=(0,0,0)
    bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
    if simplify < 1:
        modifier=model.modifiers.new('Web mesh reduction','DECIMATE')
        modifier.ratio=simplify
        bpy.ops.object.modifier_apply(modifier=modifier.name)
    bpy.ops.export_scene.gltf(
        filepath=str(destination/(name+'.glb')),
        export_format='GLB', use_selection=True, export_yup=True,
        export_apply=True, export_cameras=False, export_lights=False,
        export_animations=False, export_texcoords=False,
    )
    model.data.calc_loop_triangles()
    print(name, 'triangles',len(model.data.loop_triangles))
    # Joining invalidates the original object references.
    for obj in list(bpy.data.objects):
        if obj.parent==rig:
            bpy.data.objects.remove(obj,do_unlink=True)
    objects.clear()

kit['make_pager']()
export('messenger',.52)
kit['make_printer']()
export('printer',.48)
kit['make_headset']()
export('headset',.12)

# A continuous, non-circular speech silhouette with a tail and a fine inner rim.
# The square profile gives each edge an architectural, reflective face.
from mathutils import Vector

outer = kit['material']('Pearl titanium',(.13,.38,.74),.79,.19,.58)
inner = kit['material']('Inner cyan metal',(.07,.62,.86),.84,.18,.45)
curve = bpy.data.curves.new('Speech silhouette','CURVE')
curve.dimensions='3D'
curve.resolution_u=16
spline=curve.splines.new('BEZIER')
points=[
 (-1.62,.0,-.42),(-1.82,.0,.64),(-1.54,.0,1.62),(-.57,.0,2.02),
 (.63,.0,1.97),(1.47,.0,1.52),(1.69,.0,.49),(1.38,.0,-.57),
 (.58,.0,-1.18),(-.33,.0,-1.32),(-1.58,.0,-1.83),(-1.19,.0,-.91)
]
spline.bezier_points.add(len(points)-1)
for point,loc in zip(spline.bezier_points,points):
    point.co=loc
    point.handle_left_type=point.handle_right_type='AUTO'
spline.bezier_points[10].handle_left_type='VECTOR'
spline.bezier_points[10].handle_right_type='VECTOR'
spline.use_cyclic_u=True
curve.bevel_depth=.112
curve.bevel_resolution=4
obj=bpy.data.objects.new('Sculptural conversation frame',curve)
bpy.context.scene.collection.objects.link(obj)
kit['attach'](obj,outer)

# A second narrow metal line follows the inner edge and gives the rim depth.
line=curve.copy()
line.bevel_depth=.021
line.bevel_resolution=2
lip=bpy.data.objects.new('Cyan inner pinstripe',line)
bpy.context.scene.collection.objects.link(lip)
lip.scale=(.965,1,.965)
lip.location.y=-.11
kit['attach'](lip,inner)
export('speech-frame',.78)
