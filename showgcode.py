#! /usr/bin/python3
from PIL import Image, ImageFont, ImageDraw, ImageOps  
import time,sys,math,os,datetime

os.system('killall display')

IMG=Image.new(mode="RGB",size=(10000,10000),color=(0xe5,0xd5,0xa4))

def parsee(s):
    i=0
    tulos={}
    number=""
    prevalfa="kakka"
    while i<len(s):
        if s[i]=="(": break
        elif ord(s[i]) in range(ord('0'),ord('9')+1) or s[i]=='.':
            number+=s[i]
        else:
            if prevalfa != "kakka" and number != "":
                tulos.update({prevalfa:float(number)})
                number=""
            if ord(s[i]) in range(ord('A'),ord('Z')+1):
                prevalfa=s[i]
        i+=1
    return tulos

MAX_X=0
MAX_Y=0
PREV_X=0
PREV_Y=0
PEN_DOWN=False

def mydraw(x1,y1,x2,y2,color=(0,0,0)):
    if abs(x2-x1)>abs(y2-y1):
        if x1>x2:
            x1,x2=x2,x1
            y1,y2=y2,y1
        for x in range(x1,x2):
            IMG.putpixel((x,int(y1+(x-x1)*((y2-y1)/(x2-x1)))),color)
    else:
        if y1>y2:
            x1,x2=x2,x1
            y1,y2=y2,y1
        for y in range(y1,y2):
            IMG.putpixel((int(x1+(y-y1)*((x2-x1)/(y2-y1))),y),color)
    IMG.putpixel((x2,y2),(0,0,0))

def Move2(s):
    global IMG,MAX_X,MAX_Y,PREV_X,PREV_Y
    try: x=int(10*s['X'])
    except: x=PREV_X
    try: y=int(10*s['Y'])
    except: y=PREV_Y
    if x>MAX_X: MAX_X=x
    if y>MAX_Y: MAX_Y=y
    if PEN_DOWN:
        mydraw(PREV_X,PREV_Y,x,y)
    PREV_X=x
    PREV_Y=y

try:   F=open(sys.argv[1],'r')
except: F=open('gcode.gcode','r')

k=F.readline()
while k:
    k=F.readline()
    print(k)
    s=parsee(k)
    if 'G' in s:
        if s['G']==0:
            Move2(s)
            if 'Z' in s and s['Z']>1:
                PEN_DOWN=False
        elif s['G']<4:
            if 'Z' in s and s['Z']<1:
                PEN_DOWN=True
            Move2(s) 
            if 'S' in s: pass #print('power',s['S'])
            if 'F' in s: pass #print('Speed',s['F'])
        elif s['G']==4:
            print('täällä on pauseja')
            time.sleep(s['P'])
    elif 'M' in s:
        if s['M']==3:
            PEN_DOWN=True
        if s['M']==4:
            PEN_DOWN=True
        if s['M']==5:
            PEN_DOWN=False
           
IMG=IMG.crop((0,0,MAX_X+10,MAX_Y+10))

for x in range(0,MAX_X,100):
    mydraw(x,0,x,int(MAX_X/40),(255,0,0))
    if x%1000==0: mydraw(x,0,x,MAX_Y,(255,0,0))
for y in range(0,MAX_Y,100):
    mydraw(0,y,int(MAX_Y/40),y,(255,0,0))
    if y%1000==0: mydraw(0,y,MAX_X,y,(255,0,0))

IMG=ImageOps.flip(IMG)
if IMG.size[0] >1600: IMG=IMG.resize((1600,int(1600./MAX_X*MAX_Y)))
if IMG.size[1] >1000: IMG=IMG.resize((int(1000./MAX_Y*MAX_X),1000))
IMG.show()
print('MAX',MAX_X,MAX_Y)
print(IMG.size)
