# 2D component illustrations. Each fn returns (svg, pins) ; pins: name->(x,y) absolute
MONO="ui-monospace,'SF Mono','JetBrains Mono',Menlo,Consolas,monospace"
SANS="-apple-system,'Segoe UI',Helvetica,Arial,sans-serif"
DEFS='''
<linearGradient id="gMetal"><stop stop-color="#DAD8D1"/></linearGradient>
<linearGradient id="gGold"><stop stop-color="#C4A15F"/></linearGradient>
<linearGradient id="gCyd"><stop stop-color="#E6B65A"/></linearGradient>
<linearGradient id="gPur"><stop stop-color="#6F6194"/></linearGradient>
<linearGradient id="gBlk"><stop stop-color="#2E2D2A"/></linearGradient>
<linearGradient id="gBat"><stop stop-color="#F5F3EC"/></linearGradient>
<linearGradient id="gBatR"><stop stop-color="#B8432F"/></linearGradient>
<linearGradient id="gBatK"><stop stop-color="#2E2D2A"/></linearGradient>
<linearGradient id="gSpk"><stop stop-color="#D3D1CA"/></linearGradient>
<linearGradient id="gCone"><stop stop-color="#3B3A37"/></linearGradient>
<linearGradient id="gBrown"><stop stop-color="#946A47"/></linearGradient>
<filter id="sh"><feOffset dx="0" dy="0"/></filter>
'''
def T(x,y,t,size=10,fill='#fff',anchor='middle',weight=600,font=MONO,rot=0,op=1):
    r=f' transform="rotate({rot} {x} {y})"' if rot else ''
    return f'<text x="{x:.1f}" y="{y:.1f}" font-family="{font}" font-size="{size}" font-weight="{weight}" fill="{fill}" text-anchor="{anchor}" opacity="{op}"{r}>{t}</text>'
def smd(x,y,w,h,body='#1f1f22',cap='#d9d9d9'):
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w}" height="{h}" rx=".8" fill="{cap}"/>'
            f'<rect x="{x+w*0.22:.1f}" y="{y:.1f}" width="{w*0.56:.1f}" height="{h}" fill="{body}"/>')
def soic(x,y,w,h,n,label='',pin='#cfd2d6',fs=7,rot=0):
    s=f'<g transform="rotate({rot} {x+w/2} {y+h/2})">'
    p=w/(n+0.5)
    for i in range(n):
        px=x+p*(i+0.5)
        s+=f'<rect x="{px:.1f}" y="{y-4:.1f}" width="{p*0.45:.1f}" height="5" fill="{pin}"/><rect x="{px:.1f}" y="{y+h-1:.1f}" width="{p*0.45:.1f}" height="5" fill="{pin}"/>'
    s+=f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="1.5" fill="#1b1c1f"/><circle cx="{x+5}" cy="{y+h-5}" r="1.8" fill="#333"/>'
    if label: s+=T(x+w/2,y+h/2+fs*0.35,label,fs,'#8d9096',weight=500)
    return s+'</g>'
def jst(x,y,n,pitch=12,label=None,labels=None,vertical=False,lc='#3b2a00',exit='top',fs=7.2):
    # JST 1.25 style connector, beige housing
    w=n*pitch+8; h=16
    s=f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="2.5" fill="#f3ecdc" stroke="#c9bd9f"/>'
    s+=f'<rect x="{x+3}" y="{y+3}" width="{w-6}" height="{h-8}" rx="1.5" fill="#e2d6bb"/>'
    pins={}
    for i in range(n):
        cx=x+4+pitch*(i+0.5)
        s+=f'<rect x="{cx-2.2:.1f}" y="{y+5}" width="4.4" height="5" fill="url(#gGold)"/>'
        pins[i]=(cx,y if exit=='top' else y+h)
        if labels: s+=T(cx,(y+h+fs+3) if exit=='top' else (y-4),labels[i],fs,lc,weight=800)
    if label: s+=T(x+w/2,(y-6) if exit=='top' else (y+h+fs+6),label,fs+1.6,lc,weight=800)
    return s,pins

