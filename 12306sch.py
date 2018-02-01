!/usr/bin/python
#tested in python 2.7.14 on win10 x64
from __future__ import print_function
import os
import re
def getkm(str,station):
    for i in range(len(station)):
        if str==station[i][0]:
            return station[i][1]
    return -1

def getmin(str):
    try:
        a,b=str.split(':')[0:2]
        return int(a)*60+int(b)
    except:
        return -1

def getkms(str,station):
    a=re.findall(r'[^\x00-\x7f]+', str , re.I|re.M)
    for i in range(len(a)):
        a[i]=getkm(a[i],station)
    return a

def getmins(str):
    t=re.findall(r'[0-9]+:[0-9]+', str , re.I|re.M)
    for i in range(len(t)):
        t[i]=getmin(t[i])
    return t

fstat=open('station.txt')
source0=fstat.read()
station=source0.split('\n')

for i in range(len(station)):
    station[i]=station[i].split(' ')

len(station) #34

fsch=open('schedule.txt')
source=fsch.read()
sch=source.split('\n')
len(sch)

flag=0
x=0
y=0
def sync(str):
    nums=re.findall(r'(\b[GDCZTKYL]{1}[1-9][0-9]{0,3}|[1-9][0-9]{3})', str , re.I|re.M)
    kms=getkms(str,station)
    mins=getmins(str)
    #print('%s %s %s'%(nums,kms,mins))
    if len(nums):
        num=nums[0]
        flag=1
        print ('<polyline name="%s" class="G" style="fill:none;stroke:blue;stroke-width:1;opacity:0.8" points="'%(num),end='')
        return ('start %s'%(num))
    if len(kms):
        if kms[0]==-1:
            return ''
        else:
            y=kms[0]
    else:
        print('"/>')
        return('end')
        '''
        if flag>0:
            flag=0
            print('"/>')
            return 'end'
        else:
            print('')
            return ''
        '''
    for i in range(len(mins)):
        x=mins[i]
        print('%s,%s '%(x,y),end='')

print('<?xml version="1.0" standalone="no"?>')
print('<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" ')
print('"http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">')
print('<svg width="%s" height="%s" version="1.1"'%(1440,2450))
print('xmlns="http://www.w3.org/2000/svg">')

a=getkms(source0,station)
for i in range(len(a)):
    print('<line x1="0" y1="%s" x2="1440" y2="%s" style="stroke:rgb(220,220,220);stroke-width:1"/>'%(a[i],a[i]))

for i in range(24):
    print('<line x1="%d" y1="0" x2="%d" y2="3000" style="stroke:rgb(128,128,128);stroke-width:1"/>'%(i*60,i*60))
    print('<line x1="%d" y1="0" x2="%d" y2="3000" style="stroke:rgb(220,220,220);stroke-width:1"/>'%(i*60+30,i*60+30))

for i in range(len(sch)):
    sync(sch[i])

print('</svg>')

#os.system("pause")
