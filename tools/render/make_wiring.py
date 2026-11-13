from comp import *
from theme import *
import numpy as np
# Every net is routed by hand on orthogonal channels; the ordering rules in the
# comments keep the drawing free of wire crossings.
W,H=1900,1120
C=dict(v5='#B8432F',v33='#D97757',gnd='#8A8880',sda='#C49A2C',scl='#4A6FA5',spk='#6E5C93',btn='#5E8C6A')
wires=[];marks=[];text=[]
def route(pts,col,w=3.6,r=12,ends=(True,True)):
    d=f'M{pts[0][0]:.1f} {pts[0][1]:.1f}'
    for i in range(1,len(pts)-1):
        p0,p1,p2=map(np.array,(pts[i-1],pts[i],pts[i+1]))
        a=p1-p0; b=p2-p1; la,lb=np.hypot(*a),np.hypot(*b)
        if la<1e-6 or lb<1e-6: continue
        rr=min(r,la/2,lb/2); q0=p1-a/la*rr; q1=p1+b/lb*rr
        d+=f'L{q0[0]:.1f} {q0[1]:.1f}Q{p1[0]:.1f} {p1[1]:.1f} {q1[0]:.1f} {q1[1]:.1f}'
    d+=f'L{pts[-1][0]:.1f} {pts[-1][1]:.1f}'
    wires.append(f'<path d="{d}" stroke="{IVORY}" stroke-width="{w+5}" fill="none" stroke-linejoin="round" stroke-linecap="round"/>'
                 f'<path d="{d}" stroke="{col}" stroke-width="{w}" fill="none" stroke-linejoin="round" stroke-linecap="round"/>')
    for p,e in zip((pts[0],pts[-1]),ends):
        if e: marks.append(f'<circle cx="{p[0]:.1f}" cy="{p[1]:.1f}" r="4.2" fill="{IVORY}" stroke="{col}" stroke-width="2.2"/>')
def junction(x,y,col): marks.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="5" fill="{col}"/>')
def tag(x,y,t,col):
    tw=len(t)*7.6+20
    text.append(f'<rect x="{x-tw/2:.0f}" y="{y-11:.0f}" width="{tw:.0f}" height="22" rx="11" fill="#FFFFFF" stroke="{col}" stroke-width="1.2"/>'+T(x,y+4,t,11.5,col,weight=600))
def small(x,y,t,col,anchor='start'): text.append(T(x,y,t,11.5,col,anchor,600))
def head(x,y,t,sub=None,anchor='start'):
    s=T(x,y,t,19,INK,anchor,500,SERIF)
    if sub: s+=T(x,y+20,sub,12.5,MUTE,anchor,400,SANS)
    text.append(s)

# ───────── parts
CX,CY,CS=520,150,6.8
cyd_s,cyd=cyd(CX,CY,CS)
sw_s,sw=slide(110,170,7)
bo_s,bo=boost(110.5,400,7.5,note=False)
ba_s,ba=battery(60,640,6.0)
pc_s,pc=pcf(930,640,10,bridge=True)
sp_s,sp=speaker(1250,300,6.6)
SW_X=1330
BTNS=[('UP','P7',474),('LEFT','P6',544),('DOWN','P5',614),('RIGHT','P4',684),
      ('SELECT','P3',794),('B','P2',864),('START','P1',934),('A','P0',1004)]
tsw=[];tp={}
for name,pin,y in BTNS:
    s_,p_=tact(SW_X,y,9); tsw.append(s_); tp[name]=p_
parts=[cyd_s,sw_s,bo_s,ba_s,pc_s,sp_s]+tsw

# ───────── power: battery → boost → switch → P1
route([bo['OUT+'],sw['1']],C['v5'])                                   # OUT+ sits right under lug 1
route([sw['COM'],(sw['COM'][0],300),(440,300),(440,110),(cyd['VIN'][0],110),cyd['VIN']],C['v5'])
route([bo['OUT−'],(bo['OUT−'][0],380),(50,380),(50,86),(cyd['P1_GND'][0],86),cyd['P1_GND']],C['gnd'])
route([bo['B+'],(bo['B+'][0],575),(36,575),(36,ba['+'][1]),ba['+']],C['v5'])
route([bo['B−'],(bo['B−'][0],600),(352,600),(352,ba['-'][1]),ba['-']],C['gnd'])
tag(160,348,'5 V',C['v5']); tag(440,205,'5 V · switched',C['v5']); tag(50,230,'GND',C['gnd'])
tag(90,575,'BAT +',C['v5']); tag(280,600,'BAT −',C['gnd'])

