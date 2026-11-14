"""Original studio props for the Chatversio website. Run with Blender in background mode."""
from pathlib import Path
from math import pi, sin, cos, radians, sqrt
import argparse
import sys
import tempfile
import bpy
from mathutils import Vector
import math

parser = argparse.ArgumentParser()
parser.add_argument('--shots', default=str(Path(tempfile.gettempdir())/'chatversio-shots'))
parser.add_argument('--spin', action='store_true')
parser.add_argument('--ambient', action='store_true')
parser.add_argument('--only', default='all')
args = parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
output = Path(args.shots)
output.mkdir(exist_ok=True, parents=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.render.engine = 'CYCLES'
scene.cycles.samples = 26
scene.cycles.use_denoising = False
scene.cycles.max_bounces = 5
scene.cycles.transparent_max_bounces = 4
scene.render.film_transparent = True
scene.render.image_settings.color_mode = 'RGBA'
scene.render.image_settings.compression = 30
scene.view_settings.view_transform = 'AgX'
scene.view_settings.look = 'AgX - Medium High Contrast'
scene.view_settings.exposure = -0.12
scene.world = bpy.data.worlds.new('Midnight cyclorama')
scene.world.use_nodes = True
scene.world.node_tree.nodes['Background'].inputs[0].default_value = (.14,.22,.38,1)
scene.world.node_tree.nodes['Background'].inputs[1].default_value = .44

def material(name, rgb, metal=0, rough=.30, coat=0, grain=0, glow=0):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*rgb,1)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    bs = nodes['Principled BSDF']
    for k,v in [('Base Color',(*rgb,1)),('Metallic',metal),('Roughness',rough),('Coat Weight',coat)]:
        bs.inputs[k].default_value=v
    if glow:
        bs.inputs['Emission Color'].default_value=(*rgb,1)
        bs.inputs['Emission Strength'].default_value=glow
    if grain:
        noise=nodes.new('ShaderNodeTexNoise')
        noise.inputs['Scale'].default_value=170
        bump=nodes.new('ShaderNodeBump')
        bump.inputs['Strength'].default_value=grain
        bump.inputs['Distance'].default_value=.014
        mat.node_tree.links.new(noise.outputs['Fac'],bump.inputs['Height'])
        mat.node_tree.links.new(bump.outputs['Normal'],bs.inputs['Normal'])
    return mat

silver=material('Brushed titanium',(.67,.68,.72),.93,.22,.22,.045)
chrome=material('Mirror edge',(.87,.89,.96),.99,.13,.28)
black=material('Midnight navy',(.006,.014,.038),.54,.26,.22)
leather=material('Pleated navy leather',(.009,.018,.042),.12,.46,.15,.32)
blue=material('Chatversio blue lacquer',(.015,.115,.80),.35,.23,.42)
cyan=material('Cyan enamel',(.025,.47,.84),.43,.24,.48)
ivory=material('Ceramic white',(.86,.93,1),.15,.32,.24)
glass=material('Smoked display glass',(.014,.011,.041),.44,.18,.42)
shadow=material('Acoustic apertures',(.004,.003,.008),.1,.52)
ink=material('Printed graphite',(.013,.011,.018),.04,.62)
paper=material('Thermal receipt paper',(.93,.97,1),.03,.69)
blue_led=material('Blue phosphor',(.025,.40,1),.09,.22,.14,1.7)
cyan_led=material('Cyan phosphor',(.10,.68,1),.08,.26,.16,1.4)

bpy.ops.object.empty_add(type='PLAIN_AXES')
rig=bpy.context.object
rig.name='Product turntable'
products=[]
def attach(o,m=None,parent=None):
    o.parent=rig if parent is None else parent
    if m is not None:o.data.materials.append(m)
    products.append(o)
    return o

def mesh(name,vertices,faces,m,parent=None,smooth=False):
    data=bpy.data.meshes.new(name)
    data.from_pydata(vertices,[],faces)
    data.update()
    o=bpy.data.objects.new(name,data)
    scene.collection.objects.link(o)
    if smooth:
        for p in data.polygons:p.use_smooth=True
    return attach(o,m,parent)

def edge(o,r=.045):
    if r:
        b=o.modifiers.new('Rolled edges','BEVEL');b.width=r;b.segments=5
    n=o.modifiers.new('Face weighted normals','WEIGHTED_NORMAL')
    return o

