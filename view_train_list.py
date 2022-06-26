#!/usr/bin/python
# -*- coding: utf-8 -*-
# tested in python 2.7.16 on windows server 2016 x64
# tested in python 2.7.15 on win10 x64
# tested in python 2.7.14 on centos7 x64
# tested in python 2.7.5 on centos7 x64

from __future__ import print_function

import os
import sys
import platform
import re
import json
import time
import datetime
import base64
# import math
# import random

import requests


def readcsv(fn):
    with open(fn, 'rb') as f:  # py2
        if f.read(3) != b'\xef\xbb\xbf':
            f.seek(0, 0)
        data = f.read().decode('utf-8')
    c = data.split('\n')
    for i in range(len(c)):
        c[i] = c[i].replace('\r', '').split(',')
    return c


def writecsv(f1, ret):
    if len(ret) == 0:
        return 0
    try:
        fn = os.path.join(os.path.dirname(os.path.abspath(__file__)), f1)
    except:
        fn = f1
    with open(fn, "wb") as f: # use wb on win, or get more \r \r\n
        if f.tell() == 0:
            f.write(b'\xef\xbb\xbf')
        for i in range(len(ret)):
            f.write(b','.join(ret[i]) + b'\n')
    return len(ret)


def writemincsv(f1, ret):
    if len(ret) == 0:
        return 0
    try:
        fn = os.path.join(os.path.dirname(os.path.abspath(__file__)), f1)
    except:
        fn = f1
    with open(fn, "wb") as f: # use wb on win, or get more \r \r\n
        if f.tell() == 0:
            f.write(b'\xef\xbb\xbf')
        for i in range(len(ret)):
            f.write(re.sub(r',+$', r'', b','.join(ret[i]) + b'\n'))
    return len(ret)


def readbyte(fn):
    '''
    read bytes skip UTF-8 BOM
    '''
    # f = open(fn, 'r',encoding = 'utf8'); #py3
    # f = open(fn, 'r'); #py2
    data = ''
    with open(fn, 'rb') as f: # py2 py3
        if f.read(3) != b'\xef\xbb\xbf':
            f.seek(0, 0)
        data = f.read()
    return data


def writebyte(f1, b):
    '''
    write bytes without UTF-8 BOM
    '''
    try:
        fn = os.path.join(os.path.dirname(os.path.abspath(__file__)), f1)
    except:
        fn = f1
    with open(fn, 'wb') as f: # use wb on win, or get more \r \r\n
        f.write(b)


def writebytebom(f1, b):
    '''
    write bytes with UTF-8 BOM
    '''
    try:
        fn = os.path.join(os.path.dirname(os.path.abspath(__file__)), f1)
    except:
        fn = f1
    with open(fn, 'wb') as f: # use wb on win, or get more \r \r\n
        if f.tell() == 0:
            f.write(b'\xef\xbb\xbf')
        f.write(b)


def isLeap(y):
    if y & 0x03:
        return 0
    if y % 400 == 0:
        return 1
    if y % 100 == 0:
        return 0
    return 1


def date_add(date, diff):
    match = re.findall(r'(\d+)-(\d+)-(\d+)', date, re.I | re.M)[0]
    y = int(match[0])
    m = int(match[1])
    d = int(match[2])
    day_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    day_month[2 - 1] = 28
    if isLeap(y):
        day_month[2 - 1] = 29
    #
    d += diff
    #
    while d > day_month[(m-1) % 12]:
        d -= day_month[(m-1) % 12]
        m += 1
        while m > 12:
            m -= 12
            y += 1
            day_month[2 - 1] = 28
            if isLeap(y):
                day_month[2 - 1] = 29
    #
    while d < 1:
        m -= 1
        while m < 1:
            y -= 1
            day_month[2 - 1] = 28
            if isLeap(y):
                day_month[2 - 1] = 29
            m += 12
        d += day_month[(m-1) % 12]
    #
    return '%04d-%02d-%02d' % (y, m, d)


def date_ymd(s):
    return re.sub(r'(\d\d\d\d)(\d\d)(\d\d)', r"\1-\2-\3", s)


def date_yyyymmdd(s):
    return re.sub(r'(\d\d\d\d)-(\d\d)-(\d\d)', r"\1\2\3", s)


def date_add_ymd(s, diff):
    if len(s) == 6:
        s = '20' + s
    if diff == 0:
        return s
    ymd = re.sub(r'(\d\d\d\d)(\d\d)(\d\d)', r"\1-\2-\3", s)
    return re.sub(r'(\d\d\d\d)-(\d\d)-(\d\d)', r"\1\2\3", date_add(ymd, diff))


def datediff(date1, date0):
    match = re.findall(r'(\d+)-(\d+)-(\d+)', date0, re.I | re.M)[0]
    y = int(match[0])
    m = int(match[1])
    d = int(match[2])
    match = re.findall(r'(\d+)-(\d+)-(\d+)', date1, re.I | re.M)[0]
    y1 = int(match[0])
    m1 = int(match[1])
    d1 = int(match[2])
    #
    day_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    day_month[2 - 1] = 28
    if isLeap(y):
        day_month[2 - 1] = 29
    #
    cmp = 0
    if y < y1:
        cmp = 1
    if y > y1:
        cmp = -1
    if y == y1:
        if m < m1:
            cmp = 1
        if m > m1:
            cmp = -1
    #
    while cmp == 1:
        d -= day_month[(m - 1) % 12]
        m += 1
        while m > 12:
            m -= 12
            y += 1
            day_month[2 - 1] = 28
            if isLeap(y):
                day_month[2 - 1] = 29
        if (y1 == y and m1 == m):
            break
    #
    while cmp == -1:
        m -= 1
        while m < 1:
            y -= 1
            day_month[2 - 1] = 28
            if isLeap(y):
                day_month[2 - 1] = 29
            m += 12
        d += day_month[(m - 1) % 12]
        if (y1 == y and m1 == m):
            break
    return d1 - d


def nowdate():
    return datetime.datetime.now().strftime('%Y-%m-%d')


def basedate(now):
    graphdate_rev = [
'19970401',
'19981001',
'20001021',
'20011021',
'20040418',
'20070418',
'20081221',
'20090401', '20090701', '20091111', # '20091226',
'20100426', # '20100701',
'20110111', '20110701', '20110828', '20111212',
'20120701', '20121221', # '20120401',
'20130701', '20131228', 
'20140701', '20141210', 
'20150320', '20150701', # '20150520',
'20160110', '20160515', '20160910', '20161101', 
'20170105', '20170416', '20170701', '20170921',
'20171228', '20180410', '20180701', '20180921', #    '20180201', '20180404', 
'20190105', '20190410', '20190710', '20191011', #    '20191230', 
#    '20190121', '20190404', '20190430', '20190606', '20190912', '20190930', 
'20200110', '20200410', '20200701', '20201011', #    '20200430',
'20210120', '20210410', '20210625', '20211011',
'20220110', '20220408', '20220620',
][::-1]
    if not now:
        now = nowdate()
    for d in graphdate_rev:
        date = date_ymd(d)
        if datediff(now, date) >= 0:
            return date_ymd(d)
    return date_ymd(graphdate_rev[0])


def base_yymmdd(now=''):
    return date_yyyymmdd(basedate(now))[2:]


def weekday(date):
    match = re.findall(r'(\d+)-(\d+)-(\d+)', date, re.I | re.M)[0]
    y = int(match[0])
    m = int(match[1])
    d = int(match[2])
    if m <= 2:
        m += 12
        y -= 1
    c = y // 100
    y = y % 100
    w = y+y//4+c//4-2*c+(13*(m+1))//5+d-1
    # return 365*(y-1)+y//4 +36524*c+c//4 +153*(m + 1)//5-63 + d
    return w % 7


def getmin(s):
    try:
        a, b = s.split(':')[0:2]
        return int(a)*60+int(b)
    except:
        return -1


def has_a_day(s):
    s = re.sub("^(.*)&", "", s)
    date = "20200601"
    if s == "":
        return date
    if s[0] == u'停':
        return date
    if s[0] == u'!':
        return date
    if s[0] == u'b':
        return date
    if s[0] == u'单':
        return date_add_ymd(date, 1)
    if s[0] == u'双':
        return date
    if s[0] == u'w':
        diff = int(s[1]) - weekday(re.sub(r'(\d\d\d\d)(\d\d)(\d\d)', r"\1-\2-\3", date))
        if diff < 0:
            diff += 7
        return date_add_ymd(date, diff)
    #
    if len(s) < 4:
        return date
    #
    sp = s.split("|")
    #
    if len(sp) > 0:
        ssp = sp[0].split("-")
        return '20'+ssp[0]
    return date


def is_a_day(s, date):
    #print('is_a_day() %s %s'%(s,date))
    s = re.sub("^(.*)&", "", s)
    if s == "":
        return 1
    if s[0] == u'停':
        return 1-is_a_day(re.sub(u'停', '', s), date)
    if s[0] == '!':
        return 1-is_a_day(re.sub(u'!', '', s), date)
    if s[0] == u'b':
        return 1
    if s[0] == u'单':
        return 1
    if s[0] == u'双':
        return 1
    if s[0] == u'w':
        return 1
        w = weekday(re.sub(r'(\d\d\d\d)(\d\d)(\d\d)', r"\1-\2-\3", date))
        if w < 0:
            w += 7
        return 1
    #
    if len(s) < 4:
        return 1
    #
    # TODO
    yyyymmdd = '20000000'
    sp = s.split("|")
    for i in range(len(sp)):
        ssp = sp[i].split("-")
        if len(ssp):
            yyyymmdd = yyyymmdd[:-len(ssp[0])]+ssp[0]
            d0 = yyyymmdd
            yyyymmdd = yyyymmdd[:-len(ssp[-1])]+ssp[-1]
            d1 = yyyymmdd
            #print(d0, d1)
            if d0 <= date and date <= d1:
                return 1
    #
    return 0

#is_a_day(u'!200425-30|0502-03|17-18', '20200616')


def print_stat(stat):
    buf = ''
    for i in range(len(stat)):
        buf += (("    " + str(stat[i]))[-4:]
                + ('' if (i+1) % 20 else '\n')
                + ('' if (i+1) % 60 else '\n'))
    return buf


def no_add(s, diff):
    '''
    no_add(24000000Z10A,-1) -> 24000000Z109
    '''
    if len(s) < 12:
        return s, -1
    if diff < 0:
        if s[11] == 'A':
            return s[0:11] + '9', 1
        return s[0:11] + chr(ord(s[11]) - 1), 1
    if diff > 0:
        if s[11] == '9':
            return s[0:11] + 'A', 1
        return s[0:11] + chr(ord(s[11]) + 1), 1
    return s, 0


def no2_add(s, diff):
    '''
    no_add(5600000G4070,-1) -> 5600000G4060
    '''
    if len(s) < 12:
        return s, -1
    if diff < 0:
        if s[10] == 'A':
            return s[0:10] + '90', 1
        return s[0:10] + chr(ord(s[10]) - 1) + '0', 1
    if diff > 0:
        if s[10] == '9':
            return s[0:10] + 'A0', 1
        return s[0:10] + chr(ord(s[10]) + 1) + '0', 1
    return s, 0