def cyd(x,y,s=6.4):
    W,H=86*s,50*s
    o=f'<g filter="url(#sh)"><rect x="{x}" y="{y}" width="{W}" height="{H}" rx="{2.5*s}" fill="url(#gCyd)" stroke="#141413" stroke-width="1.5"/></g>'
    # traces
    import random; random.seed(3)
    tr=''
    for i in range(16):
        yy=y+H*0.18+i*H*0.045; x0=x+W*0.22; x1=x+W*(0.55+random.random()*0.25)
        tr+=f'<path d="M{x0:.0f} {yy:.0f}H{x1-20:.0f}l14 14H{x1+40:.0f}" stroke="#CFA14E" stroke-width="2" fill="none"/>'
    o+=tr
    for hx,hy in ((3.5,3.5),(82.5,3.5),(3.5,46.5),(82.5,46.5)):
        o+=f'<circle cx="{x+hx*s:.1f}" cy="{y+hy*s:.1f}" r="{3.2*s/2+3:.1f}" fill="#e3e1da"/><circle cx="{x+hx*s:.1f}" cy="{y+hy*s:.1f}" r="{3.2*s/2:.1f}" fill="#16233a"/>'
    # ESP32 module (right side in back view)
    ex,ey=x+W-26*s,y+11*s
    o+=f'<rect x="{ex}" y="{ey}" width="{25.5*s}" height="{18*s}" rx="3" fill="#202125"/>'
    o+=f'<rect x="{ex+6.5*s}" y="{ey+1*s}" width="{18*s}" height="{16*s}" rx="2" fill="url(#gMetal)" stroke="#8e9298"/>'
    o+=T(ex+15.5*s,ey+7*s,'ESP32-WROOM-32',8.5,'#55595f',weight=700)+T(ex+15.5*s,ey+10*s,'Wi-Fi · BT · 240 MHz',6.5,'#6b6f75',weight=500)
    o+=f'<path d="M{ex+1.5*s} {ey+2.5*s}h{4*s}v{2.2*s}h-{3*s}v{2.2*s}h{3*s}v{2.2*s}h-{3*s}v{2.2*s}h{3*s}v{2.2*s}h-{3*s}v{2.2*s}h{3*s}" stroke="#c9a227" stroke-width="2" fill="none"/>'
    # SD slot
    sx,sy=x+38*s,y+28*s
    o+=f'<rect x="{sx}" y="{sy}" width="{14*s}" height="{15*s}" rx="2" fill="url(#gMetal)" stroke="#8e9298"/>'
    o+=f'<path d="M{sx+2*s} {sy+3*s}h{10*s}M{sx+2*s} {sy+5*s}h{10*s}" stroke="#8e9298"/>'+T(sx+7*s,sy+10*s,'µSD',10,'#4b4f55',weight=800)
    # USB ports on left edge (back view mirrored)
    o+=f'<rect x="{x-3}" y="{y+19*s}" width="{8*s}" height="{9*s}" rx="6" fill="url(#gMetal)" stroke="#8e9298"/><rect x="{x+1.5*s}" y="{y+21.5*s}" width="{4*s}" height="{4*s}" rx="4" fill="#2a2c30"/>'
    o+=T(x+10*s,y+24.5*s,'USB-C',7,'#7a4300',anchor='start',weight=800)
    o+=f'<rect x="{x-2}" y="{y+31*s}" width="{6*s}" height="{8*s}" rx="2" fill="url(#gMetal)" stroke="#8e9298"/>'
    # chips
    o+=soic(x+16*s,y+30*s,10*s,5*s,8,'CH340C',fs=7)
    o+=soic(x+27*s,y+19.5*s,5*s,4*s,4,'',fs=6)+T(x+29.5*s,y+27*s,'AMS1117',6.5,'#7a4300',weight=800)
    o+=soic(x+28*s,y+5*s,5*s,4*s,4,'',fs=6)+T(x+30.5*s,y+12.5*s,'SC8002B',6.5,'#7a4300',weight=800)
    # passives
    for i in range(8): o+=smd(x+(35+i*2.2)*s,y+21*s,1.6*s,0.8*s)
    for i in range(6): o+=smd(x+(56+i*2.2)*s,y+42*s,1.6*s,0.8*s)
    # RGB LED
    o+=f'<rect x="{x+56*s}" y="{y+33*s}" width="{5*s}" height="{5*s}" rx="2" fill="#fafafa" stroke="#bbb"/><circle cx="{x+58.5*s}" cy="{y+35.5*s}" r="{1.6*s}" fill="#d9e6ff"/>'
    o+=T(x+58.5*s,y+41*s,'RGB',6.5,'#7a4300',weight=800)
    # buttons
    for i,lab in enumerate(('BOOT','RST')):
        bx=x+(68+i*7)*s; by=y+3.5*s
        o+=f'<rect x="{bx}" y="{by}" width="{4*s}" height="{3*s}" rx="2" fill="url(#gMetal)"/><rect x="{bx+1*s}" y="{by+0.7*s}" width="{2*s}" height="{1.6*s}" rx="2" fill="#e8e8e8"/>'+T(bx+2*s,by+5*s,lab,6,'#7a4300',weight=800)
    pins={}
    # connectors (pin order as silkscreened)
    s1,p1=jst(x+6*s,y+5*s,4,pitch=3.6*s,fs=max(6.5,1.1*s),labels=['VIN','TX','RX','GND'],label='P1 · POWER')
    o+=s1; pins['VIN']=p1[0]; pins['P1_GND']=p1[3]
    s2,p2=jst(x+19*s,y+40*s,4,pitch=3.6*s,fs=max(6.5,1.1*s),labels=['GND','IO22','IO27','3V3'],label='CN1 · I²C',exit='bottom')
    o+=s2; pins['CN1_GND']=p2[0]; pins['IO22']=p2[1]; pins['IO27']=p2[2]; pins['3V3']=p2[3]
    s3,p3=jst(x+44*s,y+5*s,2,pitch=3.6*s,fs=max(6.5,1.1*s),labels=['+','−'],label='SPEAK')
    o+=s3; pins['SPK+']=p3[0]; pins['SPK-']=p3[1]
    s4,p4=jst(x+62*s,y+40*s,4,pitch=3.6*s,fs=max(6.5,1.1*s),labels=['GND','IO35','IO22','IO21'],label='P3',exit='bottom')
    o+=s4
    o+=T(x+4*s,y+H-3*s,'ESP32-2432S028R',max(7,1.2*s),'#7a4300',anchor='start',weight=800)
    return o,pins