def box(name,loc,size,m,r=.055,parent=None):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc)
    o=bpy.context.object;o.name=name;o.dimensions=size
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    return edge(attach(o,m,parent),r)

def ellipsoid(name,loc,size,m,parent=None):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=48,ring_count=28,location=loc)
    o=bpy.context.object;o.name=name;o.scale=size
    for p in o.data.polygons:p.use_smooth=True
    return attach(o,m,parent)

def cylinder(name,loc,r,depth,m,axis='Z',bevel=.035,parent=None):
    bpy.ops.mesh.primitive_cylinder_add(vertices=72,radius=r,depth=depth,location=loc)
    o=bpy.context.object;o.name=name
    o.rotation_euler={'X':(0,pi/2,0),'Y':(pi/2,0,0),'Z':(0,0,0)}[axis]
    for p in o.data.polygons:p.use_smooth=len(p.vertices)==4
    return edge(attach(o,m,parent),bevel)

def curve(name,pts,r,m,parent=None,bezier=True):
    c=bpy.data.curves.new(name,'CURVE');c.dimensions='3D';c.resolution_u=24
    kind='BEZIER' if bezier else 'POLY'
    sp=c.splines.new(kind)
    if bezier:
        sp.bezier_points.add(len(pts)-1)
        for p,xyz in zip(sp.bezier_points,pts):
            p.co=xyz;p.handle_left_type=p.handle_right_type='AUTO'
    else:
        sp.points.add(len(pts)-1)
        for p,xyz in zip(sp.points,pts):p.co=(*xyz,1)
    c.bevel_depth=r;c.bevel_resolution=4;c.resolution_u=20;c.use_fill_caps=True
    o=bpy.data.objects.new(name,c);scene.collection.objects.link(o);return attach(o,m,parent)

def type_on(name,body,loc,size,m,normal=(0,-1,0),up=(0,0,1),parent=None):
    from mathutils import Matrix
    n=Vector(normal).normalized();u=Vector(up).normalized();right=u.cross(n).normalized();u=n.cross(right).normalized()
    c=bpy.data.curves.new(name,'FONT');c.body=body;c.size=size;c.align_x='CENTER';c.align_y='CENTER';c.resolution_u=5
    o=bpy.data.objects.new(name,c);scene.collection.objects.link(o);o.location=loc
    o.rotation_euler=Matrix([right,u,n]).transposed().to_euler()
    return attach(o,m,parent)

def group(name,loc=(0,0,0)):
    o=bpy.data.objects.new(name,None);scene.collection.objects.link(o);o.location=loc
    return attach(o)

def arch(name,rx,rz,z0,width,thick,m,start=-4,end=184):
    pts=[];faces=[];n=90
    for i in range(n+1):
        a=radians(start+(end-start)*i/n)
        for h,y in [(-thick/2,-width/2),(-thick/2,width/2),(thick/2,width/2),(thick/2,-width/2)]:
            pts.append(((rx+h)*cos(a),y,z0+(rz+h)*sin(a)))
    for i in range(n):
        for j in range(4):faces.append((i*4+j,i*4+(j+1)%4,(i+1)*4+(j+1)%4,(i+1)*4+j))
    faces+=[(3,2,1,0),tuple(range(n*4,n*4+4))]
    return edge(mesh(name,pts,faces,m,smooth=True),min(.072,thick*.42))

def cushion(parent,side):
    # The folds change around the seam instead of using a uniform torus.
    verts=[];faces=[];n=160;k=20
    for i in range(n):
        u=2*pi*i/n
        for j in range(k):
            v=2*pi*j/k;fold=(.009*cos(64*u)+.006*cos(47*u))*(.65+.35*cos(v))
            rad=.168+fold
            verts.append((-side*.19+side*.16*sin(v),(.47+rad*cos(v))*cos(u),(.65+rad*cos(v))*sin(u)))
    for i in range(n):
        for j in range(k):faces.append((i*k+j,((i+1)%n)*k+j,((i+1)%n)*k+(j+1)%k,i*k+(j+1)%k))
    mesh('Memory foam earpad · stitched leather',verts,faces,leather,parent,True)

