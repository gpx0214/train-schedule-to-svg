#!/usr/bin/python
# -*- coding: utf-8 -*-


from view_train_list import *


try:
    date = sys.argv[1]
except:
    date = nowdate()


yyyymmdd = re.sub(
    r'(\d\d)(\d\d)-(\d+)-(\d+)',
    r"\1\2\3\4",
    date
)

ccrgt = readcsv('emu/ccrgt%s.csv'%(yyyymmdd))
equip = readcsv('emu/equip%s.csv'%(yyyymmdd))
bureau = readcsv('emu/bureau%s.csv'%(yyyymmdd))
carcode = readcsv('emu/carcode%s.csv'%(yyyymmdd))
trainset = readcsv('emu/trainset%s.csv'%(yyyymmdd))

maxlen = 90000
ccrgtmap = [[] for i in range(maxlen)]
equipmap = [[] for i in range(maxlen)]
bureaumap = [[] for i in range(maxlen)]
carcodemap = [[] for i in range(maxlen)]
trainsetmap = [[] for i in range(maxlen)]

for row in ccrgt:
    if not len(row[0]):
        continue
    #if row[2] != row[3]:
        #if platform.system() == "Windows":
            #print(','.join(row).encode('gbk'))
        #else:
            #print(','.join(row).encode('utf-8'))
    ccrgtmap[hash_no(row[0])] = row

for row in equip:
    if not len(row[0]):
        continue
    equipmap[hash_no(re.sub(r'^0+', "", row[0][2:10]))] = row

for row in bureau:
    if not len(row[0]):
        continue
    key = hash_no(row[0])
    if key < 0 or key >= len(bureaumap):
        continue
    bureaumap[hash_no(row[0])] = row

for row in carcode:
    if not len(row[0]):
        continue
    key = hash_no(row[0])
    if key < 0 or key >= len(carcodemap):
        continue
    carcodemap[hash_no(row[0])] = row

for row in trainset:
    if not len(row[0]):
        continue
    key = hash_no(row[0].split('/')[0])
    if key < 0 or key >= len(trainsetmap):
        continue
    trainsetmap[key] = row


bureaustr = u'''哈尔滨,哈
沈阳,沈
北京,京
呼和浩特,呼
郑州,郑
济南,济
上海,上
南昌,南
广州,广
南宁,宁
成都,成
昆明,昆
兰州,兰
乌鲁木齐,乌
西宁,青
太原,太
武汉,武
西安,西'''
bureau_map = dict([x.split(',') for x in bureaustr.split('\n')])

ret = []
for key in range(0,maxlen):
    c = ccrgtmap[key] #221226 插入下标2 车号
    e = equipmap[key]
    b = bureaumap[key]
    a = carcodemap[key]
    t = trainsetmap[key]
    if (len(c) == 0) and (len(e) == 0) and (len(a) == 0) and (len(t) == 0):
        if len(b) > 1:
            row = [b[0],b[1]]
            ret.append(row)
            continue
        #print(key,len(c),len(e),len(a))
        continue
    #print(key,len(c),len(e),len(b),len(a))
    c.extend(["" for i in range(7-len(c))])
    e.extend(["" for i in range(9-len(e))])
    b.extend(["" for i in range(2-len(b))])
    a.extend(["" for i in range(3-len(a))])
    t.extend(["" for i in range(8-len(t))])
    row = []
    row.append(c[0] if c[0] else a[0] if a[0] else b[0] if b[0] else t[0])
    #row.append(e[0])
    bu = bureau_map.get(c[4],c[4]) #c[3]
    if not bu and len(b)>1:
        bu = b[1]
    #if len(bu) and len(e[3]) and bu != e[3]:
        #print(','.join([','.join(c),','.join(e)]))
    row.append(e[3] if e[3] else bu)
    emu_no = (u'2*' if u'重' in (c[1] if c[1] else t[6]) else '') + (e[2] if e[2] else c[2] if c[2] else c[1] if c[1] else a[1] if a[1] else t[6] if t[6] else t[1])
    row.append(emu_no.replace(u'型','').replace(u'重联','').replace(u'CRH380','').replace(u'CRH','').replace(u'CR400','').replace(u'CR300','300').replace(u'CR200','200').replace(u'DC600V','-').replace(u'AC380V','~'))
    row.append(e[4])
    row.append(e[5])
    row.append(c[5])
    row.append(c[6] if c[6] else a[2])
    row.append(t[5])
    #row.extend([e[i] for i in [6,7,8]])
    ret.append(row)

writemincsv(
    'emu/emu%s.csv'%(yyyymmdd),
    [[x.encode('utf-8') for x in row] for row in ret]
)


'''
for row in ret:
    if len(row[2]) and len(row[3]) and row[3] not in row[2]:
        print(','.join(row))
'''


#[c[i] for i in [0,1,2,3,4,5]]
#[e[i] for i in [0,1,2,3,4,5,6,7,8]]

