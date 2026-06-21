# -*- coding: utf-8 -*-
from PIL import Image, ImageDraw, ImageFont
W,H=1200,630
img=Image.new("RGB",(W,H),(17,30,52))
d=ImageDraw.Draw(img,"RGBA")
top=(18,32,54); bot=(11,22,40)
for y in range(H):
    t=y/H
    d.line([(0,y),(W,y)],fill=(int(top[0]+(bot[0]-top[0])*t),int(top[1]+(bot[1]-top[1])*t),int(top[2]+(bot[2]-top[2])*t)))
for gx in range(80,W,60):
    for gy in range(60,H,60):
        d.ellipse([gx-1,gy-1,gx+1,gy+1],fill=(255,255,255,8))
def F(path,size):
    try: return ImageFont.truetype(path,size)
    except: return ImageFont.load_default()
geo=lambda s:F("C:/Windows/Fonts/georgiab.ttf",s)
seg=lambda s:F("C:/Windows/Fonts/segoeui.ttf",s)
segb=lambda s:F("C:/Windows/Fonts/segoeuib.ttf",s)
mono=lambda s:F("C:/Windows/Fonts/consola.ttf",s)
d.rectangle([0,0,12,H],fill=(192,85,43))
pts=[(720,470),(800,440),(860,455),(930,400),(1000,415),(1070,360),(1140,330)]
d.line(pts,fill=(192,85,43,90),width=4,joint="curve")
for p in pts: d.ellipse([p[0]-4,p[1]-4,p[0]+4,p[1]+4],fill=(192,85,43,150))
d.text((80,84),"MAKROMODELL-APPARATET  ·  INTERAKTIVT DASHBORD",font=mono(22),fill=(224,150,111))
d.text((78,140),"Norske makroøkonomiske",font=geo(62),fill=(255,255,255))
d.text((78,212),"modeller — på ett sted",font=geo(62),fill=(255,255,255))
d.text((80,310),"Apparat · kritikk · data · skatt · produktivitet · interaktiv simulator",font=seg(27),fill=(174,191,214))
d.text((80,348),"8 faner — verifisert mot SSB, Norges Bank, NBIM og OECD (2026)",font=seg(23),fill=(140,155,180))
d.line([(80,408),(1120,408)],fill=(255,255,255,30),width=1)
chips=[("Makroøkonometri",(58,74,140)),("DSGE",(31,111,107)),("CGE",(154,123,31)),("Mikrosimulering",(192,85,43))]
x=80
for name,col in chips:
    d.rounded_rectangle([x,440,x+18,458],4,fill=col)
    tw=d.textlength(name,font=segb(22))
    d.text((x+28,438),name,font=segb(22),fill=(210,218,228))
    x+=28+tw+34
d.text((80,520),"KVARTS · MODAG · NEMO · NORA · SNOW · DEMEC · MOSART · LOTTE",font=mono(20),fill=(127,168,216))
d.text((80,566),"Oljefond 21 286 mrd  ·  styringsrente 4,25 %  ·  Fastlands-BNP +1,7 %",font=mono(19),fill=(120,135,160))
img.save("og.png","PNG")
print("OG written", img.size)
