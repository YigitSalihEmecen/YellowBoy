from common import *
from theme import SERIF,IVORY,MUTE
P=parts()
T=dict(shell=0,buttons=-70,spk=62,cyd=135,plate=135,tact=135,pcf=135,bat=215,boost=215,slide=215,cap=290)
AX=np.array([0,0.12,-1.0]); off={k:v*AX for k,v in T.items()}
for g,d in dict(plate=(0,-14,0),tact=(0,-14,0),pcf=(0,-14,0),cyd=(0,8,0),bat=(0,-14,0),boost=(0,-14,0),slide=(0,14,0)).items(): off[g]=off[g]+np.array(d)
Q=place(P,off)
R=cam(-52,14)
body,proj,bb,sc,c=draw(Q,R,2600,1000,fill=real_fill,sw=(1.0,1.9))
items=[('buttons','Cross buttons ×2',['btn_l'],(-40,-90)),('shell','Front shell (2-colour)',['shell'],(-60,-150)),
       ('spk','Speaker 8Ω 0.5W',['spk'],(30,-110)),('cyd','CYD ESP32-2432S028R',['cyd_lcd'],(0,-120)),
       ('plate','Switch plate + 8 tact + PCF8574',['plate'],(-10,130)),('slide','SS12F15 slide switch',['slide'],(-20,-70)),
       ('bat','13450 Li-ion 650 mAh',['bat'],(30,110)),('boost','Boost / charger (Type-C)',['boost'],(40,90)),('cap','Back cap',['cap'],(40,-110))]
ov=[]; legend=[]
for i,(g,label,names,(dx,dy)) in enumerate(items,1):
    x,y,_=proj(centroid(Q,names))[0]
    bx,by=x+dx,y+dy
    ov.append(f'<path d="M{x:.0f} {y:.0f}L{bx:.0f} {by:.0f}" stroke="{INK}" stroke-width="1.6" stroke-dasharray="2 4"/>'
              f'<circle cx="{x:.0f}" cy="{y:.0f}" r="4" fill="{INK}"/>'+balloon(bx,by,i))
    legend.append((i,label))
x0,y0,x1,y1=bb; m=80
vb=[x0-m,y0-m-40,(x1-x0)+2*m,(y1-y0)+2*m+130]
# legend row
lx=vb[0]+50; ly=vb[1]+vb[3]-60
leg=''; cols=5
for k,(i,label) in enumerate(legend):
    cx=lx+(k%cols)*((vb[2]-100)/cols); cy=ly-30+(k//cols)*38-20
    leg+=balloon(cx+14,cy,i,r=13)+f'<text x="{cx+36:.0f}" y="{cy+5:.0f}" font-family="{SANS}" font-size="17" fill="{INK}">{label}</text>'
title=f'<text x="{vb[0]+50:.0f}" y="{vb[1]+66:.0f}" font-family="{SERIF}" font-size="34" fill="{INK}">Exploded view</text><text x="{vb[0]+50:.0f}" y="{vb[1]+96:.0f}" font-family="{MONO}" font-size="13" letter-spacing="2" fill="{MUTE}">YELLOWBOY · 99 × 113 × 20 MM · 4 PRINTED PARTS · 7 OFF-THE-SHELF PARTS</text>'
open('out/exploded.svg','w').write(svg_wrap(body+''.join(ov)+leg+title,vb,bg=IVORY))
