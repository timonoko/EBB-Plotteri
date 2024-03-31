#! /usr/bin/python3

"""
 This laserizes the "Path to Gcode" in Inkscape

 usage:
   fixInkscape filename laserpower laserspeed idlespeed

 Removes F(speed) and adds your own F
 Replaces Z-movement with M3 and M5
 Replaces G2 and G3 arcs with G1 lines
  -- just make impossible long arc radiuses in Inkscape.
"""

import time,sys

try:   F=open(sys.argv[1],'r')
except: F=open('gcode.gcode','r')

try: POWER=sys.argv[2]    
except: POWER=975
try: SPEED=sys.argv[3]    
except: SPEED=2400
try: FSPEED=sys.argv[4]    
except: FSPEED=2400
  
print(';Z removed, M3 and M5 added')
s=1
done=True
while s:
    s=F.readline()
    if s.find('F')>0:
        s=s.replace('F','; F')
    if s.find('I')>0:
        s=s.replace('I','; I')
    if s.find('J')>0:
        s=s.replace('J','; J')
    if s.find('Z')>0:
        if s[s.find('Z')+1]=='5':
            print('M5')
            print('G0F{}'.format(FSPEED))
            done=True
        elif done:
            done=False
            print("G1S{}F{}".format(POWER,SPEED))
            print('M3')
            print('M8')
        s=s.replace('Z5.000000','')
        s=s.replace('Z-0.125000','')
    s=s.replace('G02','G1')
    s=s.replace('G03','G1')
    s=s.replace('G2 ','G1 ')
    s=s.replace('G3 ','G1 ')
    print(s)

