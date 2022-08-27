#!/usr/bin/python
# -*- coding: utf-8 -*-


from view_train_list import *

date = re.sub(
    r'(\d\d)(\d\d)-(\d+)-(\d+)',
    r"\1\2\3\4",
    nowdate()
)

ccrgt = readcsv('emu/ccrgt%s.csv'%(date))
equip = readcsv('emu/equip%s.csv'%(date))
bureau = readcsv('emu/bureau%s.csv'%(date))

maxlen = 90000
ccrgtmap = [[] for i in range(maxlen)]
equipmap = [[] for i in range(maxlen)]
bureaumap = [[] for i in range(maxlen)]

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
    bureaumap[hash_no(row[0])] = row


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
    c = ccrgtmap[key]
    e = equipmap[key]
    b = bureaumap[key]
    if (len(c) == 0) and (len(e) == 0):
        if len(b) > 1:
            row = [b[0],b[1]]
            ret.append(row)
            continue
        #print(key,len(c),len(e))
        continue
    #print(key,len(c),len(e))
    c.extend(["" for i in range(6-len(c))])
    e.extend(["" for i in range(9-len(e))])
    row = []
    row.append(c[0])
    #row.append(e[0])
    bu = bureau_map.get(c[3],c[3]) #c[2]
    #if len(bu) and len(e[3]) and bu != e[3]:
        #print(','.join([','.join(c),','.join(e)]))
    row.append(e[3] if e[3] else bu)
    emu_no = (u'2*' if u'重' in c[1] else '') + (e[2] if e[2] else (c[1].replace(u'型','').replace(u'重联','')))
    row.append(emu_no.replace(u'CRH380','').replace(u'CRH','').replace(u'CR400','').replace(u'CR300','300'))
    row.extend([e[i] for i in [4,5]])
    row.extend([c[i] for i in [4,5]])
    #row.extend([e[i] for i in [6,7,8]])
    ret.append(row)


writecsv(
    'emu/emu%s.csv'%(date),
    [[x.encode('utf-8') for x in row] for row in ret]
)


'''
for row in ret:
    if len(row[2]) and len(row[3]) and row[3] not in row[2]:
        print(','.join(row))
'''


#[c[i] for i in [0,1,2,3,4,5]]
#[e[i] for i in [0,1,2,3,4,5,6,7,8]]

