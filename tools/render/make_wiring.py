from comp import *
from theme import *
import numpy as np
W,H=1900,1250
BG=IVORY; TX=INK; K=IVORY
C=dict(v5='#B8432F',v33='#D97757',gnd='#8A8880',sda='#C49A2C',scl='#4A6FA5',spk='#7E6AA8',
       up='#5E8C6A',down='#3F7F7A',left='#7FA38C',right='#2F5F55',a='#B5677A',b='#8E4A5C',start='#C08A9A',select='#6E5C93')
o=[];wires=[];tags=[]
def route(pts,col,w=5,r=14,dots=True):
    w=w*0.7
    d=f'M{pts[0][0]:.1f} {pts[0][1]:.1f}'
    for i in range(1,len(pts)-1):
        p0,p1,p2=map(np.array,(pts[i-1],pts[i],pts[i+1]))
        a=p1-p0; b=p2-p1; la,lb=np.hypot(*a),np.hypot(*b)
        if la<1e-6 or lb<1e-6: continue
        rr=min(r,la/2,lb/2); q0=p1-a/la*rr; q1=p1+b/lb*rr
        d+=f'L{q0[0]:.1f} {q0[1]:.1f}Q{p1[0]:.1f} {p1[1]:.1f} {q1[0]:.1f} {q1[1]:.1f}'
    d+=f'L{pts[-1][0]:.1f} {pts[-1][1]:.1f}'
    s=f'<path d="{d}" stroke="{IVORY}" stroke-width="{w+4}" fill="none" stroke-linejoin="round" stroke-linecap="round"/><path d="{d}" stroke="{col}" stroke-width="{w}" fill="none" stroke-linejoin="round" stroke-linecap="round"/>'
    if dots:
        for p in (pts[0],pts[-1]): s+=f'<circle cx="{p[0]:.1f}" cy="{p[1]:.1f}" r="{max(3.2,w*0.8):.1f}" fill="{IVORY}" stroke="{col}" stroke-width="2"/>'
    wires.append(s)
def tag(x,y,text,col):
    tw=len(text)*8.0+20
    tags.append(f'<rect x="{x-tw/2:.0f}" y="{y-12:.0f}" width="{tw:.0f}" height="24" rx="12" fill="#FFFFFF" stroke="{col}" stroke-width="1.3"/>'+T(x,y+4.5,text,12,col,weight=600))
def head(x,y,t,sub=None,anchor='start'):
    s=T(x,y,t,18,TX,anchor,500,SERIF)
    if sub: s+=T(x,y+20,sub,12.5,MUTE,anchor,400,SANS)
    o.append(s)
# ---------- parts
CX,CY=560,140
cyd_s,cyd_p=cyd(CX,CY,6.8)
sw_s,sw_p=slide(110,150,7)
bo_s,bo_p=boost(95,420,7.5)
ba_s,ba_p=battery(60,720,6.0)
pc_s,pc_p=pcf(820,640,10)
sp_s,sp_p=speaker(1330,330,6.6)
S=9; D=92
tl=[];tp={}
for name,lab,cx,cy in [('up','UP',530,700),('down','DOWN',530,700+2*D),('left','LEFT',530-D,700+D),('right','RIGHT',530+D,700+D),
                       ('start','START',1480,700),('b','B',1480,700+2*D),('select','SELECT',1480-D,700+D),('a','A',1480+D,700+D)]:
    s_,p_=tact(cx,cy,S,lab); tl.append(s_); tp[name]=p_
parts_svg=[cyd_s,sw_s,bo_s,ba_s,pc_s,sp_s]+tl
# ---------- power
bp,bm=ba_p['+'],ba_p['-']
route([bp,(40,bp[1]),(40,bo_p['B+'][1]-40),(bo_p['B+'][0],bo_p['B+'][1]-40),bo_p['B+']],C['v5'])
route([bm,(bm[0]+28,bm[1]),(bm[0]+28,bo_p['B−'][1]-24),(bo_p['B−'][0],bo_p['B−'][1]-24),bo_p['B−']],C['gnd'])
tag(40,620,'BAT +',C['v5']); tag(bm[0]+28,660,'BAT −',C['gnd'])
op=bo_p['OUT+']; om=bo_p['OUT−']
route([op,(op[0],op[1]+40),(60,op[1]+40),(60,sw_p['1'][1]+36),(sw_p['1'][0],sw_p['1'][1]+36),sw_p['1']],C['v5'])
tag(60,330,'5 V',C['v5'])
cm=sw_p['COM']
route([cm,(cm[0],cm[1]+64),(470,cm[1]+64),(470,100),(cyd_p['VIN'][0],100),cyd_p['VIN']],C['v5'])
tag(470,200,'5 V · SWITCHED',C['v5'])
route([om,(om[0],om[1]+64),(500,om[1]+64),(500,116),(cyd_p['P1_GND'][0],116),cyd_p['P1_GND']],C['gnd'])
tag(500,500,'GND',C['gnd'])
# ---------- I2C harness (CN1 -> PCF)
xs=[pc_p['VCC'][0]-46-k*16 for k in range(4)]
for k,(key,pin,col) in enumerate([('IO22','SDA','sda'),('IO27','SCL','scl'),('CN1_GND','GND','gnd'),('3V3','VCC','v33')]):
    a=cyd_p[key]; b=pc_p[pin]; yy=CY+50*6.8+40+k*14
    route([a,(a[0],yy),(xs[k],yy),(xs[k],b[1]),b],C[col],w=4.5)
