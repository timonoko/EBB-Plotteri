#! /usr/bin/python3

"""
 Sends G-code file to EBB-plotter
   after fixInkscape.py - filtering
"""

import nokoplot as n
import time,os,sys

try:   f=open(sys.argv[1],'r')
except: f=open('gcode.gcode','r')

try:   X_OFFSET=int(sys.argv[2])
except: X_OFFSET=0

try:   Y_OFFSET=int(sys.argv[3])
except: Y_OFFSET=0


    
def parsee(s):
    i=0
    tulos={}
    number=""
    prevalfa="kakka"
    while i<len(s):
        if ord(s[i]) in range(ord('0'),ord('9')+1) or s[i]=='.' or s[i]=='-':
            number+=s[i]
        else:
            if prevalfa != "kakka" and number != "." and number != '' and number != '..':
                tulos.update({prevalfa:float(number)})
                number=""
            if ord(s[i]) in range(ord('A'),ord('Z')+1):
                prevalfa=s[i]
        i+=1
    return tulos


def vino_x(y): 
    return -y*100/30000

def Move2(s):
    y=int(s['Y']*100)
    print('n.Move',int(s['X']*100-vino_x(y))+X_OFFSET,y+Y_OFFSET)
    n.Move(int(s['X']*100-vino_x(y))+X_OFFSET,y+Y_OFFSET)

st=f.readline()
while st:
    st=f.readline()
    print(st[:-1])
    s=parsee(st)
    if 'G' in s:
        if s['G']==0:
            if 'X' in s: Move2(s) 
        elif s['G']==1:
            if 'X' in s: Move2(s) 
            if 'S' in s: pass #print('power',s['S'])
            if 'F' in s: pass #print('Speed',s['F'])
        elif s['G']==4:
            time.sleep(s['P'])
    elif 'M' in s:
        if s['M']==3:
            n.Pen('DOWN')
        if s['M']==4:
            n.Pen('DOWN')
        if s['M']==5:
            n.Pen('UP')
           
n.Move(0,0)
n.wait_when_busy()
n.Free()

