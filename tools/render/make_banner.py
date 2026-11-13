from common import *
from theme import *
from pixfont import text_px
P=parts(); Q=place(P,{}); Q={k:v for k,v in Q.items()}
Q['cyd_scr']=(Q['cyd_scr'][0],(0.15,0.16,0.15))
R=cam(-32,16)
body,proj,bb,sc,c=draw(Q,R,900,900,fill=real_fill,sw=(0.9,1.7))
x0,y0,x1,y1=bb
sD=410/(y1-y0)
dev=f'<g transform="translate({1530-x1*sD:.1f},{455-y1*sD:.1f}) scale({sD:.4f})">{body}</g>'
# pixel logo
pts,w=text_px('YELLOWBOY'); px=15
def logo(dx,dy,col):
    return ''.join(f'<rect x="{dx+x*px}" y="{dy+y*px}" width="{px}" height="{px}" fill="{col}"/>' for x,y in pts)
L=logo(80,132,CLAY)+logo(74,126,INK)
# highlight row
chips=['ESP32 · 240 MHz','ILI9341 320×240','I²C controller','DAC audio','Li-ion · USB-C','Game Boy emulator']
cx=78; ch=''
for t in chips:
    w_=len(t)*9.6+30
    ch+=f'<rect x="{cx}" y="340" width="{w_:.0f}" height="36" rx="18" fill="none" stroke="{RULE}" stroke-width="1.5"/><text x="{cx+w_/2:.0f}" y="363" font-family="{MONO}" font-size="14" fill="{SLATE}" text-anchor="middle">{t}</text>'
    cx+=w_+12
    if cx>900: break
scan='<pattern id="scan" width="4" height="4" patternUnits="userSpaceOnUse"><rect width="4" height="2" fill="#ffffff" opacity=".018"/></pattern>'
glow='<radialGradient id="glow" cx=".78" cy=".5" r=".55"><stop offset="0" stop-color="#ffb02e" stop-opacity=".22"/><stop offset="1" stop-color="#ffb02e" stop-opacity="0"/></radialGradient>'
W,H=1600,500
svg=(f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 {W} {H}" width="{W}" height="{H}"><defs>{scan}{glow}</defs>'
     f'<rect width="{W}" height="{H}" rx="32" fill="{CLOUD}"/>'
     f'{L}<text x="76" y="286" font-family="{SERIF}" font-size="34" fill="{INK}">An open-source handheld console for the ESP32 CYD</text>'
     f'<text x="78" y="320" font-family="{SANS}" font-size="18" fill="{SLATE}">Cheap Yellow Display · 3D-printed shell · no custom PCB · runs Game Boy games</text>'
     f'{ch}<text x="78" y="440" font-family="{MONO}" font-size="13" letter-spacing="3" fill="{MUTE}">OPEN SOURCE HARDWARE + FIRMWARE · MIT</text>'
     f'<g fill="none" stroke-linecap="round" stroke-linejoin="round">{dev}</g></svg>')
open('out/banner.svg','w').write(svg); print(len(svg)//1024,'KB', bb)
