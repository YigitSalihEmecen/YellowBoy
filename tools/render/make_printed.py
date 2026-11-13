from common import *
from theme import *
from comp import T
from stl import load
import os
D=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','..','hardware','stl','')
cells=[('Shell.stl + Shell-Color.stl','Front shell',"×1 · white + black (colour mask)",{'shell':(load(D+'Shell.stl'),(.92,.90,.85)),'mask':(load(D+'Shell-Color.stl')+np.array([0,0,0.04]),(.13,.13,.14))},cam(-28,18)),
       ('cap.stl','Back cap','×1 · white',{'cap':(load(D+'cap.stl'),(.88,.86,.81))},rot(200,140)),
       ('d-pad.stl','Switch plate','×1 · black',{'plate':(load(D+'d-pad.stl'),(.25,.25,.26))},rot(20,-50)),
       ('button.stl','Cross button','×2 · olive',{'b':(load(D+'button.stl'),(.42,.47,.22))},rot(25,-48))]
CW,CH,G=560,500,24
W=4*CW+5*G; H=CH+2*G+90
o=[f'<rect width="{W}" height="{H}" rx="28" fill="{IVORY}"/>',T(G+6,62,'Printed parts',32,INK,'start',500,SERIF),
   T(W-G-6,62,'PLA · 0.2 mm layers · STLs in hardware/stl',14,MUTE,'end',400,SANS)]
from comp import T as TT
T=TT
for i,(fn,name,meta,Q,R) in enumerate(cells):
    x=G+i*(CW+G); y=90+G
    body,proj,bb,sc,c=draw(Q,R,CW,CH-130,fill=real_fill,sw=(0.9,1.6),pad=40)
    o.append(f'<rect x="{x}" y="{y}" width="{CW}" height="{CH}" rx="16" fill="#FFFFFF" stroke="{RULE}"/>')
    o.append(f'<g transform="translate({x},{y+10})" fill="none" stroke-linecap="round" stroke-linejoin="round">{body}</g>')
    o.append(TT(x+24,y+CH-78,name,22,INK,'start',500,SERIF)+TT(x+24,y+CH-50,meta,14,SLATE,'start',400,SANS)+TT(x+24,y+CH-24,fn,12.5,MUTE,'start',500,MONO))
svg=f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">{"".join(o)}</svg>'
open('out/printed-parts.svg','w').write(svg); print(len(svg)//1024,'KB')
