from common import *
from theme import SERIF,IVORY,CLAY,RULE
import sys
P=parts()
HL_LIT,HL_SH='#F4D9CC','#E6B29C'
def ikea_fill(hl):
    def f(n,c):
        g=[k for k,v in GROUPS.items() if n in v][0]
        if n=='mask': return '#ffffff','#ececea'
        if g in hl: return HL_LIT,HL_SH
        return '#ffffff','#e9e7e2'
    return f
SCREW=lambda x,y,s=1: (f'<g transform="translate({x},{y}) scale({s})" stroke="{INK}" stroke-width="2.2" fill="#fff">'
  '<path d="M-16 0h32v-7q0-7-7-7h-18q-7 0-7 7z"/><path d="M-6 0v34l6 9 6-9v-34" />'
  '<path d="M-6 8l12-4M-6 16l12-4M-6 24l12-4M-6 32l12-4" stroke-width="1.6"/>'
  '<path d="M-5 -10h10" stroke-width="2.6"/></g>')
def callout(x,y,qty,label,icon='screw'):
    w=230
    s=(f'<rect x="{x}" y="{y}" width="{w}" height="96" rx="14" fill="#fff" stroke="{RULE}" stroke-width="2"/>')
    if icon=='screw': s+=SCREW(x+44,y+30,0.95)
    elif icon=='tact':
        s+=(f'<g transform="translate({x+44},{y+48})" stroke="{INK}" stroke-width="2.2" fill="#fff"><rect x="-17" y="-8" width="34" height="22" rx="3"/>'
            f'<rect x="-8" y="-24" width="16" height="16" rx="3"/><path d="M-12 14v10M12 14v10"/></g>')
    elif icon=='cross':
        s+=(f'<g transform="translate({x+44},{y+48})" stroke="{INK}" stroke-width="2.2" fill="#fff"><path d="M-8 -26h16v18h18v16h-18v18h-16v-18h-18v-16h18z"/><circle r="3" fill="{INK}"/></g>')
    elif icon=='chip':
        s+=(f'<g transform="translate({x+44},{y+48})" stroke="{INK}" stroke-width="2.2" fill="#fff"><rect x="-22" y="-22" width="44" height="44" rx="4"/><rect x="-9" y="-12" width="18" height="24" fill="{INK}"/>'
            + ''.join(f'<circle cx="{-15+i*6}" cy="-16" r="1.8" fill="{INK}"/><circle cx="{-15+i*6}" cy="16" r="1.8" fill="{INK}"/>' for i in range(6)) + '</g>')
    elif icon=='wire':
        s+=(f'<g transform="translate({x+44},{y+48})" fill="none" stroke-width="4" stroke-linecap="round"><path d="M-26 -20c20 0 10 40 52 40" stroke="#B8432F"/><path d="M-26 -8c20 0 10 40 52 40" stroke="{INK}"/><path d="M-26 4c18 0 14 -26 52 -26" stroke="#C49A2C"/></g>')
    elif icon=='glue':
        s+=(f'<g transform="translate({x+44},{y+48})" stroke="{INK}" stroke-width="2.2" fill="#fff"><path d="M-10 -30h20v12l8 8v30h-36v-30l8-8z"/>'
            f'<path d="M-4 -30v-8h8v8"/><circle cx="0" cy="34" r="4" fill="{INK}"/></g>')
    s+=(f'<text x="{x+92}" y="{y+50}" font-family="{SANS}" font-size="34" font-weight="700" fill="{INK}">{qty}</text>'
        f'<text x="{x+92}" y="{y+76}" font-family="{SANS}" font-size="15" fill="#5f5b52">{label}</text>')
    return s
