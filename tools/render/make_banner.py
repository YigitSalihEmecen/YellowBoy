import base64,io,numpy as np
from PIL import Image
from common import *
from theme import *
from pixfont import text_px
from gbscreen import screen
P=parts(); Q=place(P,{}); Q={k:v for k,v in Q.items()}
R=cam(-24,10)
body,proj,bb,sc,c=draw(Q,R,900,900,fill=real_fill,sw=(0.9,1.7))
# screen image (pixel art) mapped by affine from 3 projected corners
g=(screen()*255).astype(np.uint8)
full=np.full((240,320,3),8,np.uint8)
gi=np.array(Image.fromarray(g).resize((266,240),Image.NEAREST)); full[:,27:293]=gi
buf=io.BytesIO(); Image.fromarray(full).save(buf,'PNG',optimize=True); b64=base64.b64encode(buf.getvalue()).decode()
z=-0.30
p00=proj(np.array([-4.4-29,-0.4+21.75,z]))[0]; p10=proj(np.array([-4.4+29,-0.4+21.75,z]))[0]; p01=proj(np.array([-4.4-29,-0.4-21.75,z]))[0]
a=(p10[0]-p00[0])/320; b=(p10[1]-p00[1])/320; c_=(p01[0]-p00[0])/240; d=(p01[1]-p00[1])/240
img=f'<image href="data:image/png;base64,{b64}" width="320" height="240" style="image-rendering:pixelated" preserveAspectRatio="none" transform="matrix({a:.5f} {b:.5f} {c_:.5f} {d:.5f} {p00[0]:.2f} {p00[1]:.2f})"/>'
# compute screen draw-order: draw device, then screen image clipped? screen sits recessed; bezel overlaps edges slightly -> draw image then redraw nothing (fine)
x0,y0,x1,y1=bb
sD=410/(y1-y0)
dev=f'<g transform="translate({1530-x1*sD:.1f},{455-y1*sD:.1f}) scale({sD:.4f})">{body}{img}</g>'
# pixel logo
pts,w=text_px('YELLOWBOY'); px=15
def logo(dx,dy,col):
    return ''.join(f'<rect x="{dx+x*px}" y="{dy+y*px}" width="{px}" height="{px}" fill="{col}"/>' for x,y in pts)
L=logo(80,132,CLAY)+logo(74,126,INK)
# highlight row
chips=['ESP32 · 240 MHz','No PSRAM','ILI9341 320×240','I²C controller','DAC audio','µSD ROMs']
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
     f'{L}<text x="76" y="286" font-family="{SERIF}" font-size="34" fill="{INK}">A pocket Game Boy emulator for the ESP32 Cheap Yellow Display</text>'
     f'<text x="78" y="320" font-family="{SANS}" font-size="18" fill="{SLATE}">3D-printed shell · custom I²C controller · true analog audio · ~€32 in parts</text>'
     f'{ch}<text x="78" y="440" font-family="{MONO}" font-size="13" letter-spacing="3" fill="{MUTE}">OPEN SOURCE HARDWARE + FIRMWARE · MIT</text>'
     f'<g fill="none" stroke-linecap="round" stroke-linejoin="round">{dev}</g></svg>')
open('out/banner.svg','w').write(svg); print(len(svg)//1024,'KB', bb)