# seat
def seat(s):
    seat_map = {
        '餐车': 'CA',
        '行李车': 'XL',
        '行邮车': 'XU',
        '邮政车': 'UZ',
        '空调发电车': 'KD',
        '发电车': 'KD',  # FD
        '硬座': 'YZ',
        '软座': 'RZ',
        '硬卧': 'YW',
        '软卧': 'RW',
        '双层硬座': 'SYZ',
        '双层软座': 'SRZ',
        '双层硬卧': 'SYW',
        '双层软卧': 'SRW',
        '包厢式硬卧': 'YW18',  # BY
        '高级软卧': 'RW19',  # GR
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


def seats(arr_seat):
    ret = []
    num = 0
    last = ''
    for i in range(len(arr_seat)):
        if arr_seat[i] != last and i > 0:
            ret.append('%s%s' % (num if num > 1 else '', seat(last)))
            num = 0
        last = arr_seat[i]
        num += 1
    ret.append('%s%s' % (num if num > 1 else '', seat(last)))
    return '+'.join(ret)


def seatcaps(arr_seat, arr_cap):
    ret = []
    num = 0
    last = ''
    last_cap = ''
    for i in range(len(arr_seat)):
        if (arr_seat[i] != last or arr_cap[i] != last_cap) and i > 0:
            ret.append('%s%s(%s)' % (
                num if num > 1 else '',
                seat(last),
                last_cap
            ))
            num = 0
        last = arr_seat[i]
        last_cap = arr_cap[i]
        num += 1
    ret.append('%s%s(%s)' % (
        num if num > 1 else '',
        seat(last),
        last_cap
    ))
    return '+'.join(ret)


def seatcapsccrgt(arr_seat, arr_cap):
    ret = []
    for i in range(len(arr_seat)):
        ret.append('%s%s(%s)' % ('', seat(arr_seat[i]), arr_cap[i]))
    return '+'.join(ret)


# compare
def cmpbyTime(a1, a2):
    if (len(a1) < 5):
        return 0
    if (len(a2) < 5):
        return 0
    t1 = getmin(a1[4])
    t2 = getmin(a2[4])
    if t1 > t2:
        return 1
    if t1 < t2:
        return -1
    return 0


def cmpby0_7_i2_i5_i3_m4(a1, a2):
    if (len(a1) < 5):
        return 0
    if (len(a2) < 5):
        return 0
    train1 = a1[0]
    train2 = a2[0]
    if train1 > train2:
        return 1
    if train1 < train2:
        return -1
    date1 = a1[7] if (len(a1) > 7) else ''
    date2 = a2[7] if (len(a2) > 7) else ''
    if date1 > date2:
        return 1
    if date1 < date2:
        return -1
    n1 = int(a1[2])
    n2 = int(a2[2])
    if n1 > n2:
        return 1
    if n1 < n2:
        return -1
    if int(a1[5]) > int(a2[5]):
        return 1
    if int(a1[5]) < int(a2[5]):
        return -1
    d1 = int(a1[3])
    d2 = int(a2[3])
    if d1 > d2:
        return 1
    if d1 < d2:
        return -1
    t1 = getmin(a1[4])
    t2 = getmin(a2[4])
    if t1 > t2:
        return 1
    if t1 < t2:
        return -1
    return 0


# station_name.js
def getStation(fn='js/station_name.js', fn1='js/qss.js'):
    s = re.findall(
        r'\'\@([^\']+)\'',
        readbyte(fn).decode('utf-8'),
        re.I | re.M
    )[0].split('@')
    for i in range(len(s)):
        s[i] = s[i].split('|')
    print('read %d stations in %s' % (len(s), fn))
    s.append([u"tsn", u"唐山南", u"TNP", u"tangshannan", u"tsn", u"-1"])
    s.append([u"gye", u"古冶", u"GYP", u"guye", u"gy", u"-1"])
    s.append([u"", u"香港红磡", u"JQO", u"xiangganghongkan", u"xghk", u"-1"])
    s.append([u"jlo", u"九龙", u"JQO", u"jiulong", u"jl", u"-1"])
    s.append([u'jsw', u'金山卫', u'BGH', u'jinshanwei', u'jsw', u'-1'])
    s.append([u'mji', u'梅江', u'MKQ', u'meijiang', u'mj', u'-1'])
    s.append([u'ylo', u'元龙', u'YLY', u'yuanlong', u'yl', u'-1'])
    s.append([u'nsb', u'南山北', u'NBQ', u'nanshanbei', u'nsb', u'-1'])
    s.append([u'', u'车墩', u'MIH', u'chedun', u'cd', u'-1'])
    s.append([u'', u'羊木', u'AMJ', u'yangmu', u'ym', u'-1'])
    s.append([u'', u'马海', u'MHO', u'mahai', u'mh', u'-1'])
    try:
        qss = json.loads(re.findall(
            r'{.*}',
            readbyte(fn1).decode('utf-8'),
            re.I | re.M | re.S
        )[0])
        print('read %d qss in %s' % (len(qss), fn1))
    except:
        qss = {}
    for row in s:
        row.append(re.sub(r':00$', '', qss.get(row[1], "")))
        # row.append(row[1].encode('gbk').encode('hex').decode('latin-1'))
        row.append(base64.b64encode(row[1].encode('gbk')).decode('latin-1'))
    return s


def telecode(s, station):
    for i in range(len(station)):
        if s == station[i][1]:
            return station[i][2]
    # print(s)
    return u''


def teleToName(s, station):
    for i in range(len(station)):
        if s == station[i][2]:
            return station[i][1]
    # print(s)
    return u''


# telecode hash
def hash_tele(s):
    if len(s) < 3:
        return 0
    return (ord(s[2])-65) * 26 * 26 + (ord(s[0])-65) * 26 + (ord(s[1])-65)


def unhash_tele(n):
    return chr(n//26 % 26+65) + chr(n % 26+65) + chr(n//26//26+65)


# train_map
def hash_no(s):
    items = [('Z', 10000), ('T', 20000), ('K', 30000),
             ('Y', 00000),
             ('G', 40000), ('D', 50000), ('C', 60000),
             ('S', 70000),
             ('L', 80000), ('A', 80000), ('N', 80000),
             ('P', 10000), ('Q', 20000), ('W', 30000),
             ('J', 40000), ('I', 50000),
             ('H', 80000),
             ('V', 1000), ('B', 2000), 
             ('U', 4000), ('X', 5000), ('M', 6000), 
             ('O', 7000)]
    d = dict(items)
    train_class = d[s[0]] if s[0] in d else 0
    try:
        n = int(re.sub(r'\D+', '', str(s)))
    except:
        print('hash_no error %s', s)
        n = 0
    return train_class + n


def unhash_no(n):
    items = [('Z', 10000), ('T', 20000), ('K', 30000),
             ('Y', 00000),
             ('G', 40000), ('D', 50000), ('C', 60000),
             ('S', 70000),
             ('L', 80000), ('A', 80000), ('N', 80000),
             ('P', 10000), ('Q', 20000), ('W', 30000),
             ('I', 50000),
             ('V', 1000), ('B', 2000), ('U', 4000), ('X', 5000)]
    head = ["", "Z", "T", "K", "G", "D", "C", "S", "L"]
    if n > 90000:
        return ""
    train_class = head[(n-1) // 10000]
    if n <= 1000:
        train_class = "Y"
    for i in range(len(items)):
        if train_class == items[i][0]:
            return train_class + str(n-items[i][1])
    return str(n)


def hash_no_stat_block(arr, step, maxlen):
    cnt = 0
    # step = 100;
    stat = [0 for i in range(1+(maxlen-1)//step)]
    for i in range(len(arr)):
        if arr[i]:
            stat[i//step] += 1
            cnt += 1
    return stat, cnt


def print_block(stat):
    s = ''
    cnt = 0
    for i in range(len(stat)):
        s += (("    " + str(stat[i]))[-4:]
              + ('' if (i+1) % 10 else '\n')
              + ('' if (i+1) % 100 else '\n'))
        if stat[i]:
            cnt += 1
    return s, cnt


def add_map(train_map, a):
    '''
    add s obj to train_map
    map[key][idx].date |= date
    map[key][idx].src |= src
    1 hand write
    2 search_v1
    4 train_list.js
    8 czxx
    16 ticketleft
    '''
    key = hash_no(re.sub(r'^0+', "", a['train_no'][2:10])) - 1
    if key >= len(train_map):
        print('out of index limit train_map %s' % (re.sub(r'^0+', "", a['train_no'][2:10])))
        key = len(train_map) - 1
        return
    found = 0
    for train in train_map[key]:
        if train['train_no'] == a['train_no']:
            train['date'] |= a['date']
            train['src'] |= a['src']
            found = 1
            break
    if found == 0:
        train_map[key].append(a)


def mapToArr(train_map):
    '''
    hash bucket train_map to compact array train_arr
    '''
    train_arr = []
    for key in range(len(train_map)):
        train_arr.extend(train_map[key])
    return train_arr


def trainlistCsv(train_arr, base_date, size, station=None):
    stat = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    ret = []
    for train in train_arr:
        t1 = ''
        t2 = ''
        if station != None:
            t1 = telecode(train['from_station'], station).encode('utf-8')
            t2 = telecode(train['to_station'], station).encode('utf-8')
        if not t1:
            t1 = train['from_station'].encode('utf-8')
        if not t2:
            t2 = train['to_station'].encode('utf-8')
        #
        val, status = compress_bin_vector(train['date'], base_date, size)
        stat[status] += 1
        #
        ret.append([
            train['train_no'].encode('utf-8'),
            t1,
            t2,
            train['station_train_code'].encode('utf-8'),
            str(train['total_num'] if 'total_num' in train else 0),
            '0' if 'service_type' in train and train['service_type'] == '0' else '',
            val,
            # train['src'],
        ])
    #
    print(stat)
    return ret


# train_list.js
def openTrainList(fn='js/train_list.js'):
    return json.loads(readbyte(fn)[16:])


def add_train_list(train_map, fn0='js/train_list.js', base_date=None):
    '''
    add 30~60 days train_list to train_map

    a['station_train_code'] : u'Z97(北京西-广州)'
    a['train_no'] : u'2400000Z9701'

    s['station_train_code'] = u'Z97'
    s['from_station'] = u'北京西'
    s['to_station'] = u'广州'
    s['train_no'] = u'2400000Z9701'
    s['total_num'] = 0
    s['date'] = 0

    '''
    print('add_train_list() %s' % (fn0))
    data = readbyte(fn0)[16:]  # .decode('utf-8')
    #
    slice_mark = sorted(mark_json_slice(data))
    # print(slice_mark)
    if base_date == None:
        base_date = slice_mark[0][0]
    mask = 0
    msg = ''
    for i in range(len(slice_mark)):
        date = slice_mark[i][0]
        d = json.loads(data[slice_mark[i][1]:slice_mark[i][2]])
        diff = datediff(date, base_date)
        if diff < 0:
            continue
        cnt = 0
        ss = ''
        ss += (date.encode('utf-8'))
        for train_class in d:
            ss += '\t%s %d' % (
                train_class.encode('utf-8'),
                len(d[train_class])
            )
            for idx in range(0, len(d[train_class])):
                cnt += 1
                a = atos(d[train_class][idx])
                a['date'] = (1 << diff)
                a['src'] = 4
                add_map(train_map, a)
                #
        ss += '\t%d' % (cnt)
        print(ss)
        if cnt:
            mask |= (1 << diff)
        msg += ss + '\n'
    return base_date, mask, msg

# 181103 new 12306 search/v1
def getsearch12306(kw, date, cache=1):
    yyyymmdd = date.replace("-", "")
    name = 'search%s/%s_%s.json' % (base_yymmdd(date), yyyymmdd, kw)
    try:
        fn = os.path.join(os.path.dirname(os.path.abspath(__file__)), name)
    except:
        fn = name
    if cache == 0 and os.path.exists(fn) and os.path.getmtime(fn):
        cache = 1
    if cache and os.path.exists(fn):
        try:
            search = json.loads(readbyte(fn))
            if search['status'] == True and len(search['data']) and cache<2:
                print('read  %-3s %3d %5s-%5s %8s' % (
                    kw, len(search['data']),
                    search['data'][0]['station_train_code'],
                    search['data'][-1]['station_train_code'],
                    yyyymmdd
                    )
                )
                return search['data'], len(search['data'])
        except ValueError:
            print('ValueError ' + kw)
    if cache >= 2:
        return [], 0
    #
    url = "https://search.12306.cn/search/v1/train/search?keyword=" + \
        kw + "&date=" + yyyymmdd
    # header = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:59.0) Gecko/20100101 Firefox/59.0"}
    header = {
        "User-Agent": "Netscape 5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36",
        "Referer": "https://kyfw.12306.cn/",
    }
    try:
        resp = requests.get(url, headers=header, timeout=20)
    except:
        print('Net Error ' + kw)
        return [], -1
    body = resp.content.decode('utf-8')  # bytes -> str (ucs2)
    try:
        search = json.loads(body)
    except ValueError:
        print('ValueError ' + kw)
        time.sleep(5)
        return [], -2
    if not isinstance(search, dict):
        print('search is %s %s' % (type(search), kw))
        return [], -1
    if not 'data' in search:
        print('key data not exist ' + kw)
        return [], -1
    if search['status'] == True and len(search['data']):
        writebyte(name, resp.content)
        print('save  %-3s %3d %5s-%5s %8s' % (
            kw, len(search['data']),
            search['data'][0]['station_train_code'],
            search['data'][-1]['station_train_code'],
            yyyymmdd
            )
        )
        time.sleep(1)
        return search['data'], len(search['data'])
    else:
        print('empty %-3s' % (kw))
        return [], 0


def searchAll12306(train_map, base_date, date, st, cache=1):
    '''
    dfs search_v1 in stack
    add to train_map
    '''
    #st = ["90", "50", "10", "C", "D", "G", "", "K", "Y", "P", "T", "Z"]
    size = 0
    dead = []
    cnt = 0
    while(len(st)):
        kw = st.pop()
        jump = 0
        if kw == "": # kw == "Y" or 
            jump = 1 # direct push stack 0-9
        max_depth = 3
        res = []
        ret = 0
        if not jump:
            cnt += 1
            for retry in range(2):
                res, ret = getsearch12306(kw, date, cache)
                if ret >= 0:
                    break
                if ret == -2:
                    # time.sleep(300)
                    break
                time.sleep(2 << retry)
        if cache < 2 and cnt % 15 == 0: # TODO
            time.sleep(60)
        if ret == -1:
            dead.append(kw)
            continue
        if ret == -2:
            dead.append(kw)
            dead.extend(st)
            return dead, size
        max_index = -1
        for i in range(len(res)):
            diff = datediff(date, base_date)
            if diff >= size:
                size = diff + 1
            res[i]['date'] = 1 << diff
            res[i]['src'] = 2
            add_map(train_map, res[i])
            if res[i]['station_train_code'].startswith(kw):
                max_index = i
        max_str = ""
        if not jump:
            if max_index + 1 < 200:
                continue
            max_str = res[max_index]['station_train_code']
        if len(kw) >= max_depth:
            print("max_depth")
            continue
        for i in range(9, -1, -1):
            k = kw + str(i)
            if re.sub(r'\D+', '', k).startswith('0'):
                continue
            #if k in max_str or k > max_str or len(re.sub(r'\D+', '', max_str)) < 4: #顺序
                #st.append(k)
            #if len(re.sub(r'\D+', '', max_str)) < 4: 
            st.append(k) #乱序 除了0开头都进
    return dead, size


def atos(a):
    '''
    transform object a in train_list.js to object s in search_v1

    a['station_train_code'] : u'Z97(北京西-广州)'
    a['train_no'] : u'2400000Z9701'

    s['station_train_code'] = u'Z97'
    s['from_station'] = u'北京西'
    s['to_station'] = u'广州'
    s['train_no'] = u'2400000Z9701'
    s['total_num'] = 0
    s['date'] = 0
    '''
    # a to s obj
    match = re.findall(
        r'(.*)\((.*)-(.*)\)',
        a['station_train_code'],
        re.I | re.M
    )[0]
    s = {}
    s['station_train_code'] = match[0]
    s['from_station'] = match[1]
    s['to_station'] = match[2]
    s['train_no'] = a['train_no']
    s['total_num'] = 0
    s['date'] = 0
    return s


# timetable train_list.js
def processS(a, date, station):
    name = 'sch/' + a['train_no'].encode('utf-8')+'.json'
    try:
        fn = os.path.join(os.path.dirname(os.path.abspath(__file__)), name)
    except:
        fn = name
    if os.path.exists(fn):
        try:
            sch = json.loads(readbyte(fn))
            if sch['status'] == True and sch['httpstatus'] == 200 \
                    and len(sch['data']['data']):
                return sch['data']['data']
        except ValueError:
            print('ValueError ' + a['train_no'])
    #
    t1 = telecode(a['from_station'], station).encode('utf-8')
    t2 = telecode(a['to_station'], station).encode('utf-8')
    if not t1:
        if platform.system() == "Windows":
            print(a['from_station'].encode('gbk') +
                  " telecode not found! " + a['station_train_code'].encode('gbk'))
        else:
            print(a['from_station'].encode('utf-8') +
                  " telecode not found! " + a['station_train_code'].encode('utf-8'))
        t1 = "AAA"
    if not t2:
        if platform.system() == "Windows":
            print(a['to_station'].encode('gbk') +
                  " telecode not found! " + a['station_train_code'].encode('gbk'))
        else:
            print(a['to_station'].encode('utf-8') +
                  " telecode not found! " + a['station_train_code'].encode('utf-8'))
        t2 = "AAA"
    return getSch12306(t1, t2, a['train_no'], date)


# timetable
def getSch12306(t1, t2, train_no, date):
    sch = getSch12306Local(train_no)
    if len(sch):
        return sch
    sch = getSch12306Online(t1, t2, train_no, date)
    return sch


def getSch12306Local(train_no):
    name = 'sch/' + train_no + '.json'
    try:
        fn = os.path.join(os.path.dirname(os.path.abspath(__file__)), name)
    except:
        fn = name
    if os.path.exists(fn):
        try:
            sch = json.loads(readbyte(fn))
            if sch['status'] == True and sch['httpstatus'] == 200 and len(sch['data']['data']):
                return sch['data']['data']
        except ValueError:
            print('ValueError %s local' % (train_no))
            return []
    return []


def getSch12306Online(t1, t2, train_no, date):
    url = "https://kyfw.12306.cn/otn/czxx/queryByTrainNo?train_no=" + train_no + \
        "&from_station_telecode=" + t1 + "&to_station_telecode=" + t2 + \
        "&depart_date=" + date
    header = {
        "User-Agent": "Netscape 5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36"}
    try:
        resp = requests.get(url, headers=header, timeout=30)
    except:
        print('Net Error ' + train_no)
        return []
    body = resp.content.decode('utf-8')  # bytes -> str (ucs2)
    try:
        sch = json.loads(body)
    except ValueError:
        print('ValueError %s %s' % (train_no, date))
        return []
    name = 'sch/' + train_no + '.json'
    if sch['status'] == True and sch['httpstatus'] == 200 and len(sch['data']['data']):
        writebyte(name, resp.content)
        print('%s %s %s %2d' % (train_no, t1, t2, len(sch['data']['data'])))
        return sch['data']['data']
    else:
        print('data error %s %s %s %s' % (train_no, t1, t2, date))
        return []


def schToCsv(s):
    # buf = ''
    ret = []
    day = 0
    last = 0
    for i in range(0, len(s)):
        # print(s[0]['station_train_code'].encode('utf-8') + ',' + s[i]['station_name'].encode('utf-8') + ',' + s[i]['start_time'].encode('utf-8') + ',' + s[i]['arrive_time'].encode('utf-8')); # 打印时刻
        if getmin(s[i]['arrive_time']) > -1 and i > 0:
            minute = getmin(s[i]['arrive_time'])
            if minute < last:
                day += 1
            last = minute
            # TODO
            # print(s[0]['station_train_code'].encode('utf-8') + ',' + s[i]['station_name'].encode('utf-8') + ',' + s[i]['arrive_time'].encode('utf-8') + ',' + '0');
            # print(s[0]['station_train_code'].encode('utf-8') + ',' + s[i]['station_name'].encode('utf-8') + ',' + s[i]['station_no'].encode('utf-8') + ',' + str(day) + ',' + s[i]['arrive_time'].encode('utf-8') + ',' + '0');
            '''buf += (
                s[0]['station_train_code'].encode('utf-8')
                + ',' + s[i]['station_name'].encode('utf-8')
                + ',' + s[i]['station_no'].encode('utf-8')
                + ',' + str(day)
                + ',' + s[i]['arrive_time'].encode('utf-8')
                + ',' + '1'+'\n'
            )'''
            ret.append([
                s[0]['station_train_code'].encode('utf-8'),
                s[i]['station_name'].replace(u'\ue244', u'\u78cf').replace(
                    u'\ue24d', u'\u6911').encode('utf-8'),
                s[i]['station_no'].encode('utf-8'),
                str(day),
                s[i]['arrive_time'].encode('utf-8'),
                '0'
            ])
        #
        if getmin(s[i]['start_time']) > -1 and i < len(s)-1:
            minute = getmin(s[i]['start_time'])
            if minute < last:
                day += 1
            last = minute
            # print(s[0]['station_train_code'].encode('utf-8') + ',' + s[i]['station_name'].encode('utf-8') + ',' + s[i]['start_time'].encode('utf-8') + ',' + '1');
            # print(s[0]['station_train_code'].encode('utf-8') + ',' + s[i]['station_name'].encode('utf-8') + ',' + s[i]['station_no'].encode('utf-8') + ',' + str(day) + ',' + s[i]['start_time'].encode('utf-8') + ',' + '1');
            '''buf += (
                s[0]['station_train_code'].encode('utf-8')
                + ',' + s[i]['station_name'].encode('utf-8')
                + ',' + s[i]['station_no'].encode('utf-8')
                + ',' + str(day)
                + ',' + s[i]['start_time'].encode('utf-8')
                + ',' + '1'+'\n'
            )'''
            ret.append([
                s[0]['station_train_code'].encode('utf-8'),
                s[i]['station_name'].replace(u'\ue244', u'\u78cf').replace(
                    u'\ue24d', u'\u6911').encode('utf-8'),
                s[i]['station_no'].encode('utf-8'),
                str(day),
                s[i]['start_time'].encode('utf-8'),
                '1'
            ])
    # return buf
    return ret


def checkSchdatebintocsv(train_arr, base_date, size, station=None):
    '''
    change train_arr[i]['service_type'] ['total_num']
    '''
    rows = []
    for train in train_arr:
        for retry in range(2):
            diff = get_last_one(train['date'], size)
            date = base_date  # TODO
            if diff > -1:
                date = date_add(base_date, diff)
            sch = processS(train, date, station)
            if len(sch):
                break
            time.sleep(1 << retry)
        train['total_num'] = len(sch)
        if len(sch):
            train['service_type'] = sch[0]['service_type']
        else:
            train['service_type'] = ""
        #if (train['station_train_code'] in train['train_no']) == False:
            #continue
        s = schDateToCsv(sch, train['src'], train['date'], base_date, size, station)
        for row in s:
            if len(row) >= 7:
                rows.append(row)
    return rows


def schDateToCsv(s, src, date_bin, base_date, size, station=None):
    # buf = ''
    ret = []
    day = 0
    last = 0
    val, _ = compress_bin_vector(
        date_bin,
        date_add(base_date, day),
        size
    )
    for i in range(0, len(s)):
        t1 = ''
        if station != None:
            t1 = telecode(s[i]['station_name'], station).encode('utf-8')
        if not t1:
            t1 = s[i]['station_name'].replace(u'\ue244', u'\u78cf').replace(u'\ue24d', u'\u6911').encode('utf-8')
        #
        if getmin(s[i]['arrive_time']) > -1 and i > 0:
            minute = getmin(s[i]['arrive_time'])
            if minute < last:
                day += 1
                val, _ = compress_bin_vector(
                    date_bin,
                    date_add(base_date, day),
                    size
                )
            last = minute
            ret.append([
                s[0]['station_train_code'].encode('utf-8'),
                t1,
                s[i]['station_no'].encode('utf-8'),
                str(day),
                s[i]['arrive_time'].encode('utf-8'),
                '0',
                val
                # str(src),
            ])
        #
        if getmin(s[i]['start_time']) > -1 and i < len(s)-1:
            minute = getmin(s[i]['start_time'])
            if minute < last:
                day += 1
                val, _ = compress_bin_vector(
                    date_bin,
                    date_add(base_date, day),
                    size
                )
            last = minute
            ret.append([
                s[0]['station_train_code'].encode('utf-8'),
                t1,
                s[i]['station_no'].encode('utf-8'),
                str(day),
                s[i]['start_time'].encode('utf-8'),
                '1',
                val
                # str(src),
            ])
    # return buf
    return ret


def checkSchdatebintocsvmin(train_arr, base_date, size, station=None):
    '''
    change train_arr[i]['service_type'] ['total_num']
    '''
    rows = []
    for train in train_arr:
        for retry in range(2):
            diff = get_last_one(train['date'], size)
            date = base_date  # TODO
            if diff > -1:
                date = date_add(base_date, diff)
            sch = processS(train, date, station)
            if len(sch):
                break
            time.sleep(1 << retry)
        train['total_num'] = len(sch)
        if len(sch):
            train['service_type'] = sch[0]['service_type']
        else:
            train['service_type'] = ""
        #if (train['station_train_code'] in train['train_no']) == False:
            #continue
        s = schDateToCsvMin(sch, train['src'], train['date'], base_date, size, station)
        rows.extend(s)
    return rows


def schDateToCsvMin(s, src, date_bin, base_date, size, station=None):
    '''
    use diff time to reduce size
    change train_arr[i]['service_type'] ['total_num']
    '''
    ret = []
    day = 0
    last = 0
    val, _ = compress_bin_vector(
        date_bin,
        date_add(base_date, day),
        size
    )
    for i in range(0, len(s)):
        t1 = ''
        if station != None:
            t1 = telecode(s[i]['station_name'], station).encode('utf-8')
        if not t1:
            t1 = s[i]['station_name'].replace(u'\ue244', u'\u78cf').replace(u'\ue24d', u'\u6911').encode('utf-8')
        #
        cross_day = 0
        stop_cross_day = 0
        if getmin(s[i]['arrive_time']) > -1 and i > 0:
            arrive_minute = getmin(s[i]['arrive_time'])
            if arrive_minute < last:
                day += 1
                val, _ = compress_bin_vector(
                    date_bin,
                    date_add(base_date, day),
                    size
                )
                cross_day = 1
            last = arrive_minute
        if getmin(s[i]['start_time']) > -1 and i < len(s)-1:
            start_minute = getmin(s[i]['start_time'])
            if start_minute < last:
                day += 1
                val, _ = compress_bin_vector(
                    date_bin,
                    date_add(base_date, day),
                    size
                )
                cross_day = 1
                stop_cross_day = 1
            last = start_minute
        stop_time = 0
        if i > 0 and i < len(s)-1:
            stop_time = getmin(s[i]['start_time']) - getmin(s[i]['arrive_time'])
            if stop_cross_day:
                stop_time += 1440
        if i > 0:
            run_time = getmin(s[i]['arrive_time']) - getmin(s[i-1]['start_time'])
            if run_time < 0:
                run_time += 1440
        ret.append([
            t1,
            #s[i]['station_no'].encode('utf-8'),
            str(run_time) if i > 0 else '',
            str(stop_time) if stop_time > 0 else s[i]['start_time'].encode('utf-8') if i < len(s)-1 else '',
            s[0]['station_train_code'].encode('utf-8') if i == 0 else '',
            str(day) if cross_day else '',
            val if cross_day or i == 0 else ''
            # str(src),
        ])
    return ret


# line
def openMilage(fn):
    m = readbyte(fn).decode('utf-8').split('\n')
    ret = []
    for i in range(len(m)):
        sp = m[i].replace('\r', '').split(' ')
        if len(sp) >= 2:
            ret.append(sp)
    return ret


def getkm(s, m, station=None):
    name = u''
    if station != None:
        name = teleToName(s, station)
    if len(name) == 0:
        name = s
    for i in range(len(m)):
        if len(m[i]) > 1 and name == m[i][0]:
            return int(m[i][1])
    return -1


def polylineClass(train_no):
    ret = 'polyline%s' % (
        train_no[:1]
    )
    if train_no[:2] in re.split(r'[\n,*]+', 'G4,D4,Z4,T3,K4') and len(train_no) == 5:
        ret += ' temp'
    if train_no[:2] in re.split(r'[\n,*]+', 'G8,G9,K5') and len(train_no) == 5:
        ret += ' peak'
    return ret


def schToPolyline(s, m):
    # (1440-x0)/x1=(y-y0)(y1-y) = k
    # (y-y0)=(y1-y)*(1440-x0)/x1
    # (y-y0)=(y1-y)*k
    # y=y0+y1*k-y*k
    # (1+k)y=y0+y1*k
    # y=(y0+y1*k)/(1+k)
    # k:
    # y=y0/(1+k)+y1*(1+k-1)/(1+k)
    # y=y0/(1+k)+y1-y1/(1+k)
    # y=(y0-y1)/(1+k)+y1
    # (lasty-y)/(1+(1440-lastx)/x)+y
    # (lasty-y)*x/((1440+x-lastx))+y
    # 1/k:
    # y=y0(1+k-k)/(1+k)+y1*k/(1+k)
    # y=y0-y0*k/(1+k)+y1*k/(1+k)
    # y=y0+(y1-y0)*k/(1+k)
    # y=y0+(y1-y0)*(1/(1/k))/((1/k)/(1/k)+(1/(1/k)))
    # y=y0+(y1-y0)*1/((1/k)+1)
    # lasty+(lasty-y)/(1+x/(1440-lastx))
    if (len(s)) <= 0:
        return ''
    buf = ''
    day = 0
    lastx = 0
    lasty = 0
    polyline_class = polylineClass(s[0]['station_train_code'].encode('utf-8'))
    buf += '<polyline name="%s" class="%s" points="' % (
        s[0]['station_train_code'].encode('utf-8'),
        polyline_class
    )
    for i in range(0, len(s)):
        y = getkm(s[i]['station_name'], m, station)
        x = getmin(s[i]['arrive_time'])
        if y > -1 and i > 0:
            if x < lastx:
                day += 1
                split_y = int(y) + int(x)*(int(lasty)-int(y)) / \
                    ((1440+int(x)-int(lastx)))
                buf += '%d,%d "/>\n<polyline name="%s+%d" class="%s" points="%d,%d ' % (
                    1440, split_y,
                    s[0]['station_train_code'].encode('utf-8'), day,
                    polyline_class,
                    0, split_y
                )
            lastx = x
            lasty = y
            buf += '%s,%s ' % (x, y)
        #
        x = getmin(s[i]['start_time'])
        if y > -1 and i < len(s)-1:
            if x < lastx:
                day += 1
                split_y = int(y) + int(x)*(int(lasty)-int(y)) / \
                    ((1440+int(x)-int(lastx)))
                buf += '%d,%d "/>\n<polyline name="%s+%d" class="%s" points="%d,%d ' % (
                    1440, split_y,
                    s[0]['station_train_code'].encode('utf-8'), day,
                    polyline_class,
                    0, split_y,
                )
            buf += '%s,%s ' % (x, y)
            lastx = x
            lasty = y
    buf += '"/>\n'
    return buf


def csvToPolyline(c, m, station=None):
    # ['K868,\xe6\xb3\x8a\xe5\xa4\xb4,05,1,00:00,0']
    if (len(c)) <= 0:
        return ''
    buf = ''
    day = 0
    lastx = 0
    lasty = 0
    lastdate = ''
    polyline_class = polylineClass(c[0][0])
    buf += '<polyline name="%s_%s" class="%s" points="' % (
        c[0][7].replace('&', ''),
        c[0][0],
        polyline_class
    )
    for i in range(0, len(c)):
        x = getmin(c[i][4])  # + (3 if int(c[i][5])>0 else (-2)) #
        y = getkm(c[i][1], m, station)
        date = c[i][7] if len(c[i]) > 7 else ''
        if y > -1:
            if x < lastx and lastx > -1 and lastdate == date:
                day += 1
                split_y = int(y) + int(x)*(int(lasty)-int(y)) / \
                    ((1440+int(x)-int(lastx)))
                buf += '%d,%d "/>\n<polyline name="%s_%s+%d" class="%s" points="%d,%d ' % (
                    1440, split_y,
                    date.replace('&', ''),
                    c[0][0], day, polyline_class,
                    0, split_y
                )
            if lastx == -1 or (lastdate != date and i > 0):
                day = 0
                buf += '"/>\n<polyline name="%s_%s+%d" class="%s" points="' % (
                    date.replace('&', ''),
                    c[0][0], day, polyline_class
                )
            buf += '%s,%s ' % (x, y)
        lastx = x
        lasty = y
        lastdate = date
    buf += '"/>\n'
    return buf


def csvToSvg(m, c, rule='', station=None):
    r = re.compile('^' + rule + '$', re.IGNORECASE | re.MULTILINE)
    maxlen = 90000
    arr = [[] for i in range(maxlen)]

    for i in range(len(c)):
        if len(c[i]) < 2:
            continue
        if getkm(c[i][1], m, station) > -1:
            # print(hash_no(c[i][0]))
            arr[hash_no(c[i][0])].append(c[i])
    #
    buf = ''
    buf += '<?xml version="1.0" standalone="no"?>\n'
    buf += '<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" \n'
    buf += '"http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">\n'
    buf += '<svg width="%s" height="%s" version="1.1" \n' % (
        1440,
        (int(m[-1][1])+50)//50*50
    )
    buf += 'xmlns="http://www.w3.org/2000/svg">\n'
    buf += '''
<style>
line,polyline {
  stroke-width:1
}
line.hour {
  stroke:rgb(128,128,128);
}
line.halfhour, line.station {
  stroke:rgb(220,220,220);
}
polyline {
  fill:none;opacity:0.8;
}
.polylineG {
  stroke:#3d668f;
}
.polylineD {
  stroke:#a80022;
}
.polylineC {
  stroke:#bf9540;
}
.polylineZ {
  stroke:#004a80;
}
.polylineT {
  stroke:#123da1;
}
.polylineK {
  stroke:#cc4c33;
}
.polyline1,
.polyline2,
.polyline3,
.polyline4,
.polyline5,
.polyline6,
.polyline7,
.polyline8,
.polyline9 {
  stroke: #305030
}
.temp{
  stroke-dasharray:10 2
}
.peak{
  stroke-dasharray:9 1 1 1
}
</style>

'''
    for i in range(24):
        buf += ('<line class="hour" x1="%d" y1="0" x2="%d" y2="3000" />\n' %
                (i*60, i*60))
        buf += ('<line class="halfhour" x1="%d" y1="0" x2="%d" y2="3000" />\n' %
                (i*60+30, i*60+30))

    for i in range(len(m)):
        buf += ('<text x="0" y="%d">%s %s</text>\n' %
                (int(m[i][1]) if int(m[i][1]) > 16 else (int(m[i][1]) + 16), m[i][0], m[i][1]))
        buf += ('<line class="station" x1="0" y1="%s" x2="1440" y2="%s" />\n' %
                (m[i][1], m[i][1]))
    #
    num = 0
    for i in range(maxlen):
        flag = 0
        if len(arr[i]) > 2:
            flag = 1
        if len(arr[i]) == 2:
            if arr[i][0][1] != arr[i][1][1]:
                flag = 1
        if flag and len(r.findall(arr[i][0][0])) > 0:
            num += 1
            arr[i] = sorted(arr[i], cmpby0_7_i2_i5_i3_m4) #py2
            buf += csvToPolyline(arr[i], m, station)
    #
    buf += ('</svg>')
    return buf, num


def train_list_class_str(t):
    s = ''
    for date in sorted(t.keys()):
        s += train_list_day_class_str(t[date], date) + '\n'
    return s


def train_list_day_class_str(d, date):
    ss = ''
    ss += (date.encode('utf-8'))
    for train_class in d:
        ss += '\t%s %d' % (
            train_class.encode('utf-8'),
            len(d[train_class])
        )
    # ss += '\n'
    return ss


def train_list_train_no_array(t, maxlen):
    arr = ['' for i in range(maxlen)]
    for date in sorted(t.keys()):
        for train_class in t[date]:
            # for train_class in ['Z']:
            for i in range(0, len(t[date][train_class])):
                # for i in range(0,1):
                a = t[date][train_class][i]
                match = re.findall(
                    r'(.*)\((.*)-(.*)\)',
                    a['station_train_code'],
                    re.I | re.M
                )[0]
                arr[hash_no(
                    match[0].encode('utf-8')
                ) - 1] = a['train_no'].encode('utf-8')
    return arr


# czxx
def getczxx(t1, date, cache=1):
    data = []
    samestations = []
    num = 0
    if cache >= 1:
        data, samestations, num = getczxxLocal(t1, date)
    if num > 0 or cache >= 2:
        return data, samestations, num
    if cache <= 1:
        data, samestations, num = getczxxOnline(t1, date)
    return data, samestations, num


def getczxxFileName(t1, date):
    return 'ticket%s/%s_%s.json' % (base_yymmdd(date), date, t1)


def getczxxLocal(t1, date):
    name = getczxxFileName(t1, date)
    try:
        fn = os.path.join(os.path.dirname(os.path.abspath(__file__)), name)
    except:
        fn = name
    if os.path.exists(fn):
        try:
            j = json.loads(readbyte(fn))
            if j['status'] == True and j['httpstatus'] == 200 and len(j['data']['data']):
                # print('%s %s %4d local' % (t1, date, len(j['data']['data'])))
                return j['data']['data'], j['data']['sameStations'], len(j['data']['data'])
        except ValueError:
            print('ValueError %s %s' % (t1, date))
            return [], [], 0
    return [], [], 0


def getczxxOnline(t1, date):
    # url = "https://kyfw.12306.cn/otn/czxx/query?train_start_date=" + date + \
    url = "https://www.12306.cn/kfzmpt/czxx/query?train_start_date=" + date + \
        "&train_station_name=" + "" + \
        "&train_station_code=" + t1 + "&randCode="
    header = {
        "User-Agent": "Netscape 5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36"}
    try:
        resp = requests.get(url, headers=header, timeout=55)
    except:
        print('Net Error %s %s' % (t1, date))
        return [], [], -1
    body = resp.content.decode('utf-8')  # bytes -> str (ucs2)
    try:
        j = json.loads(body)
    except ValueError:
        print('ValueError %s %s' % (t1, date))
        return [], [], -1
    name = getczxxFileName(t1, date)
    if j['status'] == True and j['httpstatus'] == 200 and len(j['data']['data']):
        writebyte(name, resp.content)
        print('%s %s %4d' % (t1, date, len(j['data']['data'])))
        return j['data']['data'], j['data']['sameStations'], len(j['data']['data'])
    else:
        print('data error %s %s' % (t1, date))
        return [], [], 0


def add_station(base_date, now, max_date_diff, size, totalcache=1):
    '''
    czxx
    '''
    # 97-98主要换乘站 北京 天津 沈阳 长春 通辽 哈尔滨 齐齐哈尔 大连 泰安 徐州 南京 上海 石家庄 郑州 武昌 长沙 株洲 广州 襄阳 柳州 贵阳 西安 兰州 成都
    # 京哈线及东北地区 京沪线及华东地区 京九线 京广线及中南地区 陇海线及西南、西北地区 宝成线及西南地区 侯月、京原、京包、南北同蒲
    # 1986年铁道部铁路局列表：
    # （1）哈尔滨铁路局，下属铁路分局7个：01哈尔滨、04齐齐哈尔、03牡丹江、02佳木斯、05海拉尔、04加格达奇、05伊图里河铁路分局。
    # （2）沈阳铁路局，下属铁路分局11个：12沈阳、13大连、12丹东、11长春、18吉林、19通化、20图们、16通辽、11白城、15锦州、15阜新铁路分局。
    # （3）北京铁路局，下属铁路分局6个：24北京、25天津、26石家庄、28大同、27太原、27临汾铁路分局。
    # （4）呼和浩特铁路局，下属铁路分局2个：33包头、36集宁铁路分局。
    # （5）郑州铁路局，下属铁路分局8个：38郑州、38新乡、39武汉、42襄樊、40洛阳、41西安、41宝鸡、43安康铁路分局。
    # （6）济南铁路局，下属铁路分局3个：47济南、48徐州、49青岛铁路分局。
    # （7）上海铁路局，下属铁路分局7个：55上海、54南京、53蚌埠、56杭州、57鹰潭、57南昌、58福州铁路分局。
    # （8）广州铁路局，下属铁路分局4个：63广州、62衡阳、62长沙、64怀化铁路分局。另有65广深铁路公司和6b海南铁路办事处。66 67广梅汕 69深圳西
    # （9）柳州铁路局，下属铁路分局2个：71柳州、71南宁铁路分局。
    # （10）成都铁路局，下属铁路分局6个：76成都、77重庆、78贵阳、76西昌、80昆明、开远铁路分局。
    # （11）兰州铁路局，下属铁路分局4个：85兰州、86武威、88西宁、87银川铁路分局。
    # （12）乌鲁木齐铁路局，下属铁路分局2个：93乌鲁木齐、92哈密铁路分局。 94南疆临管处、91北疆公司 95

    citys = re.split(r'[\r\n,*]+', readbyte('citys.txt').decode('utf-8'))
    samecity_arr = []
    samecity_map = {}
    import math
    # get data less than ex-2sd
    if False and totalcache < 2 and now != base_date: # TODO
        for name in citys:
            t1 = telecode(name, station)
            if len(t1) == 0:
                continue
            if name in samecity_map:
                continue
            rets = []
            for i in range(-1, max_date_diff):  # -8...32
                date = date_add(now, i)
                c, samecity, ret = getczxx(t1, date, cache=2)
                rets.append(ret)
                if len(samecity) > 1:
                    samecity_arr.append(samecity)
                    for ii in samecity:
                        samecity_map[ii] = name
            n = len(rets)
            ex = sum(rets)  # /n
            ex2 = sum([x*x for x in rets])  # /n
            sd = round(math.sqrt((ex2*n - ex * ex)) / n)
            level = round(ex/n) - 2*sd  # sorted(rets)[len(rets)//2]*8//10
            for i in range(len(rets)):
                if rets[i] < level:
                    print(t1, date_add(now, i-1), rets[i], level)
                    c, samecity, ret = getczxx(
                        t1, date_add(now, i-1), cache=0)
    #
    for i in range(-datediff(now, base_date), max_date_diff+3): # base_date...now+max_date_diff+2
        date = date_add(now, i)
        freq = re.split(r'[\s\n,*]+',
                        u'''北京 上海 广州 天津 沈阳 长春 哈尔滨 济南 徐州 南京 杭州 石家庄 郑州 武昌 长沙 株洲 贵阳 西安 兰州 成都 重庆
            深圳 南昌 福州 厦门 昆明 呼和浩特 西宁 乌鲁木齐 大连 青岛''')
        samecity_arr = []
        samecity_map = {}
        for name in citys:
            t1 = telecode(name, station)
            if len(t1) == 0:
                continue
            if name in samecity_map:
                continue
            if i > max_date_diff and name not in freq:
                continue
            fn = getczxxFileName(t1, date)
            mdate = '1970-01-01'
            if os.path.exists(fn):
                mdate = time.strftime("%Y-%m-%d", time.localtime(os.path.getmtime(fn)))
            cache = 1
            if i == 0:
                cache = 0
            if datediff(date, mdate) > max_date_diff:
                cache = 0
            if i < 0:  # min -8  #
                cache = 2
            if name in freq:
                if (0 <= i and i < 5):
                    cache = 0
                if (5 <= i and i < 14) and datediff(now, mdate) >= 2:
                    cache = 0
                if (14 <= i) and datediff(now, mdate) >= 3:
                    cache = 0
            if (-3 <= i and i <= 0) and datediff(date, mdate) > 0:
                cache = 0
            if (0 <= i) and datediff(now, mdate) >= max_date_diff-10:
                cache = 0
            if totalcache >= 2:
                cache = 2
            for retry in range(5):
                c, samecity, ret = getczxx(t1, date, cache)
                if ret > -1:
                    break
                time.sleep(1 << retry)
            if ret == -1:
                c, samecity, ret = getczxx(t1, date, cache=2)
            for t in c:
                diff = datediff(re.sub(
                    r'(\d\d\d\d)(\d\d)(\d\d)',
                    r'\1-\2-\3',
                    t['start_train_date']),
                    base_date
                )
                if diff < 0:
                    continue
                if diff >= size:
                    size = diff + 1
                s = {}
                s['station_train_code'] = t['station_train_code']
                s['from_station'] = t['start_station_name']
                s['to_station'] = t['end_station_name']
                s['train_no'] = t['train_no']
                s['total_num'] = 0
                s['date'] = 1 << diff
                s['src'] = 8
                add_map(train_map, s)
            if len(samecity) > 1:
                samecity_arr.append(samecity)
                for ii in samecity:
                    samecity_map[ii] = name
    return size


def findschstation(sch, station_name):  # TODO
    for i in range(len(sch)):
        if sch[i]['station_name'] == station_name:
            return 1
    return 0


def checkczxx(t1, date, cache=2):
    c, samecity, ret = getczxx(t1, date, cache)
    for i in range(len(c)):
        sch = getSch12306Local(c[i]['train_no'])
        if findschstation(sch, c[i]['station_name']) == 0:
            print('no station %s in %s' % (
                c[i]['station_name'].encode('utf-8'),
                c[i]['train_no'].encode('utf-8')
            ))
            getSch12306Online(
                c[i]['start_station_telecode'],
                c[i]['end_station_telecode'],
                c[i]['train_no'],
                date
            )


'''
checkczxx('WCN', '2020-04-09')
station = getStation()
for i in range(len(station)):
    if station[i][2][2] == 'N':
        checkczxx(station[i][2], date)
'''

# leftTicket
LeftTicketUrl = "leftTicket/query"


def getLeftTicket(t1, t2, date):
    url = "https://kyfw.12306.cn/otn/" + LeftTicketUrl + "?leftTicketDTO.train_date=" + date + \
        "&leftTicketDTO.from_station=" + t1 + \
        "&leftTicketDTO.to_station=" + t2 + "&purpose_codes=ADULT"
    header = {
        "User-Agent": "Netscape 5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36"}
    try:
        resp = requests.get(url, headers=header, timeout=50)
    except:
        print('Net Error %s %s %s' % (t1, t2, date))
        return []
    body = resp.content.decode('utf-8')  # bytes -> str (ucs2)
    try:
        ticket = json.loads(body)
    except ValueError:
        print('ValueError %s %s %s' % (t1, t2, date))
        return []
    name = 'ticket/%s_%s_%s.json' % (date, t1, t2)
    if ticket['status'] == True and ticket['httpstatus'] == 200 and len(ticket['data']['result']):
        writebyte(name, resp.content)
        print('%s %s %s %d' % (t1, t2, date, len(ticket['data']['result'])))
        return ticket['data']['result']
    else:
        print('data error %s %s %s' % (t1, t2, date))
        return []


def checkLeftTicket(t1, t2, date):
    ticket = getLeftTicket(t1, t2, date)
    for i in ticket['data']['result']:
        sp = i.split('|')
        if len(sp) > 38:
            print('%s %s %s %s' % (sp[3], sp[2], sp[4], sp[5]))
            if not os.path.exists('sch/'+sp[2].encode('utf-8')+'.json'):
                for retry in range(3):
                    s = getSch12306(sp[4], sp[5], sp[2], date)
                    if len(s):
                        break
                    time.sleep(1 << retry)
                # with open("20180808.csv","a") as f:
                # f.write(b);


'''
for date in ['2018-08-09','2018-08-10','2018-08-11','2018-08-12','2018-08-13','2018-08-14','2018-08-15']:
  print(date);
  checkLeftTicket('BJP','TJP',date);
  checkLeftTicket('TJP','BJP',date);
  checkLeftTicket('TJP','YKP',date);
  checkLeftTicket('YKP','TJP',date);

for date in ['2018-11-20','2018-11-21','2018-11-22','2018-11-23','2018-11-24','2018-11-25','2018-11-26','2018-11-27','2018-11-28','2018-11-29']:
  print(date);
  checkLeftTicket('HBB','SYT',date);
  checkLeftTicket('SYT','HBB',date);
  checkLeftTicket('DLT','SYT',date);
  checkLeftTicket('SYT','DLT',date);
  checkLeftTicket('BJP','SYT',date);
  checkLeftTicket('SYT','BJP',date);
  checkLeftTicket('TJP','SYT',date);
  checkLeftTicket('SYT','TJP',date);

# https://kyfw.12306.cn/otn/leftTicket/query?leftTicketDTO.train_date=2018-08-11&leftTicketDTO.from_station=BJP&leftTicketDTO.to_station=TJP&purpose_codes=ADULT

'''


# wifi.12306.cn
def getstation(tele, date):
    name = 'station/station_%s_%s.json' % (tele, date)
    try:
        fn = os.path.join(os.path.dirname(os.path.abspath(__file__)), name)
    except:
        fn = name
    if os.path.exists(fn):
        try:
            j = json.loads(readbyte(fn))
            print('read wifi_station %s %s %d' % (tele, date, len(j['data'])))
            return j['data'], 0
        except:
            print('read wifi_station %s %s error' % (tele, date))
    url = "https://wifi.12306.cn/wifiapps/ticket/api/stoptime/queryByStationCodeAndDate?stationCode=%s&trainDate=%s" % (
        tele, date
    )
    header = {
        "User-Agent": "MicroMessenger",
    }
    try:
        resp = requests.get(url, headers=header, timeout=30)
    except:
        print('Net Error %s %s' % (tele, date))
        return [], -1
    body = resp.content.decode('utf-8')  # bytes -> str (ucs2)
    # print(body)
    try:
        j = json.loads(body)
    except:
        print('ValueError %s %s' % (tele, date))
        return [], -1
    if 'data' in j:
        print('wifi_station %s %s %d' % (tele, date, len(j['data'])))
        writebyte(name, resp.content)
        return j['data'], 0
    return [], 0


def getdetail(tele, no, date, cache=1):
    '''
    dmin dmax yyyymmdd
    ret
    >0 station num
    -1 error
    -2 over_limit
    -3 unknown
    '''
    name = 'detail/detail_' + no + '.json'
    try:
        fn = os.path.join(os.path.dirname(os.path.abspath(__file__)), name)
    except:
        fn = name
    if cache > 0 and os.path.exists(fn):
        try:
            j = json.loads(readbyte(fn))
            if 'data' in j:
                return j['data']['stopTime'][0]['startDate'], j['data']['stopTime'][0]['stopDate'], len(j['data']['stopTime'])
        except:
            print('read wifi_station %s %s error' % (tele, date))
    if cache >= 2:
        return date, date, -1
    code = re.sub(r'^0+', "", no[2:10])
    if code[0] in 'GDC':
        code = 'T'
    url = "https://wifi.12306.cn/wifiapps/appFrontEnd/v2/kpBigScreen/getBigScreenTrainDetail?stationCode=%s&stationTrainCode=%s&trainDate=%s&fullTrainCode=%s" % (
        tele, code, date, no
    )
    # print(url)
    header = {
        "User-Agent": "MicroMessenger",
    }
    try:
        resp = requests.get(url, headers=header, timeout=30)
    except:
        print('Net Error %s %s %s' % (tele, date, no))
        return date, date, -1
    body = resp.content.decode('utf-8')  # bytes -> str (ucs2)
    time.sleep(0.05)
    # print(body)
    try:
        j = json.loads(body)
    except ValueError:
        print('ValueError %s %s' % (date, no))
        return date, date, -1
    if 'data' in j:
        writebyte(name, resp.content)
        #print('%s %s %s %d' % (no, len(j['data']['stopTime'])))
        if 'stopTime' in j['data'] and len(j['data']['stopTime']) > 0:
            ret = [
                j['data']['stopTime'][0]['trainNo'],
                j['data']['stopTime'][0]['stationTelecode'],
                j['data']['stopTime'][-1]['stationTelecode'],
                j['data']['stopTime'][0]['startDate'],
                j['data']['stopTime'][0]['stopDate'],
            ]
            if 'trainsetTypeInfo' in j['data']:
                # ret.append(j['data']['trainsetTypeInfo']['trainsetType'])
                ret.append(re.sub(r'\D', '', j['data']['trainsetTypeInfo']['capacity']))
                if 'trainsetTypeName' in j['data']['trainsetTypeInfo']:
                    ret.append(j['data']['trainsetTypeInfo']['trainsetTypeName'])
            print(' '.join(ret))
        return j['data']['stopTime'][0]['startDate'], j['data']['stopTime'][0]['stopDate'], len(j['data']['stopTime'])
    else:
        if 'error' in j:
            print('trydetail(\'%s\',\'%s\',\'%s\') data error %s' % (tele, no, date, j['error']))
            if j['error'] == u'发到站信息不完整':
                return date, date, -1
            if j['error'] == u'查询异常,请重试':
                return date, date, -1
            return date, date, -2
        print('trydetail(\'%s\',\'%s\',\'%s\') no data' % (tele, no, date))
        return date, date, -3


def trydetail(s, no, date, add=-1):
    ans = 0
    #s = 'BJP'
    #no = '24000014611P'
    #date = '20171220'
    dmin = date
    dmax = date
    ret = 0
    correct = 1
    while correct > 0:  # ret >= 0:
        dmin, dmax, ret = getdetail(s, no, date, cache=0)
        if ret > 0:
            getcompilelist(no)
        if ret <= -2:
            return dmin, dmax, ret
        if ret > 0:
            ans += 1
            if add < 0:
                date = date_add_ymd(dmin, add)
            if add > 0:
                date = date_add_ymd(dmax, add)
            correct += 1
        else:
            correct >>= 1
        if add >= 0 and datediff(re.sub(r'(\d\d\d\d)(\d\d)(\d\d)', r"\1-\2-\3", dmax), '2020-12-31') > 0:
            return dmin, dmax, ans
        if add < 0 and no[11] == '0':
            if no[10] == '0':
                return dmin, dmax, ans
            break
        no, _ = no_add(no, add)
        time.sleep(0.3)
    return dmin, dmax, ans


def trycompile(s, no, l=6):
    errcnt = 0
    for c in '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'[:l]:
        compile = getcompilelist((no[:-1] + '%s') % (c))
        if len(compile):
            errcnt = 0
        else:
            errcnt += 1
        #if errcnt > 4:
            #break
        name = 'detail/detail_' + (no[:-1] + '%s') % (c) + '.json'
        try:
            fn = os.path.join(os.path.dirname(os.path.abspath(__file__)), name)
        except:
            fn = name
        if os.path.exists(fn):
            continue
        if len(compile) > 3:
            dmin, dmax, ret = getdetail(s, (no[:-1] + '%s') % (c), compile[3], cache=0)
            if ret > 0:
                continue
            getdetail(s, (no[:-1] + '%s') % (c), compile[4], cache=0)


def tryzero(s, no, date, l=6):
    dmin = date
    dmax = date
    ret = 1
    while ret > 0:
        for c in '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'[:l]:
            dmin, dmax, ret = trydetail(s, (no[:-1] + '%s') % (c), date)
            if ret > 0:
                #print(dmin, dmax, ret)
                break
            if ret <= -2:
                return dmin, dmax, ret
        if ret <= 0:
            return dmin, dmax, ret
        if no[10] == '0':
            return dmin, dmax, ret
        add = -1
        no, _ = no2_add(no, add)
        date = date_add_ymd(dmin, add)


def getcompilelist(no, cache=1):
    if len(no) < 12:
        return []
    name = 'list/list_' + no + '.json'
    try:
        fn = os.path.join(os.path.dirname(os.path.abspath(__file__)), name)
    except:
        fn = name
    if cache > 0 and os.path.exists(fn):
        try:
            j = json.loads(readbyte(fn))
            if 'data' in j:
                ret = [
                    no,
                ]
                ret.append(seatcaps(
                    [re.sub(r'\s', '', x['coachType']) for x in j['data']],
                    [str(x['limit1'] + x['limit2']) for x in j['data']]
                ))
                ret.append('|'.join(list(set([x['seatFeature'] for x in j['data']]))) )
                ret.append(j['data'][0]['startDate'])
                ret.append(j['data'][0]['stopDate'])
                #print(' '.join(ret))
                return ret
        except:
            print('json error %s' % (no))
    if cache >= 2:
        return []
    url = "https://wifi.12306.cn/wifiapps/ticket/api/trainDetailInfo/queryTrainCompileListByTrainNo?trainNo=%s" % (
        no
    )
    header = {
        "User-Agent": "MicroMessenger",
    }
    try:
        resp = requests.get(url, headers=header, timeout=30)
    except:
        print('Net Error %s' % (no))
        return []  # ,-1
    body = resp.content.decode('utf-8')  # bytes -> str (ucs2)
    # print(body)
    try:
        j = json.loads(body)
    except ValueError:
        print('ValueError %s' % (no))
        return []  # ,-1
    time.sleep(0.1)
    if 'data' in j:
        writebyte(name, resp.content)
        ret = [
            no,
        ]
        ret.append(seatcaps(
            [re.sub(r'\s', '', x['coachType']) for x in j['data']],
            [str(x['limit1'] + x['limit2']) for x in j['data']]
        ))
        ret.append('|'.join(sorted(list(set([x['seatFeature'] for x in j['data']])))) )
        ret.append(j['data'][0]['startDate'])
        ret.append(j['data'][0]['stopDate'])
        print(' '.join(ret))
        return ret
    else:
        print('compilelist %s no data' % (no))
        return []


'''
import time
c = readcsv('js/train_detail.csv')
for i in range(0, len(c), 1):
    if len(c[i]) < 5:
        continue
    name = 'list/list_' + c[i][0] + '.json'
    try:
        fn = os.path.join(os.path.dirname(os.path.abspath(__file__)), name)
    except:
        fn = name
    #if os.path.exists(fn):
        #continue
    ret = getcompilelist(c[i][0], 2)
    if len(ret) > 2 and '|' in ret[2]:
        print(' '.join(ret))
'''


def getequip(no, date):
    if len(no) < 12:
        return
    name = 'equip/equip_' + date + '_' + no + '.json'
    try:
        fn = os.path.join(os.path.dirname(os.path.abspath(__file__)), name)
    except:
        fn = name
    ret = [
        no,
        u'',
        u'',
        u'',
        u'',
        u'',
        u'',
        u'',
        u'',
    ]
    if os.path.exists(fn):
        try:
            j = json.loads(readbyte(fn))
            if 'data' in j:
                ret = [
                    no,
                    j['data'][0]['trainsetType'],
                    j['data'][0]['trainsetName'],
                    j['data'][0]['bureaName'],
                    j['data'][0]['deploydepotName'],
                    j['data'][0]['depotName'],
                    j['data'][0]['trainsetStatus'],
                    j['data'][0]['date'],
                    str(j['data'][0]['eId']),
                ]
                #print(' '.join(ret))
                return ret, 0
        except:
            pass
    url = "https://wifi.12306.cn/wifiapps/ticket/api/trainDetailInfo/queryTrainEquipmentByTrainNo?trainNo=%s" % (
        no
    )
    header = {
        "User-Agent": "MicroMessenger",
    }
    try:
        resp = requests.get(url, headers=header, timeout=30)
    except:
        print('Net Error %s' % (no))
        return ret, -1
    body = resp.content.decode('utf-8')  # bytes -> str (ucs2)
    # print(body)
    time.sleep(0.1)
    try:
        j = json.loads(body)
    except ValueError:
        print('ValueError %s' % (no))
        return ret, -1
    if 'data' in j:
        writebyte(name, resp.content)
        ret = [
            no,
            j['data'][0]['trainsetType'],
            j['data'][0]['trainsetName'],
            j['data'][0]['bureaName'],
            j['data'][0]['deploydepotName'],
            j['data'][0]['depotName'],
            j['data'][0]['trainsetStatus'],
            j['data'][0]['date'],
            str(j['data'][0]['eId']),
        ]
        #print(' '.join(ret))
        return ret, 0
    else:
        print('equip %s no data' % (no))
        return ret, 0

#getequip('6c00000G6605', date)


def getpreseq(code, date):
    name = 'preseq/preseq_' + date + '_' + code + '.json'
    try:
        fn = os.path.join(os.path.dirname(os.path.abspath(__file__)), name)
    except:
        fn = name
    url = "https://wifi.12306.cn/wifiapps/ticket/api/trainDetailInfo/queryPreseqTrainsByTrainCode?trainCode=%s" % (
        code
    )
    # print(url)
    header = {
        "User-Agent": "MicroMessenger",
    }
    try:
        resp = requests.get(url, headers=header, timeout=30)
    except:
        print('Net Error %s' % (code))
        return date, date, -1
    body = resp.content.decode('utf-8')  # bytes -> str (ucs2)
    # print(body)
    try:
        j = json.loads(body)
    except ValueError:
        print('ValueError %s' % (code))
        return date, date, -1
    if 'data' in j:
        writebyte('preseq/preseq_' + date + '_' + code + '.json', resp.content)
        print(j['data'])
        return j['data']
    else:
        if 'error' in j:
            print('preseq %s data error %s' % (code, j['error']))
            return date, date, -2
        print('preseq %s no data' % (code))
        return ''


def getcdinfo(date, s, cache=2):
    yyyymmdd = re.sub(
        r'(\d\d)(\d\d)-(\d+)-(\d+)',
        r"\1\2\3\4",
        date
    )
    name = 'ccrgt/ccrgt_' + yyyymmdd + '_' + s + '.json'
    try:
        fn = os.path.join(os.path.dirname(os.path.abspath(__file__)), name)
    except:
        fn = name
    if os.path.exists(fn):
        try:
            j = json.loads(readbyte(fn))
            ret = [
                s.encode('utf-8'),
                '%s(%d)' % (
                    j['data']['trainType'].encode('utf-8'),
                    sum([int(re.sub(r'\D', '', x['peopleNum']))
                         for x in j['data']['cdInfoList']])
                ),
                re.sub(u'中国铁路(.*)局动车段', r'\1',
                       j['data']['fixDepart']).encode('utf-8'),
                re.sub(u'中国铁路(.*)局客运段', r'\1',
                       j['data']['serverDepart']).encode('utf-8'),
                re.sub(u'(.*)节动力车，(.*)节非动力车', r'\1M\2T',
                       j['data']['trainTeam']).encode('utf-8'),
                seatcapsccrgt(
                    [(x['seatType1'] if x['seatType1'] else '') +
                     (x['seatType2'] if x['seatType2'] else '') +
                     (x['dinnerCar'] if x['dinnerCar'] else '') for x in j['data']['cdInfoList']],
                    [re.sub(r'\D', '', x['peopleNum'])
                     for x in j['data']['cdInfoList']]
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
    j = {"params": {"date": date, "trainNumber": s}}
    header = {
        "User-Agent": "Netscape 5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36",
        "Content-Type": "application/json"
    }
    try:
        resp = requests.post(url, data=json.dumps(j),
                             headers=header, timeout=20)
    except:
        print('net error %s' % (s))
        return [s.encode('utf-8'), "", "", "", "", ""], -3
    body = resp.content.decode('utf-8')
    time.sleep(0.2)
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
                sum([int(re.sub(r'\D', '', x['peopleNum']))
                     for x in j['data']['cdInfoList']])
            ),
            re.sub(u'中国铁路(.*)局动车段', r'\1',
                   j['data']['fixDepart']).encode('utf-8'),
            re.sub(u'中国铁路(.*)局客运段', r'\1',
                   j['data']['serverDepart']).encode('utf-8'),
            re.sub(u'(.*)节动力车，(.*)节非动力车', r'\1M\2T',
                   j['data']['trainTeam']).encode('utf-8'),
            seatcapsccrgt(
                [(x['seatType1'] if x['seatType1'] else '') +
                 (x['seatType2'] if x['seatType2'] else '') +
                 (x['dinnerCar'] if x['dinnerCar'] else '') for x in j['data']['cdInfoList']],
                [re.sub(r'\D', '', x['peopleNum'])
                 for x in j['data']['cdInfoList']]
            ).encode('utf-8'),
        ]
        # for r in ret:
        # print(type(r))
        # print((','.join(ret)).decode('utf-8'))
        writebyte(name, resp.content)
        return ret, 0
    # except:
    else:
        print('%s -' % (s))
        return [s.encode('utf-8'), "", "", "", "", ""], -1
    return j, 0


def ccrgtcsv(name, date):
    #name = 'js/train%s.csv'%(base_yymmdd())
    try:
        fn = os.path.join(os.path.dirname(os.path.abspath(__file__)), name)
    except:
        fn = name
    yyyymmdd = re.sub(
        r'(\d\d)(\d\d)-(\d+)-(\d+)',
        r"\1\2\3\4",
        date
    )
    c = readcsv(fn)
    idx = 0
    map = {}
    ret = []
    for i in range(idx, len(c), 1):
        if len(c[i]) <= 3 or c[i][3] in map:
            continue
        if len(c[i]) < 7:
            c[i].append('')
            c[i].append('')
        if not is_a_day(c[i][6], yyyymmdd):
            continue
        if c[i][3][0] in 'GDCS':
            # print(c[i][3])
            cache = 1
            row = []
            for retry in range(3):
                row, status = getcdinfo(date, c[i][3], cache)
                if status >= -1:
                    break
            ret.append([x for x in row])
            # print(','.join(row))
            idx = i + 1
            map[c[i][3]] = 1
    return ret


# gtzwd
def gtzwdjsp():
    url = 'http://www.gtbyxx.com/wxg/ky/zhengwan.jsp'
    header = {
        "User-Agent": "Netscape 5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36"}
    resp = requests.get(url, headers=header, timeout=20)
    body = resp.content.decode('utf-8')
    match = re.findall(u'更新时间为(\\d+)月(\\d+)日 (\\d+)点(\\d+)分',
                       body, re.I | re.M)[0]
    ret = '%s-%s %s:%s' % (
        match[0],
        match[1],
        match[2],
        match[3]
    )
    return ret.encode('utf-8')


def gtzwd(date, s):
    url = 'http://www.gtbyxx.com/wxg/inter/kyData/getTrainZwd'
    j = {"trainNo": s}
    header = {
        "User-Agent": "Netscape 5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36"}
    resp = requests.post(url, data=json.dumps(j), headers=header, timeout=60)
    body = resp.content.decode('utf-8')
    #
    try:
        j = json.loads(body)
    except:
        print(body)
    name = 'gtzwd/gt_' + date + '_' + s + '.json'
    writebyte(name, resp.content)
    return j


'''
gtzwdjsp()
gtzwd('2019-03-12', 'z')
gtzwd('2019-03-12', 't')
gtzwd('2019-03-12', 'k')
gtzwd('2019-03-12', 'g')
gtzwd('2019-03-12', 'd')
gtzwd('2019-03-12', 'c')
gtzwd('2019-03-12', 'y')
'''


def mark_json_slice(data):
    ret = []
    layer = 0
    index = 0
    # kv = 0
    lastq = -1
    lastcolon = -1
    lastkey = ''
    quot = 0
    while index < len(data):
        c = data[index]
        if c == "{":
            # if layer == 1:
            # print("%s %d"%(data[index],index))
            # kv = 0
            layer += 1
        elif c == "[":
            layer += 1
        elif c == "}":
            if layer == 1:
                # print("%s %d"%(data[index],index))
                # kv = 0
                # print("%s %d %d %s %s" % (lastkey, lastcolon+1, index, data[lastcolon+1], data[index-1]))
                ret.append([lastkey, lastcolon+1, index])
            layer -= 1
        elif c == "]":
            layer -= 1
        elif c == ":":
            if layer == 1:
                # print("%s %d"%(data[index],index))
                # kv = 1
                lastcolon = index
        elif c == ",":
            if layer == 1:
                # print("%s %d"%(data[index],index))
                # kv = 0
                # print("%s %d %d %s %s" % (lastkey, lastcolon+1, index, data[lastcolon+1], data[index-1]))
                ret.append([lastkey, lastcolon+1, index])
        elif c == '"':
            if layer == 1:
                # print("%s %d %d"%(data[index],index,quot))
                if quot == 0:
                    lastq = index
                    quot = 1
                elif quot == 1:
                    # print("%s"%(data[lastq+1:index]))
                    lastkey = data[lastq+1:index]
                    quot = 0
        index += 1
    return ret


# compress trsin_list.js
def bin_cnt(x):
    ans = 0
    while x:
        x &= x - 1
        ans += 1
    return ans


def all1(size):
    ans = 0
    while size:
        size -= 1
        ans |= 1 << size
    return ans


def all01(size, y, c):
    ans = 0
    ii = 0
    while ii < size:
        ans |= c << ii
        ii += y
    return ans


def bin_count1n(n, step=1):
    ans = 0
    temp = n
    while temp:
        ans += 1
        # print('{:0>45b}'.format(temp))
        temp &= temp >> step
    return ans


def try_step(bin):
    max_consecutive = 0
    max_step = 1
    for step in [7, 2, 3, 4, 5, 6, 1]:
        consecutive = bin_count1n(bin, step)
        #print('try %d %d' % (step, consecutive))
        if consecutive > max_consecutive:
            max_consecutive = consecutive
            max_step = step
    return max_step, max_consecutive


def left7(c, base_week):
    c <<= base_week
    c |= c >> 7
    c &= 0x7f
    return c


def cycle7(c, base_week):
    model = '71234567'
    ret = ''
    c = left7(c, base_week)
    if c == 0b01000001:
        return '67'
    if c == 0b01100011:
        return '5671'
    if c == 0b01100001:
        return '567'
    if c == 0b01000011:
        return '671'
    if c == 0b00100001:
        return '57'
    for i in range(7):
        if c & (1 << i):
            ret += model[i]
    return ret


def get_one_slice(n, size, offset=0, step=1):
    ret = []
    a = -1
    b = -1
    status = 0
    for i in range(offset, size, step):
        if n & (1 << i):
            # print('1 %d %d'%(status,i))
            if status == 0:
                a = i
            b = i
            status = 1
        else:
            # print('0 %d %d'%(status,i))
            if status == 1:
                ret.append([a, b])
            status = 0
    if status == 1:
        ret.append([a, b])
    return ret


def get_mask_one_slice(n, size, c=1, step=1):
    ret = []
    a = -1
    b = -1
    status = 0
    for i in range(0, size, 1):
        if c & (1 << (i % step)) == 0:
            #print('--- %d'%(i))
            continue
        if n & (1 << i):
            #print('1 %d %d'%(status,i))
            if status == 0:
                a = i
            b = i
            status = 1
        else:
            #print('0 %d %d'%(status,i))
            if status == 1:
                ret.append([a, b])
            status = 0
    if status == 1:
        ret.append([a, b])
    return ret


def get_first_one(n, size):
    for i in range(size):
        if n & (1 << i):
            return i
    return -1


def get_last_one(n, size):
    ret = -1
    for i in range(size):
        if n & (1 << i):
            ret = i
    return ret


def get_zero_slice(n, size, offset=0, step=1):
    ret = []
    a = -1
    b = -1
    status = 1
    for i in range(offset, size, step):
        if n & (1 << i):
            # print('0 %d %d'%(status,i))
            if status == 0:
                ret.append([a, b])
            status = 1
        else:
            # print('1 %d %d'%(status,i))
            if status == 1:
                a = i
            b = i
            status = 0
    if status == 0:
        ret.append([a, b])
    return ret


# remove prefix 2 4 6 of s1 same for s0
def gettail(s1, s0):
    if len(s0) < 8 or len(s1) < 8:
        return s1
    for idx in range(6, 0, -2):
        if s1[0:idx] == s0[0:idx]:
            return s1[idx:]
    return s1


def slice_to_str(ret, base_date):
    ans = ''
    yyyymmdd = '20000000'
    for i in range(len(ret)):
        if i > 0:
            ans += "|"
        if ret[i][0] == ret[i][1]:
            cur_ymd = re.sub(r'(\d\d)(\d\d)-(\d+)-(\d+)',
                             r"\1\2\3\4",
                             date_add(base_date, ret[i][0]))
            tail = gettail(cur_ymd, yyyymmdd)
            yyyymmdd = cur_ymd
            ans += tail
            continue
        else:
            cur_ymd = re.sub(r'(\d\d)(\d\d)-(\d+)-(\d+)',
                             r"\1\2\3\4",
                             date_add(base_date, ret[i][0]))
            tail0 = gettail(cur_ymd, yyyymmdd)
            yyyymmdd = cur_ymd
            cur_ymd = re.sub(r'(\d\d)(\d\d)-(\d+)-(\d+)',
                             r"\1\2\3\4",
                             date_add(base_date, ret[i][1]))
            tail1 = gettail(cur_ymd, yyyymmdd)
            yyyymmdd = cur_ymd
            ans += '%s-%s' % (
                tail0,
                tail1
            )
    return ans


def compress_bin_vector(date_bin, base_date, size):
    date_bin &= all1(size)
    if date_bin & all1(size) == all1(size):
        return "", 1
    #
    #step, _ = try_step(date_bin)
    #
    min = size
    c = 0b1111111
    step = 1
    ret_mask_one_slice = [[0, size-1]]
    for cur_step in [1, 2, 3, 4, 5, 6, 7]:
        cur_c = 0
        for offset in range(cur_step):
            if date_bin & all01(size, cur_step, 1 << offset) == 0:
                continue
            cur_c |= 1 << offset
        if date_bin == (all1(size) & all01(size, cur_step, cur_c)):
            if cur_step == 7:
                return 'w' + cycle7(cur_c, weekday(base_date)), cur_step
            if cur_c == 0b01 and cur_step == 2:
                return "双", 2
            if cur_c == 0b10 and cur_step == 2:
                return "单", 2
            return ('b{:0>%db}' % (cur_step)).format(cur_c), cur_step
        if cur_step > 1 and cur_c == (1 << cur_step) - 1:
            continue
        mask_one_slice = get_mask_one_slice(date_bin, size, cur_c, cur_step)
        if len(mask_one_slice) < min:
            min = len(mask_one_slice)
            step = cur_step
            c = cur_c
            ret_mask_one_slice = mask_one_slice
    #
    # print(('{:0>%db}'%(ret_step)).format(ret_c))
    # print(ret_mask_one_slice)
    if c == 0b01 and step == 2:
        return "双&" + slice_to_str(ret_mask_one_slice, base_date), step + 7
    if c == 0b10 and step == 2:
        return "单&" + slice_to_str(ret_mask_one_slice, base_date), step + 7
    if step >= 2 and bin_count1n(date_bin, step) >= 3 and len(ret_mask_one_slice) <= 3:
        if step == 7:
            return 'w%s&' % (cycle7(c, weekday(base_date))) + slice_to_str(ret_mask_one_slice, base_date), step + 7
        return ('b{:0>%db}&' % (step)).format(c) + slice_to_str(ret_mask_one_slice, base_date), step + 7
    #
    bin_weight = bin_cnt(date_bin)
    if bin_weight <= 3:  # <size / 7
        return slice_to_str(get_one_slice(date_bin, size), base_date), 17
    one_slice = get_one_slice(date_bin, size)
    zero_slice = get_zero_slice(date_bin, size)
    if len(one_slice) <= len(zero_slice):
        if len(one_slice) <= 4:
            return slice_to_str(one_slice, base_date), 15
    else:
        if len(zero_slice) <= 1 and len(zero_slice) > 0:
            return "!" + slice_to_str(zero_slice, base_date), 16
    if bin_weight > size - size / 7 and len(zero_slice) > 0:
        return "!" + slice_to_str(zero_slice, base_date), 18
    #
    # ('b{:0>%db}' % (size)).format(date_bin) + ' consecutive' + str(bin_count1n(date_bin)), 0
    return slice_to_str(one_slice, base_date), 0

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'basedate':
        print(base_yymmdd())
        exit()

    station = getStation()
    totalcache = 1

    if len(sys.argv) > 1 and sys.argv[1] == 'station':
        writecsv("js/station.csv", [[col.encode('utf-8') for col in row] for row in station])
        writecsv("js/station.min.csv", [[row[x].encode('utf-8') for x in [1,2,6]] for row in station])
        exit()

    if len(sys.argv) > 2 and sys.argv[1] == 'search':
        date = sys.argv[2]
        print('search ', date)
        maxlen = 90000
        train_map = [[] for i in range(maxlen)]
        st = ["S", "C", "D", "G", "", "K", "Y", "P", "T", "Z"]
        st, tmpsize = searchAll12306(train_map, basedate(''), date, st, cache=0)
        print(date, st)
        exit()

    if len(sys.argv) > 1 and sys.argv[1] == 'cache':
        print('set totalcache=2')
        totalcache = 2

    maxlen = 90000
    train_map = [[] for i in range(maxlen)]
    #
    now = nowdate()
    base_date = basedate('')
    #end_date = ''
    #
    #train_list.js
    #base_date, mask, msg = add_train_list(train_map, fn0, '2019-12-30')
    size = 0  # bin_cnt(mask)
    max_date_diff = 15 #5 # 15  # 29 #T+29 #可以查到全部车次的日期
    #
    #czxx
    tmpsize = add_station(base_date, now, max_date_diff, size, totalcache=1) # totalcache=1 tmp 2
    if tmpsize > size:
        size = tmpsize
    #search
    #for i in range(max_date_diff+2, -1, -1):
    for i in range(-datediff(now, base_date), max_date_diff+1):
        st = ["S", "C", "D", "G", "", "K", "Y", "P", "T", "Z"]
        #st = ["90", "50", "10", "S", "C", "D", "G", "", "K", "Y", "P", "T", "Z"]
        #st = ["D9", "G9", "3", "T", "Z", "K5", "K4", "D4", "G4"]
        date = date_add(now, i)
        #diff = datediff(date, base_date)
        #if diff >= size:
        #    size = diff + 1
        cache = 1
        if i == 0:
            cache = 0
        if i < 0:
            cache = 2
        if totalcache >= 2:
            cache = 2
        for retry in range(3):
            st, tmpsize = searchAll12306(train_map, base_date, date, st, cache)
            time.sleep(30)
            if tmpsize > size:
                size = tmpsize
            if len(st) == 0:
                break
            time.sleep(310) # 2 << retry
        print(date, st)
    #stat
    print('base_date %s size %d' % (base_date, size))
    stat, train_num = hash_no_stat_block(train_map, 100, maxlen)
    #
    train_arr = mapToArr(train_map)
    #
    ret = checkSchdatebintocsvmin(train_arr, base_date, size, station)
    num = writemincsv('js/time%s.min.csv'%(base_yymmdd()), ret)
    print(num)
    #
    ret = checkSchdatebintocsv(train_arr, base_date, size, station)
    num = writecsv('js/time%s.csv'%(base_yymmdd()), ret)
    print(num)
    #
    ret = trainlistCsv(train_arr, base_date, size, station)
    writemincsv('js/train%s.csv'%(base_yymmdd()), ret)
    #
    s, block = print_block(stat)
    writebytebom("stat_map.txt", '%d trains\n%d blocks\n%s' % (train_num,block,s))

r'''
from view_train_list import *

station = getStation()

lines = [
[u'京沪高速线', r'(?!G7[012356]\d{1,3})[G]\d{1,4}|(?!D7\d{1,3})[D]\d{1,4}'],
[u'京广高速线', r'[GDC]\d{1,4}'],
[u'沪昆高速线', r'[GDC]\d{1,4}'],
[u'京包高速线', r'[GDC]\d{1,4}|S\d{1,4}'],
[u'京哈高速线', r'[G9]\d{2}|G3[67]\d{2}'],
[u'京沪线', r'[ZTKPQWY]\d{1,4}|^\d{1,4}|D7\d{1,3}'],
[u'京广线', r'[ZTKPQWY]\d{1,4}|C7[01]\d{2}|D75\d{2}|D6[67]\d{2}'],
[u'京九线', r'[ZTKPQWY]\d{1,4}|^\d{1,4}'],
[u'京哈线', r'[ZTKPQWYD]\d{1,4}|^\d{1,4}'],
[u'丰沙京包包兰线', r'[ZTKPQWY]\d{1,4}|^\d{1,4}'],
[u'京承线', r'[ZTKPQWY]\d{1,4}|^\d{1,4}'],
[u'京通线', r'[ZTKPQWY]\d{1,4}|^\d{1,4}'],
[u'京原线', r'[ZTKPQWY]\d{1,4}|^\d{1,4}'],
[u'陇海线', r'[ZTKPQWY]\d{1,4}|^\d{1,4}'],
[u'兰新线', r'[ZTKPQWY]\d{1,4}|^\d{1,4}'],
[u'兰青青藏线', r'[ZTKPQWY]\d{1,4}|^\d{1,4}'],
[u'沪昆线', r'[ZTKPQWY]\d{1,4}|^\d{1,4}'],
[u'太新线', r'[ZTKPQWY]\d{1,4}|^\d{1,4}'],
[u'焦柳线', r'[ZTKPQWY]\d{1,4}|^\d{1,4}'],
[u'宝成成渝线', r'[ZTKPQWY]\d{1,4}|^\d{1,4}'],
[u'汉丹襄渝线', r'[ZTKPQWY]\d{1,4}|^\d{1,4}'],
[u'川黔线', r'[ZTKPQWY]\d{1,4}|^\d{1,4}'],
[u'渝怀线', r'[ZTKPQWY]\d{1,4}|^\d{1,4}'],
[u'内六线', r'[ZTKPQWY]\d{1,4}|^\d{1,4}'],
[u'成昆线', r'[ZTKPQWY]\d{1,4}|^\d{1,4}'],
[u'南昆线', r'[GDCZ]\d{1,4}'],
[u'滨洲线', r'[ZTKPQWY]\d{1,4}|^\d{1,4}'],
[u'滨绥线', r'[ZTKPQWY]\d{1,4}|^\d{1,4}'],
[u'京津城际线', r'[C]\d{1,4}|G2\d{2}'],  
[u'沪宁城际线', r'G7[012356]\d{1,3}|(?!D7\d{1,3})[D]\d{1,4}'],
[u'成灌线', r'[C]\d{1,4}|G2\d{2}']
]

c = readcsv('js/time%s.csv'%(base_yymmdd()))
for line in lines:
    fni = u'test/%s里程.txt' % (line[0])
    fn = u'test/210120%s.svg' % (line[0])
    restr = line[1]
    m = openMilage(fni)
    buf,_ = csvToSvg(m, c, restr, station)
    print('%10d %s' % (len(buf), fn))
    writebytebom(fn, buf.encode('utf-8'))
'''

r'''
fn = "C:\\Users\\Administrator\\ticket1\\2018-09-23_XJA_CBQ.json"

j = json.loads(readbyte(fn))

buf= '';
for obj in j:
    # obj['TRNO'].encode('utf-8')
    # obj['FST'].encode('utf-8')
    # obj['EST'].encode('utf-8')
    # getSch12306(obj['FST'].encode('utf-8'), obj['EST'].encode('utf-8'), obj['TRNO'].encode('utf-8'), date)
    train_code = obj['STCODE'].encode('utf-8')
    # getSchT(obj['STCODE'].encode('utf-8'), date)
    s = json.loads(readbyte('sch/'+ train_code +'_T.json'))
    day = 0;
    last = 0;
    time_list = [];
    print(s[0]['STCODE'].encode('utf-8') + "\n")
    buf += (s[0]['STCODE'].encode('utf-8') + "\n")
    for i in range(0, len(s)):
                print (s[i]['STNO'].encode('utf-8') + ',' + s[i]['SNAME'].encode('utf-8')\
                       + ',' + re.sub('(\d\d)(\d\d)', r"\1:\2", s[i]['ATIME'].encode('utf-8'))\
                       + ',' + re.sub('(\d\d)(\d\d)', r"\1:\2", s[i]['STIME'].encode('utf-8')) + "\n");
                buf += (s[i]['STNO'].encode('utf-8') + ',' + s[i]['SNAME'].encode('utf-8')\
                       + ',' + re.sub('(\d\d)(\d\d)', r"\1:\2", s[i]['ATIME'].encode('utf-8'))\
                       + ',' + re.sub('(\d\d)(\d\d)', r"\1:\2", s[i]['STIME'].encode('utf-8')) + "\n");
    buf += ("\n");

print(buf.decode('utf-8'));

writebytebom('XJA.txt', buf)
'''

'''
[226, 9418, 47, 0, 3, 0, 0, 717, 1058, 36, 608, 0, 0]

717
w12345 85
w567 116  247 - 131 
w5671 131
w67 152 181 - 29
w671 29
w7126 8
'''

r'''
import os
import glob
from view_train_list import *

station = getStation()

maxlen = 90000
train_map = [[] for i in range(maxlen)]

now = nowdate()
base_date = '2017-11-20'

for fn0 in glob.glob(r'js\train_list_*.js'):
    _, mask, msg = add_train_list(train_map, fn0, base_date)

#train_map = json.loads(readbyte('train_map_json.txt'))

size = datediff('2019-11-12','2017-11-20') + 1
print('base_date %s size %d' % (base_date, size))
train_arr = mapToArr(train_map)
buf = trainlistStr(train_arr, base_date, size, station)
writebytebom('train_list1.txt', buf)

writebytebom('train_arr_json.txt', json.dumps(train_arr).encode('utf-8'))
writebytebom('train_map_json.txt', b = json.dumps(train_map).encode('utf-8'))

[1116, 
    0,    0,    0,    0,    0,    0,    0,
    0, 2156, 1755,  836,  705,  944, 5710, 
57718,    0,11133,  345,    0]
'''

'''
# 同城站
tc_arr = []
tc_map = {}
for s in station:
    name = s[1]
    t1 = s[2] #telecode(s[1])
    if name in tc_map:
        continue
    for retry in range(3):
            c,tc,ret = getczxx(t1, date)
            if ret > -1:
                break
            time.sleep(1 << retry)
    if len(tc) > 1:
      tc_arr.append(tc)
      for i in tc:
        tc_map[i] = name
'''

'''
# first time
d = {}
cnt = 0
for train in train_arr:
    sch = processS(train, date, station)
    flag = 0
    for row in sch[0:-1]:
        if row['station_name'] not in d:
            d[row['station_name']] = 0
        d[row['station_name']] += 1


# iterate until len(ret) stable
d = {}
cnt = 0
for train in train_arr:
    sch = processS(train, date, station)
    flag = 0
    for city in ret: #ss[0:519]: #76 519 2140 2873
        for row in sch[0:-1]:
            if row['station_name'] == city:
                flag = 1
                break
        if flag == 1:
            cnt+=1
            if city not in d:
                d[city] = 0
            d[city] += 1
            break
    if flag == 0:
       print(train['train_no'] +' '+train['from_station'] +' '+train['to_station'])

print(cnt)

c = []
for k in d:
    # print("%s %d"%(k,d[k]))
    c.append([k,d[k]])

def sort1(x,y):
    if x[1] < y[1]:
        return 1
    if x[1] > y[1]:
        return -1
    return 0

ret = []
c = sorted(c, sort1)
for k in c:
    print("%s %d"%(k[0],k[1]))
    if k[1] > 0:
        ret.append(k[0])

print(len(ret))
'''

'''
76
519
2140
2873
all

11986
15230
15682
16871
16987
'''

'''
#check_sch_time
c = getczxx('CDW', date)


cnt = 0
for t in c:
    s = getSchLocal12306(t['train_no'])
    if len(s) == 0:
        print('no file %s' % (t['train_no']))
        continue
    mt = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(os.path.getmtime('sch/'+t['train_no']+'.json')))
    if t['start_start_time'] != s[0]['start_time']:
        print('st time error %s %s %s %s' % (t['train_no'],t['start_start_time'],s[0]['start_time'], mt))
        continue
    if t['end_arrive_time'] != s[-1]['arrive_time']:
        print('ar time error %s %s %s %s' % (t['train_no'],t['end_arrive_time'],s[-1]['arrive_time'], mt))
        continue
    cnt += 1
'''

'''
from view_train_list import *
import json
import os
import re
import time
import requests

def getsearch(kw, cache=1):
    fn = ''
    if cache and os.path.exists(fn):
        search = json.loads(readbyte(fn))
        return search, len(search)
    #
    url = "http://dynamic.12306.cn/yjcx/doPickJZM?param=" + kw + "&type=1&czlx=0"
    # header = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:59.0) Gecko/20100101 Firefox/59.0"}
    header = {
        "User-Agent": "Netscape 5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36"}
    try:
        resp = requests.get(url, headers=header, timeout=20)
    except:
        print('Net Error ' + kw)
        return [], -1
    body = resp.content.decode('utf-8')
    try:
        search = json.loads(body)
    except ValueError:
        print('ValueError ' + kw)
        return [], -1
    if len(search):
        writebyte(fn, resp.content)
        print('save  %-3s %2d' % (
            kw, len(search)
        ))
        return search, len(search)
    else:
        print('empty %-3s' % (kw))
        return [], 0


def getsearch2(kw, cache=1):
    fn = 'hyfw/hyfw_%s.json' % kw
    if cache and os.path.exists(fn):
        try:
            j = json.loads(readbyte(fn))
            if 'data' in j and len(j['data']):
                return j['data'], len(j['data'])
        except:
            pass
    #
    url = "http://hyfw.95306.cn/Hywsyyt/ajax/getSzjfZdZmHwkyLjm.json?q=" + kw
    # header = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:59.0) Gecko/20100101 Firefox/59.0"}
    header = {
        "User-Agent": "Netscape 5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36"}
    try:
        resp = requests.get(url, headers=header, timeout=20)
    except:
        print('Net Error ' + kw)
        return [], -1
    body = resp.content.decode('utf-8')
    try:
        j = json.loads(body)
    except ValueError:
        print('ValueError ' + kw)
        return [], -1
    if 'data' in j and len(j['data']):
        writebyte(fn, resp.content)
        print('save  %-3s %2d' % (
            kw, len(j['data'])
        ))
        return j['data'], len(j['data'])
    else:
        print('empty %-3s' % (kw))
        return [], 0


def getAllFz(kw, cache=1):
    fn = 'hyfw/getAllFz_%s.json' % kw
    if cache and os.path.exists(fn):
        try:
            j = json.loads(readbyte(fn))
            if len(j):
                return j, len(j)
        except:
            pass
    #
    url = "http://hyfw.95306.cn/gateway/DzswD2D/Dzsw/action/AjaxAction_getAllFz?q=" + kw
    # header = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:59.0) Gecko/20100101 Firefox/59.0"}
    header = {
        "User-Agent": "Netscape 5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36"}
    try:
        resp = requests.get(url, headers=header, timeout=20)
    except:
        print('Net Error ' + kw)
        return [], -1
    body = resp.content.decode('utf-8')
    try:
        j = json.loads(body)
    except ValueError:
        print('ValueError ' + kw)
        return [], -1
    if len(j):
        writebyte(fn, resp.content)
        print('save  %-3s %2d' % (
            kw, len(j)
        ))
        return j, len(j)
    else:
        print('empty %-3s' % (kw))
        return [], 0


def dfsSearchAll(map, st):
    # dfs search_v1 in stack
    dead = []
    while(len(st)):
        kw = st.pop()
        max_depth = 3
        res = []
        for retry in range(3):
            res, ret = getsearch(kw, 1)
            if ret >= 0:
                break
            time.sleep(1 << retry)
        if ret == -1:
            dead.append(kw)
            continue
        for i in range(len(res)):
            map[hash_tele(res[i]['DBM'])] = res[i] #add_map(map, res[i])
        if len(res) + 1 < 100:
            continue
        if len(kw) >= max_depth:
            print("max_depth " + kw)
            continue
        for i in range(ord('Z'), ord('@'), -1):
            k = kw + chr(i)
            if chr(i) not in 'IOUV':
                st.append(k)
    return dead


def dfsSearchAll2(map, st):
    # dfs hyfw in stack
    dead = []
    while(len(st)):
        kw = st.pop()
        max_depth = 3
        res = []
        for retry in range(3):
            res, ret = getsearch2(kw, 1)
            if ret >= 0:
                break
            time.sleep(1 << retry)
        if ret == -1:
            dead.append(kw)
            continue
        for i in range(len(res)):
            map[hash_tele(res[i]['DBM'])] = res[i] #add_map(map, res[i])
        if len(res) + 1 < 10:
            continue
        if len(kw) >= max_depth:
            print("max_depth " + kw)
            continue
        for i in range(ord('Z'), ord('@'), -1):
            k = kw + chr(i)
            if chr(i) not in 'IOUV':
                st.append(k)
    return dead


def dfsSearchAll123(map, st):
    # dfs hyfw in stack
    dead = []
    while(len(st)):
        kw = st.pop()
        max_depth = 4
        res = []
        for retry in range(3):
            res, ret = getsearch2(kw, 1)
            if ret >= 0:
                break
            time.sleep(1 << retry)
        if ret == -1:
            dead.append(kw)
            continue
        for i in range(len(res)):
            map[hash_tele(res[i]['DBM'])] = res[i] #add_map(map, res[i])
        if len(res) < 10:
            continue
        if len(kw) >= max_depth:
            print("max_depth " + kw)
            continue
        for i in range(ord('9'), ord('0')-1, -1):
            k = kw + chr(i)
            if chr(i) not in 'IOUV':
                st.append(k)
    return dead


def dfsSearchAllFz(map, st):
    # dfs hyfw in stack
    dead = []
    while(len(st)):
        kw = st.pop()
        max_depth = 4
        res = []
        for retry in range(3):
            res, ret = getAllFz(kw, 1)
            if ret >= 0:
                break
            time.sleep(1 << retry)
        if ret == -1:
            dead.append(kw)
            continue
        for i in range(len(res)):
            map[hash_tele(res[i]['DBM'])] = res[i] #add_map(map, res[i])
        if len(res) < 50:
            continue
        if len(kw) >= max_depth:
            print("max_depth " + kw)
            continue
        for i in range(ord('9'), ord('0')-1, -1):
            k = kw + chr(i)
            if chr(i) not in 'IOUV':
                st.append(k)
    return dead


kw = ''
st = []
for i in range(ord('Z'), ord('@'), -1):
            k = kw + chr(i)
            if chr(i) not in 'IOUV':
                st.append(k)

map = [None for i in range(26*26*26)]

dfsSearchAll(map, st)

dfsSearchAll2(map, st)

map = [None for i in range(26*26*26)]
kw = ''
st = []
for i in range(ord('9'), ord('0'), -1):
            k = kw + chr(i)
            if chr(i) not in 'IOUV':
                st.append(k)

dfsSearchAllFz(map, st)
#dfsSearchAll123(map, st)

writebytebom('dbm3_map_json.txt', b=json.dumps(map).encode('utf-8'))

ret = []
for v in map:
    if v == None:
        continue
    ret.append([
        v["LJDM"].encode('utf-8'),
        v["DBM"].encode('utf-8'),
        v["PYM"].encode('utf-8'),
        v["TMIS"].encode('utf-8'),
        v["SSJC"].encode('utf-8'),
        v["ZMHZ"].encode('utf-8')
    ])


ret = []
for v in map:
    if v == None:
        continue
    ret.append([
        v["LJM"].encode('utf-8'),
        v["LJDM"][0].encode('utf-8'),
        #v["LJQC"].encode('utf-8'),
        v["DBM"].encode('utf-8'),
        v["PYM"].encode('utf-8'),
        v["TMISM"].encode('utf-8'),
        # x v["SSJC"].encode('utf-8'),
        v["HZZM"].encode('utf-8')
    ])


#{"HZZM":"北京西","SBDM":"11","LJDM":"P00","TMISM":"21152","LJQC":"北京局","DBM":"BXP","LJJC":"京","PYM":"BJX","SSSX":"京"}
ret = []
for v in map:
    if v == None:
        continue
    ret.append([
        # x v["LJM"].encode('utf-8'),
        v["LJDM"][0].encode('utf-8'),
        #v["LJQC"].encode('utf-8'),
        #v["LJJC"].encode('utf-8'),
        v["DBM"].encode('utf-8'),
        v["PYM"].encode('utf-8'),
        v["TMISM"].encode('utf-8'),
        # x v["SSJC"].encode('utf-8'),
        # v["SBDM"].encode('utf-8'),
        v["SSSX"].encode('utf-8'),
        v["HZZM"].encode('utf-8')
    ])


writecsv("DBM3.csv", ret)
'''

'''
#重新获取比中位数的80%少的
from view_train_list import *
import math

now = nowdate()
base_date = basedate('')
station = getStation()

samecity_arr = []
samecity_map = {}

citys = re.split(r'[\r\n,*]+', readbyte('citys.txt').decode('utf-8'))

for name in citys:
    t1 = telecode(name, station)
    if len(t1) == 0:
        continue
    if name in samecity_map:
        continue
    rets = []
    for i in range(-7, 14): #32
        date = date_add(now, i)
        c, samecity, ret = getczxx(t1, date, cache = 2)
        rets.append(ret)
        if len(samecity) > 1:
            samecity_arr.append(samecity)
            for ii in samecity:
                samecity_map[ii] = name
    n = len(rets)
    ex = sum(rets) #/n
    ex2 = sum([x*x for x in rets]) #/n
    sd = round(math.sqrt((ex2*n - ex * ex)) /n)
    level = round(ex/n) - 2*sd # sorted(rets)[len(rets)//2]*8//10
    #print(t1, level)
    for i in range(len(rets)): #-8...32
        if rets[i] < level:
            print(t1, date_add(now, i-7), rets[i], level)
            c, samecity, ret = getczxx(t1, date_add(now, i-7), cache = 0)


samecity_arr = []
samecity_map = {}
for name in citys:
    t1 = telecode(name, station)
    if len(t1) == 0:
        continue
    if name in samecity_map:
        continue
    for i in range(-7, -1): #32
        date = date_add(now, i)
        fn = getczxxFileName(t1, date)
        if not os.path.exists(fn):
            continue
        mt = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(os.path.getmtime(fn)))
        if '2020-06-2' in mt:
            print(mt, date, t1)
            c, samecity, ret = getczxx(t1, date_add(now, i), cache = 0)

for t1 in ['BJP']:
    for i in range(1,29):
        c, samecity, ret = getczxx(t1, date_add(now, i), cache = 0)

for t1 in ['BJP','JNK','NJH','SHH']:
    for i in range(10,14):
        c, samecity, ret = getczxx(t1, date_add(now, i), cache = 0)
'''