# ───────── I²C: CN1 → PCF8574 (left source → lower pin, so nothing crosses)
gx=cyd['CN1_GND'][0]; GY=1065
route([cyd['3V3'],(cyd['3V3'][0],pc['VCC'][1]),pc['VCC']],C['v33'])
route([cyd['IO27'],(cyd['IO27'][0],pc['SCL'][1]),pc['SCL']],C['scl'])
route([cyd['IO22'],(cyd['IO22'][0],pc['SDA'][1]),pc['SDA']],C['sda'])
route([cyd['CN1_GND'],(gx,GY)],C['gnd'],ends=(True,False))
route([(gx,pc['A2'][1]),pc['A2']],C['gnd'],ends=(False,True)); junction(gx,pc['A2'][1],C['gnd'])
for k,lab,col in (('VCC','3V3','v33'),('SCL','SCL · IO27','scl'),('SDA','SDA · IO22','sda'),('A2','GND','gnd')):
    small(890,pc[k][1]-6,lab,C[col],'end')

# ───────── buttons: P-pin comb → one switch each, right legs onto the GND bus
BUS=1400
for i,(name,pin,y) in enumerate(BTNS):
    a=pc[pin]; b=tp[name]['a']
    up=i<4
    k=i if up else 7-i                         # outer pins turn first → no crossings
    xt=1150+k*15
    route([a,(xt,a[1]),(xt,b[1]),b],C['btn'],w=3)
    route([tp[name]['b'],(BUS,y)],C['gnd'],w=3,ends=(True,False)); junction(BUS,y,C['gnd'])
    text.append(T(BUS+22,y+5,name,14,INK,'start',600,SANS)+T(BUS+120,y+5,pin,13,C['btn'],'start',600))
route([(BUS,BTNS[0][2]),(BUS,GY),(gx,GY)],C['gnd'],w=3.6,ends=(False,False)); junction(gx,GY,C['gnd'])
tag(1030,GY,'common ground',C['gnd'])
for (y0,y1,lab) in ((474,684,'D-pad'),(794,1004,'Action pad')):
    text.append(f'<path d="M1585 {y0-14}h8v{y1-y0+28}h-8" stroke="{RULE}" stroke-width="2" fill="none"/>'+T(1608,(y0+y1)/2+6,lab,18,INK,'start',500,SERIF))

# ───────── speaker
route([cyd['SPK+'],(cyd['SPK+'][0],120),(sp['+'][0],120),sp['+']],C['spk'])
route([cyd['SPK-'],(cyd['SPK-'][0],140),(sp['-'][0],140),sp['-']],C['gnd'])
tag(1040,120,'GPIO26 DAC → amp',C['spk'])

# ───────── headings
head(110,150,'Power switch','SS12F15 · top edge')
head(305,450,'Boost + charger','set output to 5 V')
head(60,770,'13450 Li-ion','3.7 V · 650 mAh')
head(930,612,'PCF8574T','solder side · I²C 0x20')
head(1250,410,'Speaker','8 Ω · 0.5 W','middle')
head(CX+86*CS,CY+50*CS+40,'CYD · ESP32-2432S028R','back side · connectors as silkscreened','end')
text.append(T(932,864,'A0–A2 → GND (0x20)',11.5,MUTE,'start',500,SANS))

# ───────── legend + notes
lx,ly=1460,100
leg=[('5 V','v5'),('3.3 V','v33'),('GND','gnd'),('SDA','sda'),('SCL','scl'),('Audio','spk'),('Button','btn')]
text.append(f'<rect x="{lx}" y="{ly}" width="400" height="{56+4*30}" rx="14" fill="#FFFFFF" stroke="{RULE}"/>'+T(lx+24,ly+36,'Legend',18,INK,'start',500,SERIF))
for i,(t,k) in enumerate(leg):
    x=lx+24+(i%2)*190; y=ly+70+(i//2)*30
    text.append(f'<path d="M{x} {y-4}h34" stroke="{C[k]}" stroke-width="3.6" stroke-linecap="round"/>'+T(x+48,y+1,t,14,INK,'start',400,SANS))
notes=['Buttons are active-low. The PCF8574 has','internal pull-ups, so no resistors.','Wire them in any order: the first boot','asks you to press each button once.']
nx,ny=60,850
text.append(f'<rect x="{nx}" y="{ny}" width="400" height="{40+len(notes)*21}" rx="14" fill="#FFFFFF" stroke="{RULE}"/>')
for i,n in enumerate(notes): text.append(T(nx+24,ny+32+i*21,n,13.5,SLATE,'start',400,SANS))

hdr=T(40,60,'Wiring diagram',32,INK,'start',500,SERIF)
svg=(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}"><defs>{DEFS}</defs>'
     f'<rect width="{W}" height="{H}" rx="28" fill="{IVORY}"/>'
     f'{"".join(parts)}{"".join(wires)}{"".join(marks)}{"".join(text)}{hdr}</svg>')
open('out/wiring.svg','w').write(svg); print(len(svg)//1024,'KB')