def make_headset():
    arch('Headband · tempered rim',1.32,1.60,.29,.57,.12,silver)
    arch('Crown · burnished blue',1.37,1.65,.29,.44,.074,blue,9,171)
    arch('Suspension hammock',1.19,1.40,.31,.48,.16,leather,8,172)
    for y in (-.266,.266):
        pts=[(1.355*cos(radians(a)),y,.29+1.635*sin(radians(a))) for a in range(0,181,2)]
        curve('Rolled headband lip',pts,.022,chrome,bezier=False)
    for j in range(20,161,4):
        t=radians(j);y=-.22
        a=(1.187*cos(t),y,.31+1.39*sin(t))
        t+=.025;b=(1.187*cos(t),y,.31+1.39*sin(t))
        curve('Leather topstitch',[a,b],.009,ivory,bezier=False)
    carriers=[]
    for side in (-1,1):
        center=(side*1.27,0,-.60)
        cup=group('Driver assembly',center)
        cup.rotation_euler.y=radians(side*8)
        carriers.append(cup)
        # Elliptical shells with staggered bands and a machined face.
        for label,x,depth,ry,rz,mat in [
            ('Acoustic lining',-.13,.11,.55,.72,black),('Driver gasket',.010,.20,.62,.82,black),
            ('Enamel shell',.099,.27,.65,.84,blue),('Polished lip',.225,.052,.63,.813,chrome),
            ('Suspended faceplate',.248,.115,.607,.787,silver),('Centre dial',.307,.026,.43,.53,black),
            ('Faceplate medallion',.329,.045,.392,.484,silver)]:
            obj=cylinder(label,(side*x,0,0),1,depth,mat,'X',min(.034,depth*.38),cup)
            obj.scale.x=rz;obj.scale.y=ry
        cushion(cup,side)
        for i in range(42):
            a=2*pi*i/42
            v=(side*.314,.506*cos(a),.667*sin(a))
            o=ellipsoid('Annular acoustic port',v,(.009,.024,.036),shadow,cup)
            o.rotation_euler.x=a-pi/2
        for a in [pi/4,pi*3/4,5*pi/4,7*pi/4]:
            y=.566*cos(a);z=.725*sin(a)
            screw=cylinder('Torx fitting',(side*.308,y,z),.027,.01,chrome,'X',.003,cup)
            box('Screw slot',(side*.316,y,z),(.006,.034,.007),ink,.002,cup)
        # Raised, staggered bars form the Chatversio signal emblem.
        for j,h in enumerate([.12,.24,.35,.24,.12]):
            o=box('Signal emblem',(side*.356,(j-2)*.066,.037),(.027,.039,h),blue,.012,cup)
            o.rotation_euler.x=-.17
        type_on('Engraving','CHATVERSIO',(side*.355,0,-.25),.060,ink,(side,0,0),parent=cup)
        for y in [-.275,.275]:
            curve('Yoke / polished steel',[(side*1.32,y,.47),(side*1.46,y,.17),(side*1.55,y*1.45,-.14),(side*1.53,y*1.58,-.56)],.049,chrome)
            cylinder('Oxide pivot',(side*1.54,y*1.58,-.56),.096,.087,black,'X',.02)
            cylinder('Pivot cap',(side*1.594,y*1.58,-.56),.058,.026,silver,'X',.013)
        box('Telescoping hinge',(side*1.325,0,.32),(.21,.63,.37),black,.066)
        box('Hinge accent',(side*1.44,-.02,.29),(.035,.38,.08),blue,.025)
        type_on('Size label','R' if side>0 else 'L',(side*1.442,-.01,.4),.084,ivory,(side,0,0))
    curve('Boom arm',[(1.52,-.32,-.98),(1.55,-.76,-1.04),(1.20,-1.25,-1.09),(.65,-1.58,-.99),(.26,-1.64,-.81)],.045,chrome)
    mic=ellipsoid('Capsule microphone',(.24,-1.64,-.80),(.31,.134,.13),black)
    mic.rotation_euler.y=-.24
    ellipsoid('Microphone lamp',(.31,-1.765,-.81),(.062,.012,.019),blue_led)
    for j in range(5):
        box('Mic grille',(.09+j*.038,-1.756,-.81),(.012,.014,.064),shadow,.004)
    return carriers

