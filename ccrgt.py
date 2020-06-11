#!/usr/bin/python
# -*- coding: utf-8 -*-

from view_train_list import *
import requests
import json
import re
import time
import datetime
import os


def seat(s):
    seat_map = {
        '餐车': 'CA',
        '行李车': 'XL',
        # '行邮车': 'XL',
        '邮政车': 'UZ',
        '空调发电车': 'KD',
        '发电车': 'KD',
        '硬座': 'YZ',
        '软座': 'RZ',
        '硬卧': 'YW',
        '软卧': 'RW',
        '双层硬座': 'SYZ',
        '双层软座': 'SRZ',
        '双层硬卧': 'SYW',
        '双层软卧': 'SRW',
        '包厢式硬卧': 'YW18',
        '高级软卧': 'RW19',
        '高级卧': 'WG',
        '一等软座': 'RZ1',
        '二等软座': 'RZ2',
        '一等座': 'ZY',
        '二等座': 'ZE',
        '二等座一等座': 'ZYE',
        '商务座': 'ZS',
        '特等座': 'ZT',
        '二等/餐车': 'ZEC',
        '二等座餐车': 'ZEC',
        '软卧餐车': 'WRC',
        '一等/商务座': 'ZYS',
        '一等座商务座': 'ZYS',
        '商务座一等座': 'ZYS',
        '二等/商务座': 'ZES',
        '商务座二等座': 'ZES',
        '二等座商务座': 'ZES',
        '一等/特等座': 'ZYT',
        '一等座特等座': 'ZYT',
        '二等/特等座': 'ZET',
        '二等座特等座': 'ZET',
    }
    if s.encode('utf-8') in seat_map:
        return seat_map[s.encode('utf-8')]
    return s


def seatcaps(arr_seat, arr_cap):
    ret = []
    for i in range(len(arr_seat)):
        ret.append('%s%s(%s)' % ('', seat(arr_seat[i]), arr_cap[i]))
    return '+'.join(ret)


def getcdinfo(date, s, cache=2):
    name = 'ccrgt/ccrgt_' + date + '_' + s + '.json'
    try:
        fn = os.path.join(os.path.dirname(os.path.abspath(__file__)), name)
    except:
        fn = name
    if os.path.exists(fn):
        with open(fn, 'rb') as f:
            data = f.read()
        try:
            j = json.loads(data)
            ret = [
                s.encode('utf-8'),
                '%s(%d)' % (
                    j['data']['trainType'].encode('utf-8'),
                    sum([int(re.sub(r'\D', '', x['peopleNum'])) for x in j['data']['cdInfoList']])
                ),
                re.sub(u'中国铁路(.*)局动车段', r'\1', j['data']['fixDepart']).encode('utf-8'),
                re.sub(u'中国铁路(.*)局客运段', r'\1', j['data']['serverDepart']).encode('utf-8'),
                re.sub(u'(.*)节动力车，(.*)节非动力车', r'\1M\2T', j['data']['trainTeam']).encode('utf-8'),
                seatcaps(
                    [(x['seatType1'] if x['seatType1'] else '') +
                     (x['seatType2'] if x['seatType2'] else '') +
                     (x['dinnerCar'] if x['dinnerCar'] else '') for x in j['data']['cdInfoList']],
                    [re.sub(r'\D', '', x['peopleNum']) for x in j['data']['cdInfoList']]
                ).encode('utf-8'),
            ]
            return ret, 0
        except:
            pass
            #print(s + "-")
            # print(fn)
    if cache >= 2:
        print('%s no file' % (s))
        return [s.encode('utf-8'), "", "", "", "", ""], -1
    url = 'https://tripapi.ccrgt.com/crgt/trip-server-app/travel/getCDInfo'
    j = {"params": {"date": "2020-01-13", "trainNumber": s}}
    header = {
        "User-Agent": "Netscape 5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36",
        "Content-Type": "application/json"
    }
    try:
        resp = requests.post(url, data=json.dumps(j),
                             headers=header, timeout=20)
    except:
        print('net error %s' % (s))
        return [s.encode('utf-8'), "", "", "", "", ""], -3
    body = resp.content.decode('utf-8')
    time.sleep(0.5)
    #
    try:
        j = json.loads(body)
    except:
        print('json error %s' % (s))
        return [s.encode('utf-8'), "", "", "", "", ""], -2
    if 'data' in j and j['data']:
        ret = [
            s.encode('utf-8'),
            '%s(%d)' % (
                j['data']['trainType'].encode('utf-8'),
                sum([int(re.sub(r'\D', '', x['peopleNum'])) for x in j['data']['cdInfoList']])
            ),
            re.sub(u'中国铁路(.*)局动车段', r'\1', j['data']['fixDepart']).encode('utf-8'),
            re.sub(u'中国铁路(.*)局客运段', r'\1', j['data']['serverDepart']).encode('utf-8'),
            re.sub(u'(.*)节动力车，(.*)节非动力车', r'\1M\2T', j['data']['trainTeam']).encode('utf-8'),
            seatcaps(
                [(x['seatType1'] if x['seatType1'] else '') +
                 (x['seatType2'] if x['seatType2'] else '') +
                 (x['dinnerCar'] if x['dinnerCar'] else '') for x in j['data']['cdInfoList']],
                [re.sub(r'\D', '', x['peopleNum']) for x in j['data']['cdInfoList']]
            ).encode('utf-8'),
        ]
        # for r in ret:
        # print(type(r))
        # print((','.join(ret)).decode('utf-8'))
        with open(fn, 'wb') as f:
            f.write(resp.content)
        return ret, 0
    # except:
    else:
        print('%s -' % (s))
        return [s.encode('utf-8'), "", "", "", "", ""], -1
    return j, 0


date = datetime.datetime.now().strftime('%Y%m%d')

name = 'js/train.csv'
try:
    fn = os.path.join(os.path.dirname(os.path.abspath(__file__)), name)
except:
    fn = name

c = readcsv(fn)
idx = 0
map = {}
ret = []
for i in range(idx, len(c), 1):
    if len(c[i]) <= 3 or c[i][3] in map:
        continue
    if c[i][3][0] in 'GDCS':
        # print(c[i][3])
        cache = 1
        row = []
        for retry in range(3):
            row, status = getcdinfo(date, c[i][3], cache)
            # time.sleep(0.5)
            if status >= -1:
                break
        ret.append([x for x in row])
        # print(','.join(row))
        idx = i + 1
        map[c[i][3]] = 1


name = 'emu/ccrgt%s.csv' % (date)
try:
    fn1 = os.path.join(os.path.dirname(os.path.abspath(__file__)), name)
except:
    fn1 = name

writecsv(fn1, ret)

# awk -F '[,]' '{print $2","$6}' ccrgt.csv|sort|uniq>车型.csv
