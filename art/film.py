"""Cut an 18-second product demo from the original product renders."""
from pathlib import Path
from math import sin, cos, pi, exp
from functools import lru_cache
import subprocess
import tempfile
import wave
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parents[1]
MEDIA=ROOT/'dist/media'
WIDTH,HEIGHT,FPS=1280,720,24
DURATION=18
sans=str(ROOT/'art/jakarta-500.ttf')
display=str(ROOT/'art/jakarta-700.ttf')
mono=str(ROOT/'art/jakarta-500.ttf')
@lru_cache(None)
def font(path,size):
    return ImageFont.truetype(path,size)
@lru_cache(55)
def product(name):
    return Image.open(MEDIA/(name+'.webp')).convert('RGBA')
def text(draw,pos,words,size,color,family=sans):
    draw.text(pos,words,font=font(family,size),fill=color,anchor='lt',stroke_width=0)
chapters=[
    (0,5.5, ('#060f26','#185b97'), '#f4f8ff','#69d5ff','08:42 PM   /   INCOMING CALL','After hours.','Still here.',['“My AC stopped cooling.','Can I get a visit tomorrow?”'],'headset'),
    (5.5,11, ('#e1f2ff','#8db9df'), '#102c4c','#2569a8','08:43 PM   /   QUALIFY','The right','questions.',['“What’s your ZIP code, and does','tomorrow morning work?”'],'messenger'),
    (11,15.5, ('#3695dd','#8ddfff'), '#092648','#124976','08:44 PM   /   TEAM HANDOFF','A job for','dispatch.',['AC repair · Service area verified','Visit requested · Tomorrow, 10 AM'],'ticket'),
    (15.5,18, ('#06152d','#124e83'), '#f4f8ff','#69d5ff','CHATVERSIO AI','Every enquiry,','a next step.',['Chat Agent · Sales Agent · Voice Agent','Connected to your team’s tools.'],'patch')
]
# Soft room tone and physical desk sounds accompany the two spoken lines.
def sound(path):
    from scipy.signal import butter, sosfilt
    rate=44100
    rng=np.random.default_rng(104)
    length=DURATION*rate
    def texture(seconds,low,high):
        raw=rng.normal(0,1,round(seconds*rate))
        filters=butter(2,[low,high],btype='bandpass',fs=rate,output='sos')
        filtered=sosfilt(filters,raw)
        return filtered/(np.std(filtered)+1e-9)
    def place(start,source):
        offset=round(start*rate)
        count=min(len(source),len(room)-offset)
        if count>0:
            room[offset:offset+count]+=source[:count]
    room=texture(DURATION,75,350)*.0034
    def desk_tap(start,strength):
        t=np.arange(round(.19*rate))/rate
        touch=(1-np.exp(-t/.006))*np.exp(-t/.029)
        low=np.sin(2*pi*154*t)*np.exp(-t/.04)+.27*np.sin(2*pi*338*t)*np.exp(-t/.018)
        place(start,strength*touch*(.46*texture(.19,130,1150)+low))
    def paper(start,duration,gain):
        t=np.linspace(0,1,round(duration*rate))
        envelope=np.sin(pi*t)**2*(.6+.4*np.cos(2*pi*(t*2.2+t*t)))
        place(start,gain*texture(duration,240,1850)*envelope)
    paper(.14,.5,.017)
    desk_tap(.43,.13)
    for when,gain in [(9.93,.075),(10.1,.052),(10.43,.065),(12.58,.065),(12.8,.052)]:
        desk_tap(when,gain)
    paper(11.19,.72,.023)
    paper(15.5,.78,.015)
    desk_tap(16.22,.073)
    decoded=subprocess.check_output(['ffmpeg','-v','error','-i',str(ROOT/'art/film-dialogue.mp3'),
                                     '-ar',str(rate),'-ac','1','-f','f32le','-'])
    speech=np.frombuffer(decoded,dtype='<f4')
    place(0,speech)
    fade=np.linspace(0,1,round(rate*.4))
    room[:len(fade)]*=fade
    room[-len(fade):]*=fade[::-1]
    with wave.open(str(path),'wb') as f:
        f.setparams((1,2,rate,0,'NONE','not compressed'))
        f.writeframes((room.clip(-.91,.91)*32767).astype('<i2').tobytes())