def step(num,groups,hl,offs,R,callouts,caption,arrows_for=(),W=1300,H=1000,extra=None,arrow_sh=(0,0)):
    Q=place(P,{g:offs.get(g,(0,0,0)) for g in GROUPS})
    Q={n:v for n,v in Q.items() if any(n in GROUPS[g] for g in groups) and n!='mask'}
    body,proj,bb,sc,c=draw(Q,R,W,H,fill=ikea_fill(hl),sw=(1.3,2.4))
    ov=''
    for g in arrows_for:
        names=[n for n in GROUPS[g] if n in Q]
        a=centroid(Q,names); b=a-np.array(offs[g])
        pa,pb=proj(a)[0],proj(b)[0]
        d=pb[:2]-pa[:2]; L=np.hypot(*d); u=d/L
        s0=pa[:2]+u*L*0.05+np.array(arrow_sh); s1=pa[:2]+u*L*0.95+np.array(arrow_sh)
        ov+=arrow(*s0,*s1,col='#fff',w=11,head=26)+arrow(*(s0+u*2),*(s1-u*3),col=INK,w=4,head=18)
    if extra: ov+=extra(proj)
    x0,y0,x1,y1=bb; m=70
    vb=[min(x0-m,0),min(y0-m-150,-30),0,0]
    vb[2]=max(x1+m,W)-vb[0]+ (0); vb[3]=max(y1+m,H)-vb[1]+90
    hdr=(f'<text x="{vb[0]+56}" y="{vb[1]+124}" font-family="{SERIF}" font-size="120" fill="{INK}">{num}</text>')
    cx=vb[0]+vb[2]-56
    for k,(q,l,ic) in enumerate(callouts):
        hdr+=callout(int(cx-230-k*250),int(vb[1]+40),q,l,ic)
    hdr+=(f'<text x="{vb[0]+56}" y="{vb[1]+vb[3]-44}" font-family="{SANS}" font-size="22" fill="{INK}">{caption}</text>')
    return svg_wrap(body+ov+hdr,vb,bg=IVORY,radius=24)