def pcf(x,y,s=7):
    W,H=22*s,20*s
    o=f'<g filter="url(#sh)"><rect x="{x}" y="{y}" width="{W}" height="{H}" rx="{1.5*s}" fill="url(#gPur)" stroke="#141413" stroke-width="1.5"/></g>'
    L=['VCC','GND','SCL','SDA','A0','A1','A2','INT']; Rr=['P7','P6','P5','P4','P3','P2','P1','P0']
    pins={}
    for i in range(8):
        py=y+(2.2+i*2.2)*s
        for side,lab,xx in ((0,L[i],x+2*s),(1,Rr[i],x+W-2*s)):
            o+=f'<circle cx="{xx:.1f}" cy="{py:.1f}" r="{0.9*s:.1f}" fill="url(#gGold)"/><circle cx="{xx:.1f}" cy="{py:.1f}" r="{0.42*s:.1f}" fill="#2a1546"/>'
            o+=T(xx+(1.7*s if side==0 else -1.7*s),py+3,lab,7.5,'#f3eaff',anchor='start' if side==0 else 'end',weight=700)
            pins[lab]=(xx,py)
    o+=soic(x+7.5*s,y+6*s,7*s,8*s,8,'PCF8574T',fs=7.5,rot=90)
    o+=f'<circle cx="{x+W/2:.1f}" cy="{y+H-2.6*s:.1f}" r="{1.2*s:.1f}" fill="#1b0f2b" stroke="#d8c4ff" stroke-width="1.5"/>'
    for i in range(3): o+=smd(x+(8+i*2.4)*s,y+2*s,1.6*s,0.8*s)
    return o,pins