tag(xs[0]-24,560,'SDA · IO22',C['sda']); tag(xs[1]-90,590,'SCL · IO27',C['scl'])
for pin in ('A0','A1','A2'):
    b=pc_p[pin]; route([b,(b[0]-24,b[1]),(b[0]-24,pc_p['GND'][1])],C['gnd'],w=3,r=6,dots=False)
tag(pc_p['A1'][0]-110,pc_p['A1'][1],'A0–A2 → GND',C['gnd'])
# ---------- buttons
GY=1180
order=[('P7','up'),('P6','left'),('P5','down'),('P4','right'),('P3','select'),('P2','b'),('P1','start'),('P0','a')]
for i,(pin,btn) in enumerate(order):
    a=pc_p[pin]; b=tp[btn]['a']; xr=a[0]+34+i*13
    if btn in('up','down','left','right'):
        yb=1060+i*16; xb=b[0]-26-(0 if btn!='left' else 0)
        route([a,(xr,a[1]),(xr,yb),(xb,yb),(xb,b[1]),b],C[btn],w=4,r=10)
    else:
        yt=625-i*0+ (i-4)*14
        xb=b[0]-24
        route([a,(xr,a[1]),(xr,yt),(xb,yt),(xb,b[1]),b],C[btn],w=4,r=10)
for btn,p_ in tp.items():
    b=p_['b']; route([b,(b[0]+20,b[1]),(b[0]+20,GY)],C['gnd'],w=3,r=8,dots=False)
o.append(f'<path d="M220 {GY}H1680" stroke="{C["gnd"]}" stroke-width="5" stroke-linecap="round"/>')
route([pc_p['GND'],(pc_p['GND'][0]-80,pc_p['GND'][1]+0.01),(pc_p['GND'][0]-80,GY)],C['gnd'],w=3.5,r=8,dots=False)
tag(950,GY,'COMMON GND',C['gnd'])
for pin,btn in order: tag(pc_p[pin][0]+ (34+order.index((pin,btn))*13), 0,'',C[btn]) if False else None
# ---------- speaker
a,b=cyd_p['SPK+'],cyd_p['SPK-']
route([a,(a[0],86),(1300,86),(1300,sp_p['+'][1]-30),(sp_p['+'][0],sp_p['+'][1]-30),sp_p['+']],C['spk'],w=4)
route([b,(b[0],70),(1316,70),(1316,sp_p['-'][1]-18),(sp_p['-'][0],sp_p['-'][1]-18),sp_p['-']],C['gnd'],w=4)
tag(1150,86,'GPIO26 DAC → amp → SPEAK',C['spk'])
# ---------- headings
head(110,130,'Power switch','SS12F15 · top edge')
head(95,372,'Boost + charger','USB-C in · set to 5 V out')
head(60,700,'13450 Li-ion','3.7 V · 650 mAh')
head(820,620,'PCF8574T','I²C expander @ 0x20')
head(1330,330+11.5*6.6+34,'Speaker','8 Ω · 0.5 W','middle')
head(530,620,'D-pad','left cross','middle')
head(1480,620-0,'Action pad','right cross','middle')
head(CX+86*6.8,CY+50*6.8+30,'CYD · ESP32-2432S028R','back side · connectors as silkscreened','end')
# ---------- pin map table
tx,ty=1560,150
rows=[('UP','P7','up'),('DOWN','P5','down'),('LEFT','P6','left'),('RIGHT','P4','right'),('A','P0','a'),('B','P2','b'),('START','P1','start'),('SELECT','P3','select')]
o.append(f'<rect x="{tx}" y="{ty}" width="300" height="{70+len(rows)*30}" rx="14" fill="#FFFFFF" stroke="{RULE}"/>'+T(tx+22,ty+36,'Default pin map',18,TX,'start',500,SERIF))
for i,(n,p,k) in enumerate(rows):
    y=ty+68+i*30
    o.append(f'<circle cx="{tx+30}" cy="{y-5}" r="7" fill="{C[k]}"/>'+T(tx+50,y,n,14,TX,'start',500,SANS)+T(tx+278,y,p,14,C[k],'end',600))
o.append(T(tx+150,ty+70+len(rows)*30+26,'remappable on first boot',12,MUTE,'middle',500,SANS))
# legend
lx,ly=1560,540
leg=[('5 V','v5'),('3.3 V','v33'),('GND','gnd'),('SDA','sda'),('SCL','scl'),('Audio','spk')]
o.append(f'<rect x="{lx}" y="{ly}" width="300" height="{50+3*34}" rx="14" fill="#FFFFFF" stroke="{RULE}"/>')
for i,(t,k) in enumerate(leg):
    x=lx+24+(i%2)*140; y=ly+40+(i//2)*34
    o.append(f'<path d="M{x} {y}h34" stroke="{C[k]}" stroke-width="4" stroke-linecap="round"/>'+T(x+48,y+5,t,14,TX,'start',400,SANS))
hdr=T(40,58,'Wiring diagram',32,TX,'start',500,SERIF)+T(W-40,52,'buttons are active-low → PCF8574 quasi-bidirectional pull-ups, no resistors needed',14,MUTE,'end',500,SANS)
dots='<pattern id="dots" width="28" height="28" patternUnits="userSpaceOnUse"><circle cx="2" cy="2" r="1" fill="#E6E3D8"/></pattern>'
svg=(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}"><defs>{DEFS}{dots}</defs>'
     f'<rect width="{W}" height="{H}" rx="28" fill="{BG}"/><rect width="{W}" height="{H}" rx="28" fill="url(#dots)"/>'
     f'{"".join(parts_svg[:6])}{"".join(wires)}{"".join(parts_svg[6:])}{"".join(o)}{"".join(tags)}{hdr}</svg>')
open('out/wiring.svg','w').write(svg); print(len(svg)//1024,'KB')