def rgb(hexcolor):return tuple(bytes.fromhex(hexcolor[1:]))
def background(c1,c2):
    y,x=np.mgrid[0:HEIGHT,0:WIDTH]
    v=np.exp(-((x-955)/520)**2-((y-324)/380)**2)[:,:,None]
    noise=np.random.default_rng(74).uniform(-1.8,1.8,(HEIGHT,WIDTH,1))
    a,b=np.array(rgb(c1)),np.array(rgb(c2))
    return Image.fromarray(np.uint8(np.clip(a+(b-a)*v+noise,0,255)))
with tempfile.TemporaryDirectory() as tmp:
    wav=Path(tmp)/'sound.wav';sound(wav)
    cmd=['ffmpeg','-y','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{WIDTH}x{HEIGHT}','-r',str(FPS),'-i','-','-i',str(wav),'-c:v','libx264','-threads','3','-crf','22','-preset','veryfast','-pix_fmt','yuv420p','-c:a','aac','-b:a','80k','-movflags','+faststart','-shortest',str(MEDIA/'after-hours.mp4')]
    proc=subprocess.Popen(cmd,stdin=subprocess.PIPE)
    stages=[background(*s[2]) for s in chapters]
    logo=product('chatversio-logo').resize((182,38),Image.Resampling.LANCZOS)
    light_logo=Image.new('RGBA',logo.size,'#f4f8ff');light_logo.putalpha(logo.getchannel('A'))
    for frame in range(DURATION*FPS):
        time=frame/FPS
        j=next(i for i,c in enumerate(chapters) if c[0]<=time<c[1])
        start,end,_,fg,accent,label,line1,line2,sub,obj=chapters[j]
        t=(time-start)/(end-start);ease=1-exp(-11*t)
        im=stages[j].copy()
        art=product(obj)
        if j==0:
            position=2+10*(.5-.5*cos(t*pi));lo=int(position)
            art=Image.blend(product(f'spin/spin-{lo:02d}'),product(f'spin/spin-{lo+1:02d}'),position-lo)
        size=int(688+38*t)
        art=art.resize((size,size),Image.Resampling.BILINEAR)
        x=int(918-size/2+(1-ease)*90);y=int(352-size/2+12*sin(t*pi))
        if j==3:
            for key,xpos,ypos,span in [('sales',816,152,300),('chat',687,187,265),('voice',985,189,264)]:
                person=product('agent-'+key).resize((span,span),Image.Resampling.LANCZOS)
                im.paste(person,(xpos+int(28*(1-ease)),ypos),person)
        else:
            im.paste(art,(x,y),art)
        d=ImageDraw.Draw(im)
        stamp=light_logo if j in (0,3) else logo
        im.paste(stamp,(62,27),stamp)
        text(d,(1050,44),'SAMPLE WORKFLOW',14,fg,mono)
        d.line((62,85,1218,85),fill=accent,width=1)
        off=int(20*(1-ease))
        text(d,(61,184+off),label,18,fg,mono)
        text(d,(55,239+off),line1,73,fg)
        text(d,(57,330+off),line2,91,accent,display)
        for k,s in enumerate(sub):text(d,(64,485+k*33+off),s,21,fg)
        d.line((62,647,1218,647),fill=accent,width=1)
        d.line((62,647,62+int(1156*time/DURATION),647),fill=fg,width=4)
        text(d,(62,666),'AFTER HOURS   /   A SERVICE BUSINESS ENQUIRY',13,fg,mono)
        text(d,(1145,666),f'00:{int(time):02d}',14,fg,mono)
        if frame==44:im.resize((900,506),Image.Resampling.LANCZOS).save(MEDIA/'film-poster.webp',quality=88)
        proc.stdin.write(im.tobytes())
    proc.stdin.close()
    if proc.wait():raise SystemExit('Film encoding failed')