def tact(cx,cy,s=6,label=None,col='#2b2b2f',lc='#141413'):
    w=6*s
    o=f'<g filter="url(#sh)">'
    for sx in (-1,1):
        o+=f'<rect x="{cx+sx*(w/2+0.9*s)-0.9*s:.1f}" y="{cy-0.6*s:.1f}" width="{1.8*s:.1f}" height="{1.2*s:.1f}" rx="2" fill="#cfd2d6"/>'
    o+=f'<rect x="{cx-w/2:.1f}" y="{cy-w/2:.1f}" width="{w}" height="{w}" rx="{0.6*s}" fill="url(#gMetal)" stroke="#141413" stroke-width="1.2"/>'
    o+=''.join(f'<circle cx="{cx+dx*2.2*s:.1f}" cy="{cy+dy*2.2*s:.1f}" r="{0.45*s:.1f}" fill="#33353a"/>' for dx in(-1,1) for dy in(-1,1))
    o+=f'<circle cx="{cx}" cy="{cy}" r="{1.9*s:.1f}" fill="{col}"/><circle cx="{cx-0.4*s:.1f}" cy="{cy-0.4*s:.1f}" r="{0.9*s:.1f}" fill="#fff" opacity=".12"/></g>'
    if label: o+=T(cx,cy-w/2-10,label,12,lc,weight=800)
    pins={'a':(cx-w/2-1.6*s,cy),'b':(cx+w/2+1.6*s,cy)}
    return o,pins

def speaker(cx,cy,s=6):
    r=11.5*s
    o=f'<g filter="url(#sh)"><circle cx="{cx}" cy="{cy}" r="{r}" fill="url(#gSpk)" stroke="#141413" stroke-width="1.5"/></g>'
    o+=f'<circle cx="{cx}" cy="{cy}" r="{r*0.86}" fill="none" stroke="#8f939a" stroke-width="2"/>'
    o+=f'<circle cx="{cx}" cy="{cy}" r="{r*0.7}" fill="url(#gCone)"/>'
    o+=f'<circle cx="{cx}" cy="{cy}" r="{r*0.52}" fill="none" stroke="#3c3e44" stroke-width="2"/>'
    o+=f'<circle cx="{cx}" cy="{cy}" r="{r*0.3}" fill="#2a2b30" stroke="#55575d"/>'
    o+=T(cx,cy-2,'8Ω',13,'#e6e7ea',weight=800)+T(cx,cy+12,'0.5W',9,'#b8bbc2',weight=700)
    pins={'+':(cx+r*0.55,cy-r*0.84),'-':(cx+r*0.75,cy-r*0.66)}
    o+=f'<rect x="{pins["+"][0]-6:.0f}" y="{pins["+"][1]-4:.0f}" width="22" height="9" rx="2" fill="#e3c27a" transform="rotate(40 {pins["+"][0]} {pins["+"][1]})"/>'
    return o,pins

