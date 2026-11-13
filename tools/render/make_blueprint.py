from common import *
from theme import *
from line import render_lines, chain, path_d
P=parts(); Q=place(P,{})
BG=IVORY; GRID='#EEEBE1'; LINE=INK; DIM=MUTE
HID={'cyd_pcb':CLAY,'cyd_lcd':CLAY,'cyd_esp':CLAY,'bat':'#B8432F','boost':'#946A47','slide':'#5E8C6A','spk':'#6E5C93','plate':'#4A6FA5','pcf':'#6E5C93','tact':'#4A6FA5'}
S=4.4
def view(R,W,H,hidden=()):
    res,proj,img,idb,zb,sc,c=render_lines(Q,R,W,H,scale=S,hidden=hidden)
    g=[]
    for n,segs in res.items():
        for k,(w,col,dash) in {0:(0.9,LINE,''),1:(1.7,LINE,''),2:(1.1,HID.get(n,DIM),' stroke-dasharray="5 4"')}.items():
            s=[x for x in segs if x[4]==k]
            if s: g.append(f'<path d="{path_d(chain(s))}" stroke="{col}" stroke-width="{w}"{dash}/>')
    return ''.join(g),proj
def dim_h(x0,x1,y,label,ext0,ext1):
    return (f'<path d="M{x0} {ext0}V{y+8}M{x1} {ext1}V{y+8}" stroke="{DIM}" stroke-width="1" opacity=".7"/>'
            f'<path d="M{x0} {y}H{x1}" stroke="{DIM}" stroke-width="1.4"/>'
            f'<path d="M{x0} {y}l12 -5v10zM{x1} {y}l-12 -5v10z" fill="{DIM}"/>'
            f'<rect x="{(x0+x1)/2-34}" y="{y-13}" width="68" height="26" fill="{BG}"/>'
            f'<text x="{(x0+x1)/2}" y="{y+6}" font-family="{MONO}" font-size="17" fill="{LINE}" text-anchor="middle">{label}</text>')
def dim_v(y0,y1,x,label,ext0,ext1):
    return (f'<path d="M{ext0} {y0}H{x-8}M{ext1} {y1}H{x-8}" stroke="{DIM}" stroke-width="1" opacity=".7"/>'
            f'<path d="M{x} {y0}V{y1}" stroke="{DIM}" stroke-width="1.4"/>'
            f'<path d="M{x} {y0}l-5 12h10zM{x} {y1}l-5 -12h10z" fill="{DIM}"/>'
            f'<g transform="translate({x},{(y0+y1)/2}) rotate(-90)"><rect x="-38" y="-13" width="76" height="26" fill="{BG}"/>'
            f'<text y="6" font-family="{MONO}" font-size="17" fill="{LINE}" text-anchor="middle">{label}</text></g>')
W,H=1700,1150
body=[]
# front view (x-ray)
fw,fp=view(cam(0,0),700,700,hidden=tuple(HID))
FX,FY=150,330
body.append(f'<g transform="translate({FX},{FY})">{fw}</g>')
lo=fp(np.array([[-53.86,-81,2]]))[0]; hi=fp(np.array([[45.12,32,2]]))[0]
x0,x1=FX+lo[0],FX+hi[0]; ytop,ybot=FY+hi[1],FY+lo[1]
body.append(dim_h(x0,x1,ybot+60,'99',ybot+10,ybot+10)); body.append(dim_v(ytop,ybot,x0-55,'113',x0-10,x0-10))
# right side view
sw_,sp=view(cam(-90,0),300,700)
SX=FX+560; body.append(f'<g transform="translate({SX},{FY})">{sw_}</g>')
a=sp(np.array([[45,0,2]]))[0]; b=sp(np.array([[45,0,-18]]))[0]
xa,xb=sorted([SX+a[0],SX+b[0]]); body.append(dim_h(xa,xb,ybot+60,'20',ybot+10,ybot+10))
# top view
tw,tp=view(cam(0,90),700,300)
TY=FY-330; body.append(f'<g transform="translate({FX},{TY})">{tw}</g>')
# labels
def lab(x,y,t): return f'<text x="{x}" y="{y}" font-family="{MONO}" font-size="15" letter-spacing="3" fill="{DIM}">{t}</text>'
body+= [lab(FX+170,FY+40,'FRONT · X-RAY'),lab(SX+80,FY+40,'RIGHT'),lab(FX+170,TY+60,'TOP')]
# legend of hidden components
ly=FY+60; lx=1010
items=[('CYD ESP32-2432S028R',CLAY),('Switch plate + 8× tact','#4A6FA5'),('PCF8574 / speaker','#6E5C93'),('13450 Li-ion cell','#B8432F'),('Boost / charger','#946A47'),('SS12F15 power switch','#5E8C6A')]
body.append(lab(lx,ly,'HIDDEN COMPONENTS'))
for i,(t,c) in enumerate(items):
    y=ly+40+i*36
    body.append(f'<path d="M{lx} {y-5}h46" stroke="{c}" stroke-width="2" stroke-dasharray="7 5"/><text x="{lx+62}" y="{y}" font-family="{SANS}" font-size="17" fill="{LINE}">{t}</text>')
# ports callouts
ports=[('USB-C (flash)','right side'),('USB-C (charge)','bottom edge'),('Power slide','top edge'),('Speaker grille','front face')]
py=ly+330; body.append(lab(lx,py,'I/O'))
for i,(a_,b_) in enumerate(ports):
    body.append(f'<text x="{lx}" y="{py+38+i*32}" font-family="{SANS}" font-size="18" fill="{LINE}">{a_}<tspan fill="{DIM}" font-family="{MONO}" font-size="14"> — {b_}</tspan></text>')
# title block
tb=f'''<g transform="translate({W-640},{H-170})" font-family="{MONO}">
<rect width="600" height="130" fill="none" stroke="{DIM}" stroke-width="1.4"/>
<path d="M0 52H600M300 52V130M450 52V130" stroke="{DIM}" stroke-width="1"/>
<text x="20" y="36" font-size="24" font-family="{SERIF}" fill="{LINE}">YellowBoy — general assembly</text>
<text x="20" y="80" font-size="12" fill="{DIM}" letter-spacing="2">MATERIAL</text><text x="20" y="108" font-size="17" fill="{LINE}">PLA · 2 colours</text>
<text x="320" y="80" font-size="12" fill="{DIM}" letter-spacing="2">UNITS</text><text x="320" y="108" font-size="17" fill="{LINE}">mm</text>
<text x="470" y="80" font-size="12" fill="{DIM}" letter-spacing="2">SHEET</text><text x="470" y="108" font-size="17" fill="{LINE}">1 / 1</text></g>'''
grid=f'<pattern id="g" width="40" height="40" patternUnits="userSpaceOnUse"><path d="M40 0H0V40" fill="none" stroke="{GRID}" stroke-width="1"/></pattern><pattern id="G" width="200" height="200" patternUnits="userSpaceOnUse"><rect width="200" height="200" fill="url(#g)"/><path d="M200 0H0V200" fill="none" stroke="#E4E0D4" stroke-width="1.2"/></pattern>'
svg=(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}"><defs>{grid}</defs>'
     f'<rect width="{W}" height="{H}" rx="28" fill="{BG}"/><rect x="20" y="20" width="{W-40}" height="{H-40}" rx="14" fill="url(#G)" stroke="{RULE}"/>'
     f'<g fill="none" stroke-linecap="round" stroke-linejoin="round">{"".join(body)}</g>{tb}</svg>')
open('out/blueprint.svg','w').write(svg); print(len(svg)//1024,'KB')
