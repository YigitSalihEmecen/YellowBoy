from comp import *
from theme import *
CW,CH,G=420,400,20; COLS=4
BG=IVORY; CARD='#FFFFFF'; LINE=RULE; TX=INK; ACC=CLAY
cards=[
 ('CYD · ESP32-2432S028R','2.8″ ILI9341 320×240 · ESP32 · µSD','×1','', lambda cx,cy: cyd(cx-172,cy-100,4.0)[0]),
 ('PCF8574T I/O expander','8 GPIO over I²C · address 0x20','×1','', lambda cx,cy: pcf(cx-77,cy-70,7)[0]),
 ('Tact switch 6×6×7 mm','2-pin THT · one per direction / button','×8','', lambda cx,cy: ''.join(tact(cx+dx*62,cy-10+dy*62,6.5)[0] for dx,dy in((0,-1),(0,1),(-1,0),(1,0)))),
 ('Speaker 8 Ω · 0.5 W','Ø 23 mm · JST 1.25 lead','×1','', lambda cx,cy: speaker(cx,cy-5,6.2)[0]),
 ('Boost + charger module','3.7 V → 5 V 2 A · Type-C charging','×1','', lambda cx,cy: boost(cx-80,cy-70,7)[0]),
 ('13450 Li-ion cell','3.7 V · 650 mAh · 2.41 Wh','×1','', lambda cx,cy: battery(cx-150,cy-40,6.6)[0]),
 ('SS12F15 slide switch','SPDT · panel-mount ears · power','×1','', lambda cx,cy: slide(cx-70,cy-62,7)[0]),
 ('Hardware &amp; wiring','M3 / M2 screws · 28 AWG wire · heat-shrink','—','', None),
]
def misc(cx,cy):
    o=''
    for i,c in enumerate(['#B8432F','#2E2D2A','#C99A2E','#4A6FA5']):
        o+=f'<path d="M{cx-120} {cy-40+i*14}c60 0 40 70 110 70s50-60 120-60" stroke="none" stroke-width="10" fill="none" stroke-linecap="round"/>'
        o+=f'<path d="M{cx-120} {cy-40+i*14}c60 0 40 70 110 70s50-60 120-60" stroke="{c}" stroke-width="5" fill="none" stroke-linecap="round"/>'
    for i in range(3):
        x=cx-60+i*60; y=cy+52
        o+=f'<g filter="url(#sh)"><path d="M{x-14} {y}h28v-6q0-6-6-6h-16q-6 0-6 6z" fill="url(#gMetal)" stroke="#141413" stroke-width="1.2"/><rect x="{x-5}" y="{y}" width="10" height="34" fill="url(#gMetal)" stroke="#141413" stroke-width="1.2"/>'
        o+=''.join(f'<path d="M{x-5} {y+5+k*6}l10-3" stroke="#8e9298" stroke-width="1.5"/>' for k in range(5))+f'<path d="M{x-5} {y+34}l5 7 5-7z" fill="#a8acb2"/></g>'
    return o
rows=(len(cards)+COLS-1)//COLS
W=COLS*CW+(COLS+1)*G; H=rows*CH+(rows+1)*G+90
o=[f'<rect width="{W}" height="{H}" rx="28" fill="{BG}"/>',
   T(G+8,60,'Bill of materials',30,TX,'start',500,SERIF),
   T(W-G-8,58,'off-the-shelf modules · no custom PCB',15,MUTE,'end',500,SANS)]
for i,(name,spec,qty,_,fn) in enumerate(cards):
    c,r=i%COLS,i//COLS; x=G+c*(CW+G); y=90+G+r*(CH+G)
    o.append(f'<rect x="{x}" y="{y}" width="{CW}" height="{CH}" rx="20" fill="{CARD}" stroke="{LINE}"/>')
    o.append(f'<rect x="{x+16}" y="{y+16}" width="{CW-32}" height="{CH-120}" rx="12" fill="{CLOUD}"/>')
    cx,cy=x+CW/2,y+16+(CH-120)/2
    o.append(fn(cx,cy) if fn else misc(cx,cy))
    o.append(T(x+22,y+CH-64,name,20,TX,'start',500,SERIF))
    o.append(T(x+22,y+CH-40,spec,13.5,MUTE,'start',500,SANS))
    o.append(f'<rect x="{x+CW-86}" y="{y+CH-88}" width="64" height="30" rx="15" fill="none" stroke="{ACC}" stroke-width="1.5"/>'+T(x+CW-54,y+CH-67,qty,15,ACC,weight=600,font=SANS))
svg=f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}"><defs>{DEFS}</defs>{"".join(o)}</svg>'
open('out/components.svg','w').write(svg); print(W,H,len(svg)//1024,'KB')
