import numpy as np
from pixfont import text_px
PAL=np.array([[155,188,15],[139,172,15],[48,98,48],[15,56,15]])/255
def screen():
    g=np.zeros((144,160),int)
    # sky gradient dithering
    for y in range(144):
        for x in range(160):
            if y>96: g[y,x]=1
    # hills
    xs=np.arange(160)
    h1=(104+8*np.sin(xs/13)+5*np.sin(xs/5.3)).astype(int)
    h2=(116+6*np.sin(xs/9+1)+3*np.sin(xs/4)).astype(int)
    for x in range(160):
        g[h1[x]:,x]=2; g[h2[x]:,x]=3
    # sun
    yy,xx=np.mgrid[:144,:160]
    g[(xx-128)**2+(yy-30)**2<14**2]=1
    # clouds
    for cx,cy in((30,40),(80,26)):
        g[((xx-cx)/2.2)**2+(yy-cy)**2<20]=1
    # title box
    pts,w=text_px('YELLOWBOY'); s=2
    ox=(160-w*s)//2; oy=50
    g[oy-6:oy+7*s+6, ox-6:ox+w*s+6]=0
    g[oy-6,ox-6:ox+w*s+6]=3; g[oy+7*s+5,ox-6:ox+w*s+6]=3; g[oy-6:oy+7*s+6,ox-6]=3; g[oy-6:oy+7*s+6,ox+w*s+5]=3
    for px,py in pts: g[oy+py*s:oy+py*s+s, ox+px*s:ox+px*s+s]=3
    pts,w=text_px('PRESS START'); ox=(160-w)//2
    for px,py in pts: g[oy+28+py, ox+px]=3
    return PAL[g]