def make_pager():
    # Palm-sized translucent-era messaging terminal.
    holder=group('Messenger')
    box('Lower case',(0,.015,-.06),(2.92,.77,1.68),black,.25,holder)
    box('Enamel case',(0,-.09,.045),(2.98,.65,1.66),cyan,.23,holder)
    box('Panel seal',(-.03,-.406,.08),(2.61,.15,1.23),silver,.12,holder)
    box('Dark display',(-.03,-.494,.09),(2.49,.079,1.116),glass,.10,holder)
    type_on('Agent display','HELLO_',(-.04,-.541,.19),.42,cyan_led,parent=holder)
    type_on('Display label','MESSAGE RECEIVED',(-.15,-.542,-.18),.115,ivory,parent=holder)
    for j in range(5):
        box('Level meter',(.75+.06*j,-.544,-.24+.018*j),(.032,.011,.06+.035*j),blue_led,.009,holder)
    cylinder('Function knob',(1.53,.02,-.25),.19,.24,silver,'X',.03,holder)
    for j in range(7):
        cylinder('Dial knurl',(1.445+j*.026,.02,-.25),.193,.009,black,'X',.002,holder)
    box('Send key',(.69,-.12,.90),(.54,.30,.14),blue,.066,holder)
    box('Side key',(-1.54,-.045,.04),(.17,.29,.47),chrome,.055,holder)
    type_on('Bezel mark','CHATVERSIO   /   MSG',(-.48,-.406,-.645),.084,ink,parent=holder)
    for i in range(4):box('Bottom vent',(.74+i*.08,-.408,-.63),(.038,.022,.12),black,.016,holder)
    # Coiled antenna loop with a metal ferrule.
    curve('Lanyard',[(-1.32,0,.63),(-1.85,.06,1.02),(-1.96,.18,.74),(-1.49,.22,.47)],.058,blue,holder)

def make_printer():
    box('Feet',(0,.06,-.55),(2.36,1.38,.22),black,.1)
    box('Thermal printer',(0,0,-.06),(2.62,1.55,.98),blue,.18)
    box('Printer deck',(0,0,.435),(2.5,1.46,.15),black,.12)
    box('Rear paper cowl',(0,.45,.48),(2.39,.47,.29),silver,.095)
    box('Front panel',(0,-.765,-.043),(2.12,.06,.52),blue,.06)
    type_on('Receipt printer imprint','CHATVERSIO',(-.34,-.80,.002),.146,ink)
    type_on('Receipt printer mark','WORKFLOW  /  03',(-.45,-.8,-.152),.067,ink)
    cylinder('Panel LED',(.80,-.796,-.034),.058,.029,blue_led,'Y',.014)
    # Gentle curl bending backward as it leaves the slot.
    verts=[];faces=[]
    for i in range(51):
        t=i/50;y=.10+.37*t*t-.16*sin(t*pi);z=.52+1.70*t
        for j in range(25):
            x=(j/24-.5)*1.49
            verts.append((x,y+.05*(j/24-.5)**2,z-(.041*(j%2) if i==50 else 0)))
    for i in range(50):
        for j in range(24):
            k=i*25+j;faces.append((k,k+25,k+26,k+1))
    strip=mesh('Thermal paper ticket',verts,faces,paper,smooth=True)
    so=strip.modifiers.new('Paper thickness','SOLIDIFY');so.thickness=.011
    def printline(message,t,size):
        y=.10+.37*t*t-.16*sin(t*pi);z=.52+1.7*t
        slope=(.74*t-.16*pi*cos(pi*t))/1.7
        type_on(message,message,(0,y-.018,z),size,ink,(0,-1,slope),(0,slope,1))
    printline('APPOINTMENT',.86,.108);printline('Booked.',.71,.30)
    printline('TUE   /   10:00 AM',.49,.108);printline('CONFIRMED',.36,.08)
    for j in range(35):
        x=(j-17)*.030;t=.21;z=.52+1.7*t;y=.10+.37*t*t-.16*sin(t*pi)
        box('Printed barcode',(x,y-.022,z),(.009+(j%3)*.006,.006,.107),ink,.001)
    for j in range(5):box('Status vent',(1.185,-.49+j*.12,.497),(.072,.05,.019),silver,.007)

def make_plugs():
    # Two patch leads with real strain relief, contacts and insulating rings.
    for idx,(loc,rotation,accent,lead) in enumerate([((-.62,-.18,.19),(-.32,-.77,-.15),blue,cyan),((.88,.34,-.31),(.19,.58,.20),cyan,blue)]):
        p=group('Patch lead',loc);p.rotation_euler=rotation
        for name,r,d,z,m in [('Barrel',.242,.64,0,silver),('Insulator',.25,.075,.30,accent),('Nose',.137,.25,.49,chrome),('Jack',.10,.49,.78,chrome),('Tip',.095,.16,1.09,chrome)]:
            cylinder(name,(0,0,z),r,d,m,'Z',.024,p)
        for i in range(14):cylinder('Barrel grip',(0,0,-.18+i*.027),.248,.009,black,'Z',.003,p)
        for z in [.7,.87,1.005]:cylinder('Signal insulator',(0,0,z),.102,.036,shadow,'Z',.005,p)
        for j in range(7):cylinder('Strain relief',(0,0,-.36-.045*j),.19-j*.012,.037,accent,'Z',.011,p)
        sign=(-1 if idx==0 else 1)
        curve('Flexible cable',[(0,0,-.62),(.1*sign,0,-.93),(.68*sign,.03,-1.44),(1.22*sign,.24,-1.30),(1.48*sign,.5,-.57),(1.16*sign,.83,-.1)],.097,lead,p)
    return

