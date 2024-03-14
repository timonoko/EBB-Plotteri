#! /usr/bin(/Python3

from PIL import Image

import serial,time,sys
ser = serial.Serial()
ser.port = "/dev/ttyACM0"

try: ser.open()
except:
    ser.port = "/dev/ttyACM1"
    try: ser.open()
    except:
        print('EI PORTTIA')
        sys.exit()
        
ser.baudrate = 9600
ser.timeout = 0.1
ser.xonoff = True

ser.write(b'R\r')

def save_status():
    f=open('STATUS.py','w')
    f.write('X_NOW='+str(X_NOW)+';Y_NOW='+str(Y_NOW))
    f.close()

def query_motors():
    ser.read(20)
    ser.write(b'QM\r')
    return ser.read(10)

def wait_when_busy():
    while query_motors() != b'QM,0,0,0\n\r': pass

def Stepper_Move(duration,Steps1,Steps2):
    wait_when_busy()
    duration,Steps1,Steps2=(str(duration),str(Steps1),str(Steps2))
    ser.write(bytes("SM,{},{},{}\r".format(duration,Steps1,Steps2),encoding='UTF-8'))

PEN_SPEED=2    
def Move_Rel(x,y):
    duration=int((abs(x)+abs(y))/PEN_SPEED)
    if PEN_UP: duration=int(duration/(6/PEN_SPEED))
    Stepper_Move(duration,x-y,x+y)

def Move(x,y):
    global X_NOW,Y_NOW
    if x<42801 and y<31700 and x>-1 and y>-1:
        Move_Rel(x-X_NOW,y-Y_NOW)
        X_NOW=x
        Y_NOW=y
    else:
        print('Yli rajan',x,y)
    save_status()

PEN_UP=True
def Pen(x='UP'):
    global PEN_UP
    if x=='UP':
        PEN_UP=True
        ser.write(b'SP,1,200\r')
    else:
        PEN_UP=False
        ser.write(b'SP,0,200\r')

def Free(x):
    if x:
        ser.write(b'EM,0,0\r')
    else:
        ser.write(b'EM,1,1\r')
              
def bye():
    Pen('UP')
    Move(0,0)
    wait_when_busy()
    save_status()
    Free(True)
    sys.exit()

def lepo():
    Pen('UP')
    Move(0,20000)
    wait_when_busy()
    save_status()
    Free(True)
    sys.exit()

    
#init
X_NOW=0
Y_NOW=0
Free(False)
Pen('DOWN');time.sleep(1);Pen('UP')
from STATUS import *
print('**** STATUS:',X_NOW,',',Y_NOW,' ****')

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

def Origin_here():X_NOW=0;Y_NOW=0
     
        
def Frame(x,y):
    Move(0,0)
    Pen('DOWN')
    Move(x,0)
    Move(x,y)
    Move(0,y)
    Move(0,0)
    Pen('UP')

def plot_image(i,w=0,h=0,vali=100,musta=130,kehys=True,edestakas=False): # milli on 100
    Pen('UP')
    Move(0,0)
    img=Image.open(i)
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
    print('New Size:',w,',',h," mm:",w*vali/100,',',h*vali/100)
    img.show()
    input('Enter to continue')
    if kehys: Frame(w*vali,h*vali)
    for x in range(w):
        Pen('UP')
        print('x=',x)
        for z in range(h):
            y=h-z-1
            if edestakas and x%2==1: y=z
            p=img.getpixel((x,h-y-1))
            v=(p[0]+p[1]+p[2])/3
            if p[0]<musta:
                if PEN_UP:
                    Move(x*vali,y*vali)
                    Pen('DOWN')
            else:
                if not PEN_UP:
                    Move(x*vali,y*vali)
                    Pen('UP')
        if not PEN_UP:
            Move(x*vali,y*vali)
            Pen('UP')
    Move(0,0)
