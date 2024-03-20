from nokoplot import *

f=open('gcode.gcode','r')
def parsee(s):
    i=0
    tulos={}
    number=""
    prevalfa="kakka"
    while i<len(s):
        if ord(s[i]) in range(ord('0'),ord('9')+1) or s[i]=='.':
            number+=s[i]
        else:
            if prevalfa != "kakka" and number != "":
                tulos.update({prevalfa:eval(number)})
                number=""
            if ord(s[i]) in range(ord('A'),ord('Z')+1):
                prevalfa=s[i]
        i+=1
    return tulos

def Move2(s):
    Move(int(s['X']*100),int(s['Y']*100))

while True:
    s=f.readline()
    print(s[:-1])
    s=parsee(s)
    if 'G' in s:
        if s['G']==0:
            if 'X' in s: Move2(s) 
        elif s['G']==1:
            if 'X' in s: Move2(s) 
            if 'S' in s: pass #print('power',s['S'])
            if 'F' in s: pass #print('Speed',s['F'])
    elif 'M' in s:
        if s['M']==3:
            Pen('DOWN')
        if s['M']==5:
            Pen('UP')
           
            
