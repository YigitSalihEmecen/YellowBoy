import numpy as np, sys
from PIL import Image, ImageDraw, ImageFilter
from scene import parts, GROUPS
from svgkit import place
from rend import raster, cam, rot
from line import render_lines
from gbscreen import screen
def render(Q,R,W,H,fn,ss=2,pad=80,sc_tex=True):
    names=list(Q.keys())
    res,proj,img,idb,zb,scale,c=render_lines(Q,R,W*ss,H*ss,pad*ss)
    img=img.copy()
    if sc_tex and 'cyd_scr' in Q:
        i=names.index('cyd_scr'); ys,xs=np.where(idb==i)
        X=(xs+0.5-W*ss/2)/scale+c[0]; Y=(H*ss/2-ys-0.5)/scale+c[1]; Z=zb[ys,xs]
        M=np.stack([X,Y,Z],1)@R  # back to model
        u=(M[:,0]-(-4.4-29))/58; v=1-(M[:,1]-(-0.4-21.75))/43.5
        # 320x240 panel: game area 266 wide centered, black bars
        pu=u*320; inside=(pu>27)&(pu<293)
        gx=np.clip(((pu-27)/266*160).astype(int),0,159); gy=np.clip((v*144).astype(int),0,143)
        tex=screen(); col=np.where(inside[:,None],tex[gy,gx],0.03)
        img[ys,xs]=col
    rgb=(np.clip(img,0,1)*255).astype(np.uint8)
    a=((idb>=0)*255).astype(np.uint8)
    im=Image.fromarray(np.dstack([rgb,a]),'RGBA')
    d=ImageDraw.Draw(im)
    for n,segs in res.items():
        for x0,y0,x1,y1,k in segs:
            d.line([(x0,y0),(x1,y1)],fill=(24,24,26,255),width=int(ss*(1.6 if k else 0.9)+0.5))
    # shadow
    sh=Image.new('RGBA',im.size,(0,0,0,0)); al=Image.fromarray(a).filter(ImageFilter.GaussianBlur(18*ss))
    sh.putalpha(al.point(lambda v:int(v*0.35))); sh=sh.transform(sh.size,Image.AFFINE,(1,0,-14*ss,0,1,-22*ss))
    out=Image.alpha_composite(sh,im).resize((W,H),Image.LANCZOS)
    bb=out.getbbox(); out=out.crop((max(bb[0]-30,0),max(bb[1]-30,0),min(bb[2]+30,W),min(bb[3]+30,H)))
    out.save(fn,optimize=True); print(fn,out.size)
P=parts()
Q=place(P,{}); Q={k:v for k,v in Q.items()}
render(Q,cam(-28,16),1200,1200,'out/render-front.png')
Qb={k:v for k,v in Q.items() if k not in('cap',)}
render(Qb,rot(200,138),1400,1200,'out/render-inside.png',sc_tex=False)
