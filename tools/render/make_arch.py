from comp import T, MONO, SANS
from theme import *
W,H=1800,860
BG=IVORY; TX=INK; K='#FFFFFF'
Y=CLAY; G='#5E8C6A'; B='#4A6FA5'; P='#6E5C93'; R=SLATE
o=[]
def box(x,y,w,h,title,lines=(),col=Y,fill='#FFFFFF',tsize=19):
    s=f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="12" fill="{fill}" stroke="{RULE}" stroke-width="1.5"/>'
    s+=f'<circle cx="{x+24}" cy="{y+25}" r="5" fill="{col}"/>'
    s+=T(x+38,y+31,title,tsize,TX,'start',500,SERIF)
    for i,l in enumerate(lines): s+=T(x+22,y+54+i*21,l,13.5,MUTE,'start',500,SANS)
    o.append(s)
def lane(x,y,w,h,title,col):
    o.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="20" fill="{CLOUD}" stroke="none"/>'
             +T(x+24,y+34,title,12.5,MUTE,'start',600,MONO))
def arr(pts,col,label=None,lp=None,dash=False):
    d='M'+'L'.join(f'{x} {y}' for x,y in pts)
    (x0,y0),(x1,y1)=pts[-2],pts[-1]
    import math; a=math.atan2(y1-y0,x1-x0)
    hx,hy=x1-12*math.cos(a),y1-12*math.sin(a)
    head=f'M{x1} {y1}L{hx-6*math.sin(a):.1f} {hy+6*math.cos(a):.1f}L{hx+6*math.sin(a):.1f} {hy-6*math.cos(a):.1f}Z'
    da=' stroke-dasharray="6 6"' if dash else ''
    s=f'<path d="{d}" stroke="{col}" stroke-width="1.8" fill="none" stroke-linejoin="round"{da}/><path d="{head}" fill="{col}"/>'
    if label:
        x,y=lp; tw=len(label)*7.6+18
        s+=f'<rect x="{x-tw/2:.0f}" y="{y-11}" width="{tw:.0f}" height="22" rx="11" fill="#FFFFFF" stroke="{col}" stroke-width="1"/>'+T(x,y+4.5,label,11.5,col,weight=600)
    o.append(s)
# lanes
lane(470,100,500,690,'CORE 1 · ARDUINO LOOP',Y)
lane(1010,100,420,690,'CORE 0 · FREERTOS TASKS',G)
# hardware left
box(40,150,370,120,'µSD card · VSPI',['FAT32 · /roms/gb · /roms/gbc','/saves/&lt;rom&gt;.sav (cart RAM)'],B)
box(40,330,370,120,'Flash “rom” partition',['2.6 MB · ROM copied once','header-compared, then mmap()’d'],B)
box(40,520,370,100,'NVS preferences',['palette · frame-skip · brightness','volume · button map'],B)
# core 1
box(500,160,440,150,'Launcher UI',['scans µSD, ROM list, settings','pause menu: resume · save · load','settings · quit'],Y)
box(500,370,440,190,'Peanut-GB core',['LR35902 CPU + PPU, DMG mode','ROM read straight from mapped flash','32 KB cart RAM · 20 palettes','frame-skip 0…n','lcd_draw_line() per scanline'],Y)
box(500,620,440,120,'minigb_apu',['4-channel APU register state','fork tuned for YellowBoy'],Y)
# core 0
box(1040,160,360,170,'render task · prio 3',['line queue (32 × 160 px)','nearest-scale 160×144 → 266×240','2 × 16-line DMA ping-pong'],G)
box(1040,390,360,130,'input task · prio 2',['polls PCF8574 every ~12 ms','START+SELECT → pause menu'],G)
box(1040,590,360,150,'audio task · prio 2',['APU → 32 768 Hz samples','LPF + DC high-pass, volume','8 KB ring buffer'],G)
# peripherals right
box(1470,160,300,170,'ILI9341 2.8″',['HSPI · 80 MHz · DMA','320×240, game at 266×240','backlight PWM · GPIO21'],R)
box(1470,390,300,130,'PCF8574T · I²C 0x20',['SDA GPIO22 · SCL GPIO27','8 buttons, active-low'],P)
box(1470,590,300,150,'Timer ISR → DAC',['hw timer @ 32 768 Hz','GPIO26 (DAC2) → amp','→ 8 Ω speaker'],R)
# arrows
arr([(410,210),(500,235)],B,'ROM list',(455,205))
arr([(225,270),(225,330)],B,'copy',(262,300))
arr([(410,390),(500,430)],B,'mmap',(455,395))
arr([(410,570),(450,570),(450,280),(500,280)],B,None,None,dash=True)
arr([(940,410),(1040,250)],Y,'scanlines',(990,330))
arr([(1400,245),(1470,245)],G)
arr([(1470,455),(1400,455)],P,'I²C',(1435,435))
arr([(1040,470),(940,470)],G,'joypad',(990,455))
arr([(940,690),(1040,690)],Y,'APU state',(990,675))
arr([(1040,630),(990,630),(990,540),(940,540)],G,'frame pacing',(990,585),dash=True)
arr([(1400,665),(1470,665)],G,'samples',(1435,645))
hdr=T(40,66,'Firmware architecture',32,TX,'start',500,SERIF)+T(W-40,64,'current firmware: the Game Boy port · dual-core · no PSRAM',14,MUTE,'end',500,SANS)
dots=''
svg=(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}"><defs>{dots}</defs>'
     f'<rect width="{W}" height="{H}" rx="28" fill="{BG}"/>{"".join(o)}{hdr}</svg>')
open('out/architecture.svg','w').write(svg)