def boost(x,y,s=7):
    W,H=23*s,17*s
    o=f'<g filter="url(#sh)"><rect x="{x}" y="{y}" width="{W}" height="{H}" rx="{1*s}" fill="url(#gBlk)" stroke="#141413" stroke-width="1.5"/></g>'
    # USB-C on right edge
    o+=f'<rect x="{x+W-6*s}" y="{y+4.8*s}" width="{7.5*s}" height="{7.4*s}" rx="3" fill="url(#gMetal)" stroke="#8e9298"/><rect x="{x+W-5*s}" y="{y+6.6*s}" width="{5.5*s}" height="{3.8*s}" rx="6" fill="#2a2c30"/>'
    # inductor
    o+=f'<rect x="{x+2*s}" y="{y+6.5*s}" width="{6.6*s}" height="{6.6*s}" rx="{1.2*s}" fill="#3c3d42" stroke="#55575d"/>'+T(x+5.3*s,y+10.6*s,'100',11,'#a9abb0',weight=800)
    o+=soic(x+10*s,y+4*s,5*s,3.5*s,4,'',fs=6)+soic(x+10*s,y+11*s,5*s,3.5*s,4,'',fs=6)
    o+=f'<circle cx="{x+15*s}" cy="{y+2.2*s}" r="{1.3*s}" fill="#f4f4f4"/><path d="M{x+14.2*s} {y+2.2*s}h{1.6*s}" stroke="#555" stroke-width="2"/>'
    o+=f'<rect x="{x+16.5*s}" y="{y+13.5*s}" width="{1.2*s}" height="{0.8*s}" fill="#4cff7a"/><rect x="{x+18.5*s}" y="{y+13.5*s}" width="{1.2*s}" height="{0.8*s}" fill="#ff4c4c"/>'
    pins={}
    for i,(lab,px,py) in enumerate((('B+',2.6,2.2),('B−',6.6,2.2),('OUT+',2.6,15),('OUT−',6.6,15))):
        cx,cy=x+px*s,y+py*s
        o+=f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{1.1*s:.1f}" fill="url(#gGold)"/><circle cx="{cx:.1f}" cy="{cy:.1f}" r="{0.45*s:.1f}" fill="#111"/>'
        o+=T(cx,cy+(-1.7*s if py<5 else 2.6*s),lab,7.5,'#f0f0f0',weight=800)
        pins[lab]=(cx,cy)
    o+=T(x+W/2,y+H+16,'set output → 5 V',8,'#141413',weight=700)
    return o,pins

def battery(x,y,s=6,L=45,D=13):
    W,H=L*s,D*s
    o=f'<g filter="url(#sh)"><rect x="{x}" y="{y}" width="{W}" height="{H}" rx="{H*0.18}" fill="url(#gBat)" stroke="#141413" stroke-width="1.5"/></g>'
    o+=f'<path d="M{x+H*0.18} {y}h{W*0.17}v{H}h-{W*0.17}a{H*0.18} {H*0.18} 0 0 1 -{H*0.18} -{H*0.18}v-{H-H*0.36}a{H*0.18} {H*0.18} 0 0 1 {H*0.18} -{H*0.18}z" fill="url(#gBatR)"/>'
    o+=f'<path d="M{x+W-H*0.18-W*0.14} {y}h{W*0.14}a{H*0.18} {H*0.18} 0 0 1 {H*0.18} {H*0.18}v{H-H*0.36}a{H*0.18} {H*0.18} 0 0 1 -{H*0.18} {H*0.18}h-{W*0.14}z" fill="url(#gBatK)"/>'
    o+=T(x+W*0.52,y+H*0.45,'+13450  3.7V  650mAh',10,'#2a2a2e',weight=700)+T(x+W*0.52,y+H*0.45+14,'2.41Wh',9,'#55565c',weight=600)
    o+=f'<rect x="{x-5}" y="{y+H*0.3}" width="7" height="{H*0.4}" rx="2" fill="url(#gMetal)"/>'
    pins={'+':(x-2,y+H/2),'-':(x+W+2,y+H/2)}
    o+=T(x+W*0.09,y+H+15,'+',14,'#ff6b5f',weight=900)+T(x+W*0.93,y+H+15,'−',14,'#c8c8cc',weight=900)
    return o,pins

def slide(x,y,s=7):
    # SS12F15 front view: metal plate with ears, black body, brown base, 3 lugs, actuator
    W=20*s
    o=f'<g filter="url(#sh)">'
    o+=f'<rect x="{x+W/2-1.2*s}" y="{y}" width="{2.4*s}" height="{4*s}" rx="2" fill="#2b2b2f"/>'
    o+=''.join(f'<path d="M{x+W/2-1.2*s} {y+(0.6+i*0.7)*s}h{2.4*s}" stroke="#4a4a50" stroke-width="1.5"/>' for i in range(5))
    o+=f'<path d="M{x} {y+4*s}h{W}v{2.6*s}h-{W}z" fill="#232327"/>'
    o+=f'<circle cx="{x+2*s}" cy="{y+5.3*s}" r="{0.8*s}" fill="#0d0d0f"/><circle cx="{x+W-2*s}" cy="{y+5.3*s}" r="{0.8*s}" fill="#0d0d0f"/>'
    o+=f'<rect x="{x+5.7*s}" y="{y+6.6*s}" width="{8.6*s}" height="{3.6*s}" fill="#1e1e22"/>'
    o+=f'<rect x="{x+5.7*s}" y="{y+10.2*s}" width="{8.6*s}" height="{2*s}" fill="url(#gBrown)"/></g>'
    pins={}
    for i,lab in enumerate(('1','COM','3')):
        cx=x+(7.2+i*2.8)*s
        o+=f'<rect x="{cx-0.55*s:.1f}" y="{y+12.2*s:.1f}" width="{1.1*s:.1f}" height="{3*s:.1f}" rx="2" fill="url(#gMetal)"/><circle cx="{cx:.1f}" cy="{y+14.3*s:.1f}" r="{0.35*s:.1f}" fill="#222"/>'
        pins[lab]=(cx,y+15.2*s)
    return o,pins