def aim(o,pt):
    o.rotation_euler=(Vector(pt)-o.location).to_track_quat('-Z','Y').to_euler()
def softbox(name,loc,color,energy,w,h):
    bpy.ops.object.light_add(type='AREA',location=loc)
    o=bpy.context.object;o.name=name;o.data.shape='RECTANGLE';o.data.size=w;o.data.size_y=h;o.data.color=color;o.data.energy=energy;aim(o,(0,0,.1))
softbox('Overhead silk',(-3,-3,6),(.90,.96,1),730,5,3)
softbox('White vertical strip',(4.5,-4,.9),(.93,.97,1),570,1.4,5)
softbox('Cyan rim',(-2,2.4,2.5),(.10,.62,1),880,3,4)
softbox('Blue reflection',(3,4,1.8),(.34,.38,1),680,1.2,3.6)
softbox('Blue bounce',(0,-3,-3.7),(.04,.30,1),200,4,1.0)
bpy.ops.object.camera_add(location=(5.2,-8.7,3.3))
cam=bpy.context.object;cam.name='Studio camera';scene.camera=cam;cam.data.type='ORTHO'
def setup(loc,target,scale,rotation):
    cam.location=loc;aim(cam,target);cam.data.ortho_scale=scale;rig.rotation_euler=tuple(radians(a) for a in rotation)
def render(name,size=1050,samples=25):
    scene.render.resolution_x=scene.render.resolution_y=size;scene.render.resolution_percentage=100;scene.cycles.samples=samples
    scene.render.filepath=str(output/(name+'.png'));bpy.ops.render.render(write_still=True)
def clear():
    for o in reversed(products):
        bpy.data.objects.remove(o,do_unlink=True)
    products.clear()
    rig.rotation_euler=(0,0,0)

if args.only in ('all','headset'):
    cups=make_headset()
    setup((5.3,-8.3,3.0),(0,0,.14),4.28,(8,-16,-5))
    if args.ambient:
        baseline=rig.rotation_euler.copy()
        (output/'ambient').mkdir(exist_ok=True)
        for i in range(96):
            t=i*2*pi/96
            rig.rotation_euler.x=baseline.x+radians(3.7)*sin(t)
            rig.rotation_euler.y=baseline.y+radians(3.2)*(1-cos(t))
            rig.rotation_euler.z=baseline.z+radians(11)*sin(t)
            rig.location.z=.045*sin(t)
            render(f'ambient/frame-{i:03d}',810,11)
    elif args.spin:
        # Exclude 360 degrees so the last frame joins the first seamlessly.
        baseline=rig.rotation_euler.z
        for i in range(40):
            rig.rotation_euler.z=baseline+2*pi*i/40
            if not (output/f'spin-{i:02d}.png').exists():render(f'spin-{i:02d}',690,10)
    else:
        render('headset',1230,36)
        setup((6.9,-6.3,2.6),(.57,-.1,-.14),2.95,(6,-23,6));render('driver',920)
        for side,cup in zip((-1,1),cups):cup.location.x+=side*.69
        setup((5.8,-8.0,3.0),(0,0,.18),5.5,(11,-12,14));render('assembly',1000)
    clear()
if args.only in ('all','pager'):
    make_pager();setup((5.2,-10,3.3),(0,-.05,.09),4.25,(-7,-15,-8));render('messenger',1000,28);clear()
if args.only in ('all','ticket'):
    make_printer();setup((4.0,-8.1,3.55),(0,.07,.72),4.05,(4,-10,1));render('ticket',1000,28);clear()
if args.only in ('all','plugs'):
    make_plugs();setup((2.1,-8,2.2),(0,0,-.19),4.56,(6,-16,-11));render('patch',1000,26);clear()
