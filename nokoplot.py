#! /usr/bin/Python3

from PIL import Image, ImageFont, ImageDraw  
import serial,time,sys,math,os,datetime,glob,atexit,readchar
from nokosh import sh

MAX_X=42700
MAX_Y=33300


ser = serial.Serial()

while True:
    ser.port = "/dev/ttyACM0"
    try: ser.open() ; break
    except:
        ser.port = "/dev/ttyACM1"
        try: ser.open() ; break
        except:
            print('EI PORTTIA')
            time.sleep(1)

ser.baudrate = 9600
ser.timeout = 0.1
ser.xonoff = True
ser.write(b'R\r')

def save_status():
    f=open('STATUS.py','w')
    f.write('X_NOW='+str(X_NOW)+';Y_NOW='+str(Y_NOW))
    f.close()
            
X_NOW=0
Y_NOW=20000
if not os.path.exists('STATUS.py'): save_status()
from STATUS import *
st=os.stat('STATUS.py')
age=int(time.time()-st.st_mtime)
print('Welcome back after',age,'seconds')
if  age > 3*3600 and (X_NOW != 0 or Y_NOW != MAX_Y):
    print('*** TOO OLD STATUS :',X_NOW,Y_NOW) 
    print('    Move Manually:')
    X_NOW=0
    Y_NOW=MAX_Y
    save_status()
print('*** STATUS:',X_NOW,',',Y_NOW)
print(glob.glob('*.png'))
print(glob.glob('*.jpg'))


def query_motors():
    ser.read(20)
    ser.write(b'QM\r')
    return ser.read(10)

def wait_when_busy():
    any=False
    while query_motors() != b'QM,0,0,0\n\r':
        any=True
        print('.',end='')
    if any: print()

def Free(x=True):
    wait_when_busy()
    if x:
        ser.write(b'EM,0,0\r')
    else:
        ser.write(b'EM,1,1\r')
Free(True)
    

MOVES=0        
        
def Stepper_Move(duration,Steps1,Steps2):
    global MOVES
    MOVES+=1
    if MOVES>10:
        wait_when_busy()
        MOVES=0
    duration,Steps1,Steps2=(str(int(duration)),str(int(Steps1)),str(int(Steps2)))
    ser.write(bytes("SM,{},{},{}\r".format(duration,Steps1,Steps2),encoding='UTF-8'))

def sign(x):
    if x<0: return -1
    if x>0: return 1
    else: return 0

def smooth(duration,x,y):
    Stepper_Move(duration,x+y,x-y)
        
Klappispeed=100        
Klappikorjaus=0 # 100
Klappikorjaukset=0  # Piirturissa on x-suunnassa klappia
vanhempisuunta=0
vanhasuunta=0
PEN_SPEED=2

def Move_Rel(x,y):
    global vanhasuunta,Klappikorjaukset,X_NOW,vanhempisuunta
#    x=round(x*20/20.7)
#    y=round(y*20/20.7)
    duration=int((abs(x)+abs(y))/PEN_SPEED)
    if PEN_UP: duration=int(duration/4)
    if duration<100: duration=100
    if  sign(x)!=sign(vanhasuunta) and (not PEN_UP):
        if vanhasuunta!=0 or sign(vanhempisuunta)!=sign(x):
            z=sign(x)*Klappikorjaus
            Stepper_Move(Klappispeed,z,z)
            Klappikorjaukset+=z
    smooth(duration,x,y)
    vanhempisuunta=vanhasuunta
    vanhasuunta=x

def Move(x,y):
    global X_NOW,Y_NOW
    if x<MAX_X and y<MAX_Y and x>-1 and y>-1:
        Move_Rel(x-X_NOW,y-Y_NOW)
        X_NOW=x
        Y_NOW=y
    else:
        print('Yli rajan',x,y)
    save_status()

PEN_UP=True
def Pen(x='UP'):
    global PEN_UP,Klappikorjaukset,X_NOW
    ser.write(b'SC,1,1\r')
    ser.write(b'SC,4,10000\r')
    ser.write(b'SC,5,20000\r')
    if x=='UP':
        X_NOW+=Klappikorjaukset
        Klappikorjaukset=0
        Move(X_NOW,Y_NOW)
        PEN_UP=True
#        ser.write(b'SP,1,800\r')
        ser.write(b'SP,1,400\r')
    if x=='DOWN':
        wait_when_busy()
        MOVES=0
        PEN_UP=False
        ser.write(b'SP,0,500\r')
    if type(x)==type(1): # Numeerinen kynän asento 0-100
        wait_when_busy()
        ser.write(bytes("SC,4,{}\r".format(int(10000+(100-x)*100)),encoding='UTF-8'))
        PEN_UP=False
        ser.write(b'SP,1,500\r')
        
def bye():
    Pen('UP')
    Move(0,0)
    wait_when_busy()
    save_status()
    Free(True)
    sys.exit()

def lepo():
    Pen('UP')
    Move(0,MAX_Y-1)
    wait_when_busy()
    save_status()
    Free(True)
    sys.exit()

def vapaus():
    Pen('UP')
    wait_when_busy()
    save_status()
    Free(True)
    print('*** STATUS:',X_NOW,',',Y_NOW)
    sys.exit()

atexit.register(vapaus)

    
def ruudukko(kpl,koko):
    for x in range(kpl):
        Move(0,0)
        Move(x*koko,0)
        Pen('DOWN')
        Move(x*koko,kpl*koko)
        Pen('UP')
        Move(0,x*koko)
        Pen('DOWN')
        Move(kpl*koko,x*koko)
        Pen('UP')

