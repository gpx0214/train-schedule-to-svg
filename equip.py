#!/usr/bin/python
# -*- coding: utf-8 -*-

from view_train_list import *


yyyymmdd = re.sub(
    r'(\d\d)(\d\d)-(\d+)-(\d+)',
    r"\1\2\3\4",
    nowdate()
)


maxlen = 90000
train_map = [[] for i in range(maxlen)]
seq_map = [0 for i in range(maxlen)]

c = readcsv('js/train%s.csv'%(base_yymmdd()))
idx = 0
# for i in range(idx, len(c), 1):
for i in range(idx, len(c), 1):
    if len(c[i]) < 5:
        continue
    if len(c[i]) < 7:
        c[i].append('')
        c[i].append('')
    if c[i][3] not in c[i][0]:
        idx = i
        continue
    if is_a_day(c[i][6], yyyymmdd):
        train_map[hash_no(re.sub(r'^0+', '', c[i][0][5:-2]))].append(c[i])
        #print(c[i][0])


rows = []
for key in range(40000, 80000):  # range(len(train_map))
    if len(train_map[key]) == 0:
        continue
    for retry in range(3):
        row, ret = getequip(train_map[key][0][0], yyyymmdd)
        if ret >= 0:
            break
    rows.append(row)


'''
#local
import json
rows = []
for key in range(40000, 80000):  # range(len(train_map))
    if len(train_map[key]) == 0:
        continue
    no = train_map[key][0][0]
    date = yyyymmdd
    try:
        j = json.loads(readbyte('equip/equip_' + date + '_' + no + '.json'))
        ret = [
            j['data'][0]['trainsetType'], 
            j['data'][0]['trainsetName'], 
            j['data'][0]['bureaName'],
            j['data'][0]['deploydepotName'], 
            j['data'][0]['depotName'], 
            j['data'][0]['trainsetStatus'], 
            no,
            j['data'][0]['date'], 
            str(j['data'][0]['eId']), 
        ]
    except:
        print('equip %s no data' % (no))
        ret = [
            u'', 
            u'', 
            u'', 
            u'', 
            u'', 
            u'', 
            no, 
            u'', 
            u'', 
        ]
    rows.append(ret)
    time.sleep(0.1)
'''


writecsv(
    'emu/equip%s.csv' % (yyyymmdd),
    [[x.encode('utf-8') for x in row] for row in rows]
)