BACK=rot(200,130); FRONT=rot(20,-52)
steps=[
 (1,['shell','buttons','spk'],{'buttons','spk'},{'buttons':(0,0,-32),'spk':(0,0,-32)},BACK,
  [('2×','cross buttons','cross'),('1×','dab of glue','glue')],'Lay the shell face-down. Drop both crosses into their windows and glue the speaker into its ring.',['buttons','spk']),
 (2,['plate','tact','pcf'],{'tact','pcf'},{'tact':(0,0,22),'pcf':(0,0,22)},FRONT,
  [('8×','tact switch 6×6×7','tact'),('1×','PCF8574 module','chip')],'Press 8 tact switches into the plate pockets; seat the PCF8574 in the centre recess, header pins through the slots.',['pcf']),
 (3,['shell','buttons','spk','plate','tact','pcf'],{'plate','tact','pcf'},{'plate':(0,0,-34),'tact':(0,0,-34),'pcf':(0,0,-34)},BACK,
  [('4×','M3 screw','screw')],'Screw the switch plate onto the four bosses. It traps the crosses: each arm now sits on one switch.',['plate']),
 (4,['shell','buttons','spk','plate','tact','pcf','cyd'],{'cyd'},{'cyd':(0,0,-34)},BACK,
  [('4×','M3 screw','screw')],'Place the CYD screen-first into the window, USB-C facing the side slot, and fix it with four screws.',['cyd']),
 (5,['shell','buttons','spk','plate','tact','pcf','cyd','slide','boost','bat'],{'slide','boost','bat'},{'slide':(0,-14,-26),'boost':(0,0,-30),'bat':(0,0,-34)},BACK,
  [('2×','M2 screw','screw')],'Screw the SS12F15 to the top bracket, push the boost module’s USB-C into the bottom slot, lay the cell in its cradle.',['slide','boost','bat']),
 (7,['shell','buttons','spk','plate','tact','pcf','cyd','slide','boost','bat','cap'],{'cap'},{'cap':(0,0,-42)},BACK,
  [('4×','corner screw','screw')],'Close the back cap and drive the four corner screws. Done — flash the firmware and play.',['cap']),
]
WIRE={'red':'#B8432F','blk':'#2E2D2A','yel':'#C49A2C','blu':'#4A6FA5','wht':'#BDB9AD','pur':'#6E5C93'}
def wires(proj):
    def p(v): return proj(np.array(v,float))[0][:2]
    def w(a,b,col,lift=60,width=5):
        a,b=p(a),p(b); d=np.hypot(*(b-a)); k=max(lift,0.25*d)
        c1=a+np.array([0,-k]); c2=b+np.array([0,-k])
        path=f'M{a[0]:.1f} {a[1]:.1f}C{c1[0]:.1f} {c1[1]:.1f} {c2[0]:.1f} {c2[1]:.1f} {b[0]:.1f} {b[1]:.1f}'
        return (f'<path d="{path}" stroke="{INK}" stroke-width="{width+3.5}"/><path d="{path}" stroke="{WIRE[col]}" stroke-width="{width}"/>'
                f'<circle cx="{a[0]:.1f}" cy="{a[1]:.1f}" r="5" fill="{INK}"/><circle cx="{b[0]:.1f}" cy="{b[1]:.1f}" r="5" fill="{INK}"/>')
    def tag(v,text,dx=0,dy=-30):
        x,y=p(v); x+=dx; y+=dy; wdt=len(text)*9.6+22
        return (f'<rect x="{x-wdt/2:.0f}" y="{y-16:.0f}" width="{wdt:.0f}" height="28" rx="14" fill="{INK}"/>'
                f'<text x="{x:.0f}" y="{y+4:.0f}" font-family="{MONO}" font-size="15" font-weight="700" fill="#fff" text-anchor="middle">{text}</text>')
    o=''
    CN1=(-14,-21,-5.6); P1=(38,12,-5.6); SPK=(12,21,-5.6)
    # tact -> pcf (thin)
    for cx in (-34.5,25.5):
        for dx,dy in ((0,-7),(0,7),(-7,0),(7,0)):
            o+=w((cx+dx,-44+dy,-15),(-4.5+(dx+dy)*0.4+(cx>0)*4-2,-54,-15),'wht',lift=18,width=2.5)
    o+=w((-2.5,-70.5,-8.6),(14,-62,-1.5),'red',lift=30)
    o+=w((-47.5,-70.5,-8.6),(17,-62,-1.5),'blk',lift=55)
    o+=w((28,-62,-1.5),(-6.9,23,-13),'red',lift=50)
    o+=w((-1.9,23,-13),P1,'red',lift=40)
    o+=w((25,-62,-1.5),P1,'blk',lift=70)
    for i,col in enumerate(['blk','yel','blu','red']):
        o+=w((CN1[0]+i*1.5,CN1[1],CN1[2]),(-8+i*2.5,-34,-15),col,lift=35,width=4)
    o+=w((-14,-30,-10),SPK,'red',lift=40,width=3); o+=w((-12,-30,-10),(SPK[0]+2,SPK[1],SPK[2]),'blk',lift=46,width=3)
    o+=tag(CN1,'CN1 · I²C',-70,-10)+tag(P1,'P1 · 5V IN',50,-40)+tag(SPK,'SPEAK',95,-25)+tag((21,-64,-1.5),'BOOST',60,30)
    o+=tag((-25,-70.5,-8.6),'13450',0,50)+tag((-4.4,25,-13),'SS12F15',-150,-28)+tag((-4.5,-44,-15),'PCF8574',0,55)
    return o
steps.insert(5,(6,['shell','buttons','spk','plate','tact','pcf','cyd','slide','boost','bat'],set(),{},BACK,
  [('~25×','wires · see diagram','wire')],'Wire it up: battery → boost → switch → CYD, the I²C harness into CN1, the speaker into SPEAK.',[],1300,1000,wires))
import os
for s in steps:
    svg=step(*s)
    open(f'out/step-{s[0]}.svg','w').write(svg); print('step',s[0],len(svg)//1024,'KB')
