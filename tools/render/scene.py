import numpy as np
from stl import load
import os
D=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','..','hardware','stl','')

def box(c,s):
    c=np.array(c,float); h=np.array(s,float)/2
    v=np.array([[x,y,z] for x in(-1,1) for y in(-1,1) for z in(-1,1)])*h+c
    f=[(0,1,3),(0,3,2),(4,6,7),(4,7,5),(0,4,5),(0,5,1),(2,3,7),(2,7,6),(0,2,6),(0,6,4),(1,5,7),(1,7,3)]
    return v[np.array(f)]
def cyl(c,r,h,axis=2,n=40):
    a=np.linspace(0,2*np.pi,n,endpoint=False); b=np.roll(a,-1)
    def P(t,z):
        p=np.zeros((len(t),3)); q=[i for i in range(3) if i!=axis]
        p[:,q[0]]=r*np.cos(t); p[:,q[1]]=r*np.sin(t); p[:,axis]=z; return p+np.array(c,float)
    z0,z1=-h/2,h/2; C0=np.array(c,float); C1=C0.copy(); C0[axis]+=z0; C1[axis]+=z1
    A0,B0,A1,B1=P(a,z0),P(b,z0),P(a,z1),P(b,z1)
    t=[np.stack([A0,B0,B1],1),np.stack([A0,B1,A1],1),
       np.stack([np.repeat(C1[None],n,0),A1,B1],1),np.stack([np.repeat(C0[None],n,0),B0,A0],1)]
    return np.concatenate(t)
def cat(*a): return np.concatenate(a)

COL=dict(shell=(.92,.90,.85),ink=(.13,.13,.14),olive=(.42,.47,.22),cap=(.86,.84,.79),plate=(.17,.17,.18),
         pcb_y=(.96,.62,.12),pcb_p=(.45,.22,.62),pcb_b=(.12,.12,.13),metal=(.75,.76,.78),glass=(.09,.10,.11),
         lcd=(.55,.67,.06),bat=(.10,.10,.11),bat_r=(.80,.12,.12),spk=(.55,.56,.58),sw=(.15,.15,.15),brass=(.72,.45,.22),white=(.95,.95,.93))

def parts():
    P={}
    P['shell']=(load(D+'Shell.stl'),COL['shell'])
    m=load(D+'Shell-Color.stl').copy(); m[...,2]+=0.04
    P['mask']=(m,COL['ink'])
    b=load(D+'button.stl')+np.array([0,0,1.8]); b2=b.copy(); b2[...,0]+=60  # resting height: crosses stand proud of the face
    P['btn_l']=(b,COL['olive']); P['btn_r']=(b2,COL['olive'])
    p=load(D+'d-pad.stl').copy(); p[...,2]-=15
    P['plate']=(p,COL['plate'])
    P['cap']=(load(D+'cap.stl'),COL['cap'])
    # CYD ESP32-2432S028R
    P['cyd_pcb']=(box((-0.5,-0.5,-4.8),(86,50,1.6)),COL['pcb_y'])
    P['cyd_lcd']=(cat(box((-4.4,-0.4,-2.2),(70,50,3.6)),box((-4.4,-0.4,-0.38),(60.5,45.5,0.05))),COL['metal'])
    P['cyd_scr']=(box((-4.4,-0.4,-0.33),(58,43.5,0.05)),COL['lcd'])
    P['cyd_esp']=(cat(box((-30,4,-6.4),(18,25.5,0.8)),box((-30,6.5,-7.6),(16,17,1.6))),COL['metal'])
    P['cyd_usb']=(cat(box((39.5,-2.5,-7.2),(8,9,3.2)),box((-3,-16,-6.5),(14,15,1.8))),COL['metal'])
    # speaker 23mm
    P['spk']=(cat(cyl((-4.5,-44,-2.5),11.5,3),cyl((-4.5,-44,-4.5),6,1.2)),COL['spk'])
    # tact switches 6x6x7
    ts=[]
    for cx in (-34.5,25.5):
        for dx,dy in ((0,-7),(0,7),(-7,0),(7,0)):
            ts+= [box((cx+dx,-44+dy,-12.25),(6,6,3.5)),cyl((cx+dx,-44+dy,-8.75),1.75,3.5,n=20)]
    P['tact']=(cat(*ts),COL['sw'])
    # PCF8574 module in plate recess
    P['pcf']=(cat(box((-4.5,-44,-13.2),(20,22,1.6)),box((-4.5,-44,-11.7),(7.5,10,1.4))),COL['pcb_p'])
    # 13450 battery
    P['bat']=(cyl((-25,-70.5,-8.6),6.5,45,axis=0),COL['bat'])
    # boost module
    P['boost']=(cat(box((21,-70,-0.6),(18,22,1.2)),box((21,-77.5,-2.8),(9,7.4,3.2)),box((17,-66,-2.7),(6.6,6.6,3))),COL['pcb_b'])
    # SS12F15 slide switch, panel-mounted on the top bracket
    sw=cat(box((-4.4,27.7,-13),(20,0.6,4.6)),box((-4.4,25.2,-13),(8.6,4.4,4.4)),box((-4.4,30,-13),(2,4.6,2.2)))
    P['slide']=(sw,COL['sw'])
    return P
GROUPS=dict(
    shell=['shell','mask'], buttons=['btn_l','btn_r'], plate=['plate'], tact=['tact'], pcf=['pcf'],
    spk=['spk'], cyd=['cyd_pcb','cyd_lcd','cyd_scr','cyd_esp','cyd_usb'], bat=['bat'], boost=['boost'],
    slide=['slide'], cap=['cap'])