def Frame(x,y):
    Move(0,0)
    Pen('DOWN')
    Move(x,0)
    Move(x,y)
    Move(0,y)
    Move(0,0)
    Pen('UP')

def plot2(img,x,y,h,vali,musta):
    p=img.getpixel((x,h-y-1))
    if type(p)==type(1): v=p
    else: v=(p[0]+p[1]+p[2])/3
    if v<musta:
        if PEN_UP:
            Move(x*vali,y*vali)
            Pen('DOWN')
    else:
        if not PEN_UP:
            Move(x*vali,y*vali)
            Pen('UP')

def plot3(x,y,vali):
    if not PEN_UP:
        Move(x*vali,y*vali)
        Pen('UP')

def plot_image(i,w=0,h=0,vali=100,musta=130,kehys=False,hori=False,odota=True): # milli on 100
    Pen('UP')
    Move(0,0)
    Free(True)
    if type(i) == type('string'): img=Image.open(i)
    else: img=i
    if w>0:
        if h>0:
            img=img.resize((w,h))
        else:
            s=img.size
            h=int(s[1]/(s[0]/w))
            img=img.resize((w,h))
    else:
        s=img.size
        w=s[0]
        h=s[1]
    print('New Size:',w,h," cm:",w*vali/1000,h*vali/1000," väli mm:",vali/100.)
    if odota:
        img.show()
        input('Enter to continue')
    if kehys: Frame(w*vali,h*vali)
    if hori:
        for y in range(h):
            for x in range(w): plot2(img,x,y,h,vali,musta)
            plot3(x,y,vali)
    else:
        for x in range(w):
            for y in range(h): plot2(img,x,y,h,vali,musta)
            plot3(x,y,vali)
    Move(0,0)
    Free(True)
 

def plot_circle(xo=10000,yo=10000,r=3000,start=0,end=360,step=10):
    if start>end: step=-step
    for a in range(start,end+step,step):
         x=int(r*math.cos(math.radians(a)))
         y=int(r*math.sin(math.radians(a)))
         Move(xo+x,yo+y)
         if a==start: Pen('DOWN')
    Pen('UP')

def big_circle():
    plot_circle(xo=MAX_Y/2,yo=MAX_Y/2,r=MAX_Y/2-1)

def banneri(text,w,h=50,vali=100):
    l=len(text)
    image = Image.new(mode="RGB",size=(int(l*h/1.5),int(h*1.1)),color="white")  
    draw = ImageDraw.Draw(image)  
    font = ImageFont.truetype('/usr/share/fonts/CreteRound-Regular.ttf',h)  
    draw.text((10,-int(h/5)), text, font = font, fill='black', align ="left")  
    plot_image(image,w,hori=True,vali=vali)

    
def A0(): Move(0,0); wait_when_busy(); Free()
def A3(): Move(42000,29700); wait_when_busy(); Free()
def A4(): Move(29700,21000); wait_when_busy(); Free()
def A5(): Move(21000,14800); wait_when_busy(); Free()

def saato():
    global X_NOW,Y_NOW
    prev=""
    while True:
        Free(True)
        print(X_NOW,Y_NOW)
        k=readchar.readkey()
        if k==prev:
            steppi=int(steppi*2)
            steppi=steppi%5000
        else: steppi=50
        if k=='\x1b[A': Move(X_NOW,Y_NOW+steppi)
        if k=='\x1b[B': Move(X_NOW,Y_NOW-steppi)
        if k=='\x1b[C': Move(X_NOW+steppi,Y_NOW)
        if k=='\x1b[D': Move(X_NOW-steppi,Y_NOW)
        if k=='\x1b[5~': Pen('UP')
        if k=='\x1b[6~': Pen('DOWN')
        if k=='l': lepo()
        if k=='0': Move(0,0)
        if k=='m': lepo()
        if k=='3': A3()
        if k=='4': A4()
        if k=='5': A5()
        if k=='z': X_NOW=0;Y_NOW=0
        if k=='f': Move(0,0);Move(0,MAX_Y-1);Move(MAX_X-1,MAX_Y-1);Move(MAX_X-1,0);\
                   Move(0,0);Move(MAX_X-1,0);Move(MAX_X-1,MAX_Y-1);Move(0,MAX_Y-1);\
                   Move(0,0);Move(MAX_X-1,MAX_Y-1);Move(0,0);
        if k=='\x04': break
        if k=='q': break
        if k=='\x1b\x1b': break
        prev=k
        wait_when_busy()

def hiiri():
    import mouse
    Move(20000,10000)
    mouse.move(1800,1125)
    nolla= mouse.get_position()
    speed=10
    while True:
        nyt=mouse.get_position()
        Move(X_NOW-speed*(nyt[0]-nolla[0]),Y_NOW+speed*(nyt[1]-nolla[1]))
        wait_when_busy()
        mouse.move(1800,1125)
        nolla= mouse.get_position()
        time.sleep(0.1)
        

def cmyk(i,w):
    global X_NOW,Y_NOW
    sh('convert2cmyk '+i)
    for f in 'ycmk':
        input('Vaihda Kyna '+f)
        hori=False
        for m in (70,120,200):
            plot_image(f+'.jpg',w=w,musta=m,odota=False,vali=100,hori=hori)
            hori= not hori
            Move(25,0)
            X_NOW=0
        X_NOW=75
        Move(0,0)
