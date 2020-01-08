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
import csv
import time
# import math
# import random

import requests


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
    return w % 7


def getmin(s):
    try:
        a, b = s.split(':')[0:2]
        return int(a)*60+int(b)
    except:
        return -1


def print_stat(stat):
    buffer = ''
    for i in range(len(stat)):
        buffer += (("    " + str(stat[i]))[-4:]
                   + ('' if (i+1) % 20 else '\n')
                   + ('' if (i+1) % 60 else '\n'))
    return buffer


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
def getStation(fn='js/station_name.js'):
    # f = open(fn, 'r',encoding = 'utf8'); #py3
    with open(fn, 'rb') as f:  # py2
        s = f.read().decode('utf-8')
    a = re.findall(r'\'\@([^\']+)\'', s, re.I | re.M)[0]
    s = a.split('@')
    for i in range(len(s)):
        s[i] = s[i].split('|')
    print('read %d stations in %s' % (len(s), fn))
    s.append([u"dxc", u"大兴机场", u"IWP", u"daxingjichang", u"dxjc", u"-1"])
    s.append([u"tsn", u"唐山南", u"TNP", u"tangshannan", u"tsn", u"-1"])
    s.append([u"gye", u"古冶", u"GYP", u"guye", u"gy", u"-1"])
    s.append([u"", u"香港红磡", u"JQO", u"xiangganghongkan", u"xghk", u"-1"])
    s.append([u"jlo", u"九龙", u"JQO", u"jiulong", u"jl", u"-1"])
    #s.append([u"xgl", u"香港西九龙", u"XJA", u"hkwestkowloon", u"xgxjl", u"-1"])
    s.append([u'jsw', u'金山卫', u'BGH', u'jinshanwei', u'jsw', u'-1'])
    s.append([u'mji', u'梅江', u'MKQ', u'meijiang', u'mj', u'-1'])
    s.append([u'ylo', u'元龙', u'YLY', u'yuanlong', u'yl', u'-1'])
    s.append([u'bdl', u'八达岭', u'ILP', u'badaling', u'bdl', u'-1'])
    s.append([u'nsb', u'南山北', u'NBQ', u'nanshanbei', u'nsb', u'-1'])
    s.append([u'', u'车墩', u'MIH', u'chedun', u'cd', u'-1'])
    s.append([u'', u'羊木', u'AMJ', u'yangmu', u'ym', u'-1'])
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


# train_map
def hash_no(s):
    items = [('Z', 10000), ('T', 20000), ('K', 30000),
             ('Y', 00000), ('L', 00000), ('A', 00000),
             ('G', 40000), ('D', 50000), ('C', 60000),
             ('S', 70000),
             ('P', 10000), ('Q', 20000), ('W', 30000),
             ('V', 1000), ('B', 2000), ('U', 4000), ('X', 5000)]
    d = dict(items)
    train_class = d[s[0]] if s[0] in d else 0
    n = int(re.sub(r'\D+', '', s))
    return train_class + n


def unhash_no(n):
    items = [('Z', 10000), ('T', 20000), ('K', 30000),
             ('Y', 00000), ('L', 00000), ('A', 00000),
             ('G', 40000), ('D', 50000), ('C', 60000),
             ('S', 70000),
             ('P', 10000), ('Q', 20000), ('W', 30000),
             ('V', 1000), ('B', 2000), ('U', 4000), ('X', 5000)]
    head = ["", "Z", "T", "K", "G", "D", "C", "S"]
    if n > 80000:
        return ""
    train_class = head[(n-1) // 10000]
    if n <= 1000:
        train_class = "Y"
    for i in range(len(items)):
        if train_class == items[i][0]:
            return train_class + str(n-items[i][1])
    return str(n)


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
    key = hash_no(a['station_train_code']) - 1
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
        for train in train_map[key]:
            train_arr.append(train)
    return train_arr


def trainlistStr(train_arr, base_date, size, station=None):
    stat = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    buffer = ''
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
        buffer += '%s,%s,%s,%s,%d,%s,%d,%s\n' % (
            train['train_no'].encode('utf-8'),
            t1,
            t2,
            train['station_train_code'].encode('utf-8'),
            train['total_num'],
            '0' if train['service_type'] == '0' else '',
            train['src'],
            val
        )
    #
    print(stat)
    return buffer


# train_list.js
def openTrainList(fn='js/train_list.js'):
    # f = open(fn, 'r',encoding= 'utf8') #py3
    with open(fn, 'r') as f:  # py2
        _ = f.read(16)
        data = f.read()
    return json.loads(data)


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
    with open(fn0, 'r') as f:
        # with open(fn0, 'r', encoding='utf-8') as f: #py3
        _ = f.read(16)
        data = f.read()
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
    name = 'search/' + yyyymmdd + '_' + kw + '.json'
    try:
        fn = os.path.join(os.path.dirname(os.path.abspath(__file__)), name)
    except:
        fn = name
    if cache and os.path.exists(fn):
        with open(fn, 'r') as f:
            data = f.read()
        try:
            search = json.loads(data)
            if search['status'] == True and len(search['data']):
                print('read  %-3s %3d %5s-%5s' % (
                    kw, len(search['data']),
                    search['data'][0]['station_train_code'],
                    search['data'][-1]['station_train_code'])
                )
                return search['data'], len(search['data'])
        except ValueError:
            print('ValueError ' + kw)
    #
    url = "https://search.12306.cn/search/v1/train/search?keyword=" + \
        kw + "&date=" + yyyymmdd
    # header = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:59.0) Gecko/20100101 Firefox/59.0"}
    header = {
        "User-Agent": "Netscape 5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36"}
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
        return [], -1
    if not isinstance(search, dict):
        print('search is %s %s' % (type(search), kw))
        return [], -1
    if not 'data' in search:
        print('key data not exist ' + kw)
        return [], -1
    if search['status'] == True and len(search['data']):
        with open(fn, 'wb') as f:
            f.write(resp.content)
        print('save  %-3s %3d %5s-%5s' % (
            kw, len(search['data']),
            search['data'][0]['station_train_code'],
            search['data'][-1]['station_train_code'])
        )
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
    dead = []
    while(len(st)):
        kw = st.pop()
        jump = 0
        if kw == "Y" or kw == "":
            jump = 1
        max_depth = 3
        res = []
        if not jump:
            for retry in range(2):
                res, ret = getsearch12306(kw, date, cache)
                if ret >= 0:
                    break
                time.sleep(2 << retry)
        if ret == -1:
            dead.append(kw)
            continue
        max_index = -1
        for i in range(len(res)):
            res[i]['date'] = 1 << datediff(date, base_date)
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
            if k in max_str or k > max_str or len(re.sub(r'\D+', '', max_str)) < 4:
                st.append(k)
    return dead


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
def processA(a, date, station):
    return processS(atos(a), date, station)


# timetable train_list.js
def processS(a, date, station):
    name = 'sch/' + a['train_no'].encode('utf-8')+'.json'
    try:
        fn = os.path.join(os.path.dirname(os.path.abspath(__file__)), name)
    except:
        fn = name
    if os.path.exists(fn):
        with open(fn, 'r') as f:
            data = f.read()
        try:
            sch = json.loads(data)
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
        with open(fn, 'r') as f:
            data = f.read()
        try:
            sch = json.loads(data)
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
        "User-Agent": "Netscape 5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36"}
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
    try:
        fn = os.path.join(os.path.dirname(os.path.abspath(__file__)), name)
    except:
        fn = name
    if sch['status'] == True and sch['httpstatus'] == 200 and len(sch['data']['data']):
        with open(fn, 'wb') as f:
            f.write(resp.content)
        print('%s %s %s %2d' % (train_no, t1, t2, len(sch['data']['data'])))
        return sch['data']['data']
    else:
        print('data error %s %s %s %s' % (train_no, t1, t2, date))
        return []


def schToCsv(s):
    # buffer = ''
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
            '''buffer += (
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
            '''buffer += (
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
    # return buffer
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
        if (train['station_train_code'] in train['train_no']) == False:
            continue
        s = schDateToCsv(sch, train['src'],
                         train['date'], base_date, size, station)
        for row in s:
            if len(row) >= 7:
                rows.append(row)
    return rows


def checkSchdatemasktocsv(train_arr, base_date, size, mask, station=None):
    '''
    change train_arr[i]['service_type'] ['total_num']
    '''
    rows = []
    for train in train_arr:
        if train['date'] & mask == 0:
            continue
        for retry in range(3):
            diff = get_last_one(train['date'], size)
            if diff > -1:
                date = date_add(base_date, diff)
            else:
                date = base_date
            sch = processS(train, date, station)
            if len(sch):
                break
            time.sleep(1 << retry)
        train['total_num'] = len(sch)
        if len(sch):
            train['service_type'] = sch[0]['service_type']
        else:
            train['service_type'] = ""
        if (train['station_train_code'] in train['train_no']) == False:
            continue
        s = schDateToCsv(sch, train['src'],
                         train['date'], base_date, size, None)
        for row in s:
            if len(row) >= 7:
                rows.append(row)
    return rows


def schDateToCsv(s, src, date_bin, base_date, size, station=None):
    # buffer = ''
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
            t1 = s[i]['station_name'].replace(u'\ue244', u'\u78cf').replace(
                u'\ue24d', u'\u6911').encode('utf-8')
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
                src,
                val
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
                src,
                val
            ])
    # return buffer
    return ret


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
        fn = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          f1)
    except:
        fn = f1
    with open(fn, "wb") as f:  # use wb on win, or get more \r \r\n
        if f.tell() == 0:
            f.write('\xef\xbb\xbf')
        writer = csv.writer(f)
        writer.writerows(ret)
    return len(ret)


def writebyte(f1, b):
    '''
    write bytes with UTF-8 BOM
    '''
    fn = os.path.join(os.path.dirname(
        os.path.abspath(__file__)), f1)
    with open(fn, 'wb') as f:
        if f.tell() == 0:
            f.write('\xef\xbb\xbf')
        f.write(b)


# line
def openMilage(fn):
    with open(fn, 'rb') as f:  # py2
        if f.read(3) != b'\xef\xbb\xbf':
            f.seek(0, 0)
        data = f.read().decode('utf-8')
    m = data.split('\n')
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
    buffer = ''
    day = 0
    lastx = 0
    lasty = 0
    polyline_class = polylineClass(s[0]['station_train_code'].encode('utf-8'))
    buffer += '<polyline name="%s" class="%s" points="' % (
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
                buffer += '%d,%d "/>\n<polyline name="%s+%d" class="%s" points="%d,%d ' % (
                    1440, split_y,
                    s[0]['station_train_code'].encode('utf-8'), day,
                    polyline_class,
                    0, split_y
                )
            lastx = x
            lasty = y
            buffer += '%s,%s ' % (x, y)
        #
        x = getmin(s[i]['start_time'])
        if y > -1 and i < len(s)-1:
            if x < lastx:
                day += 1
                split_y = int(y) + int(x)*(int(lasty)-int(y)) / \
                    ((1440+int(x)-int(lastx)))
                buffer += '%d,%d "/>\n<polyline name="%s+%d" class="%s" points="%d,%d ' % (
                    1440, split_y,
                    s[0]['station_train_code'].encode('utf-8'), day,
                    polyline_class,
                    0, split_y,
                )
            buffer += '%s,%s ' % (x, y)
            lastx = x
            lasty = y
    buffer += '"/>\n'
    return buffer


def csvToPolyline(c, m, station=None):
    # ['K868,\xe6\xb3\x8a\xe5\xa4\xb4,05,1,00:00,0']
    if (len(c)) <= 0:
        return ''
    buffer = ''
    day = 0
    lastx = 0
    lasty = 0
    lastdate = ''
    polyline_class = polylineClass(c[0][0])
    buffer += '<polyline name="%s_%s" class="%s" points="' % (
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
                buffer += '%d,%d "/>\n<polyline name="%s_%s+%d" class="%s" points="%d,%d ' % (
                    1440, split_y,
                    date.replace('&', ''),
                    c[0][0], day, polyline_class,
                    0, split_y
                )
            if lastx == -1 or lastdate != date and i > 0:
                day = 0
                buffer += '"/>\n<polyline name="%s_%s+%d" class="%s" points="' % (
                    date.replace('&', ''),
                    c[0][0], day, polyline_class
                )
            buffer += '%s,%s ' % (x, y)
        lastx = x
        lasty = y
        lastdate = date
    buffer += '"/>\n'
    return buffer


def csvToSvg(m, c, rule='', station=None):
    r = re.compile('^' + rule + '$', re.IGNORECASE | re.MULTILINE)
    maxlen = 80000
    arr = [[] for i in range(maxlen)]

    for i in range(len(c)):
        if len(c[i]) < 2:
            continue
        if getkm(c[i][1], m, station) > -1:
            # print(hash_no(c[i][0]))
            arr[hash_no(c[i][0])].append(c[i])
    #
    buffer = ''
    buffer += '<?xml version="1.0" standalone="no"?>\n'
    buffer += '<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" \n'
    buffer += '"http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">\n'
    buffer += '<svg width="%s" height="%s" version="1.1" \n' % (
        1440,
        (int(m[-1][1])+50)//50*50
    )
    buffer += 'xmlns="http://www.w3.org/2000/svg">\n'
    buffer += '''
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
        buffer += ('<line class="hour" x1="%d" y1="0" x2="%d" y2="3000" />\n' %
                   (i*60, i*60))
        buffer += ('<line class="halfhour" x1="%d" y1="0" x2="%d" y2="3000" />\n' %
                   (i*60+30, i*60+30))

    for i in range(len(m)):
        buffer += ('<text x="0" y="%d">%s %s</text>\n' %
                   (int(m[i][1]) if int(m[i][1]) > 16 else (int(m[i][1]) + 16), m[i][0], m[i][1]))
        buffer += ('<line class="station" x1="0" y1="%s" x2="1440" y2="%s" />\n' %
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
            arr[i] = sorted(arr[i], cmpby0_7_i2_i5_i3_m4)
            buffer += csvToPolyline(arr[i], m, station)
    #
    buffer += ('</svg>')
    return buffer, num


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


def train_list_stat_block(arr, step, maxlen):
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


def getczxx(t1, date, cache=1):
    # TODO local online
    name = 'ticket/' + date + '_' + t1 + '.json'
    try:
        fn = os.path.join(os.path.dirname(os.path.abspath(__file__)), name)
    except:
        fn = name
    exist = os.path.exists(fn)
    if exist and cache == 1 and datediff(time.strftime(
            '%Y-%m-%d',
            time.localtime(os.path.getmtime(fn))),
            date) < -29:
        cache == 0
    if exist and cache >= 1:
        with open(fn, 'r') as f:
            data = f.read()
        try:
            j = json.loads(data)
            if j['status'] == True and j['httpstatus'] == 200 and len(j['data']['data']):
                # print('%s %s %4d local' % (t1, date, len(j['data']['data'])))
                return j['data']['data'], j['data']['sameStations'], len(j['data']['data'])
        except ValueError:
            print('ValueError %s %s' % (t1, date))
    if cache == 2:
        print('No File %s %s' % (t1, date))
        return [], [], 0
    #
    url = "https://kyfw.12306.cn/otn/czxx/query?train_start_date=" + date + \
        "&train_station_name=" + "" + \
        "&train_station_code=" + t1 + "&randCode="
    header = {
        "User-Agent": "Netscape 5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36"}
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
    if j['status'] == True and j['httpstatus'] == 200 and len(j['data']['data']):
        with open('ticket/' + date + '_' + t1 + '.json', 'wb') as f:
            f.write(resp.content)
        print('%s %s %4d' % (t1, date, len(j['data']['data'])))
        return j['data']['data'], j['data']['sameStations'], len(j['data']['data'])
    else:
        print('data error %s %s' % (t1, date))
        return [], [], 0


LeftTicketUrl = "leftTicket/query"


def getLeftTicket(t1, t2, date):
    url = "https://kyfw.12306.cn/otn/" + LeftTicketUrl + "?leftTicketDTO.train_date=" + date + \
        "&leftTicketDTO.from_station=" + t1 + \
        "&leftTicketDTO.to_station=" + t2 + "&purpose_codes=ADULT"
    header = {
        "User-Agent": "Netscape 5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36"}
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
    if ticket['status'] == True and ticket['httpstatus'] == 200 and len(ticket['data']['result']):
        with open('ticket/' + date + '_' + t1 + '_' + t2 + '.json', 'wb') as f:
            f.write(resp.content)
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


def gtzwdjsp():
    url = 'http://www.gtbyxx.com/wxg/ky/zhengwan.jsp'
    header = {
        "User-Agent": "Netscape 5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36"}
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
    name = 'delay/gt_' + date + '_' + s + '.json'
    try:
        fn = os.path.join(os.path.dirname(os.path.abspath(__file__)), name)
    except:
        fn = name
    url = 'http://www.gtbyxx.com/wxg/inter/ky/getTrainZwd'
    j = {"trainNo": s}
    header = {
        "User-Agent": "Netscape 5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36"}
    resp = requests.post(url, data=json.dumps(j), headers=header, timeout=20)
    body = resp.content.decode('utf-8')
    #
    j = json.loads(body)
    with open(fn, 'wb') as f:
        f.write(resp.content)
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
    for step in [1, 2, 7, 3, 4, 5, 6]:
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
    c <<= base_week
    c |= c >> 7
    c &= 0x7f
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


def slice_to_str(ret, base_date):
    ans = ''
    for i in range(len(ret)):
        if i > 0:
            ans += "|"
        if ret[i][0] == ret[i][1]:
            ans += re.sub(r'(\d\d)(\d\d)-(\d+)-(\d+)',
                          r"\3\4", date_add(base_date, ret[i][0]))
            continue
        else:
            ans += '%s-%s' % (
                re.sub(r'(\d\d)(\d\d)-(\d+)-(\d+)',
                       r"\3\4", date_add(base_date, ret[i][0])),
                re.sub(r'(\d\d)(\d\d)-(\d+)-(\d+)',
                       r"\3\4", date_add(base_date, ret[i][1]))
            )
    return ans


def compress_bin_vector(date_bin, base_date, size):
    date_bin &= all1(size)
    if date_bin & all1(size) == all1(size):
        return "", 1
    #
    step, _ = try_step(date_bin)
    #
    size_floor = size//step*step
    if ((date_bin & all1(size_floor)) % all01(size_floor, step, 1)) == 0:
        # 取循环节
        c = (date_bin & all1(size_floor)) // all01(size_floor, step, 1)
        if (all1(size) & all01(size, step, c)) == date_bin:
            if step == 7:
                return 'w' + cycle7(c, weekday(base_date)), step
            return ('{:0>'+str(step)+'b}').format(c), step
        else:
            return ('{:0>'+str(step)+'b} *').format(c) + " " + ('{:0>'+str(size)+'b}').format(date_bin), step
    #
    for offset in range(step):
        one_slice = get_one_slice(date_bin, size, offset, step)
        if len(one_slice) == 0:
            continue
        if step == 1:
            return slice_to_str(one_slice, base_date), step + 7
        if offset == 0 and step == 2:
            return "双&" + slice_to_str(one_slice, base_date), step + 7
        if offset == 1 and step == 2:
            return "单&" + slice_to_str(one_slice, base_date), step + 7
    #
    one_slice = get_one_slice(date_bin, size)
    zero_slice = get_zero_slice(date_bin, size)
    bin_weight = bin_cnt(date_bin)
    if bin_weight < size / 7:
        return slice_to_str(one_slice, base_date), 17
    if len(one_slice) <= len(zero_slice):
        if len(one_slice) <= 4:
            return slice_to_str(one_slice, base_date), 15
    else:
        if len(zero_slice) <= 1 and len(zero_slice) > 0:
            return "停" + slice_to_str(zero_slice, base_date), 16
    if bin_weight > size - size / 7 and len(zero_slice) > 0:
        return "停" + slice_to_str(zero_slice, base_date), 18
    #
    return ('{:0>'+str(size)+'b}').format(date_bin) + ' consecutive' + str(bin_count1n(date_bin)), 0


if __name__ == '__main__':
    try:
        fn0 = sys.argv[1]
    except:
        fn0 = os.path.join(os.path.dirname(
            os.path.abspath(__file__)), 'js/train_list.js')
    try:
        fn1 = sys.argv[2]
    except:
        fn1 = os.path.join(os.path.dirname(
            os.path.abspath(__file__)), 'js/station_name.js')
    print('input train_list file:   ' + fn0)

    '''
    try:
        # if True:
        t = openTrainList(fn0)
        arr = train_list_train_no_array(t, 80000)
        stat, train_num = train_list_stat_block(arr, 100, 80000)
        s, block = print_block(stat)
        print(str(train_num) + " trains")
        print(str(block) + " blocks")
        print(s)
        print(train_list_class_str(t))
        station = getStation(fn1)
        checkAllSch12306(t, station)
        saveallcsv(t, station)
        if platform.system() == "Windows":
            os.system('pause')
    except Exception, e:
        print(str(Exception))
        if platform.system() == "Windows":
            os.system('pause')
    '''

    station = getStation(fn1)

    # buffer = compress_train_list(fn0, station) #TODO

    maxlen = 80000
    train_map = [[] for i in range(maxlen)]
    #
    import datetime
    now = datetime.datetime.now().strftime('%Y-%m-%d')
    base_date = '2019-12-30'
    #end_date = ''
    #
    #base_date, mask, msg = add_train_list(train_map, fn0, '2019-12-30')
    size = 0  # bin_cnt(mask)
    #
    #
    # 97-98主要换乘站 北京 天津 沈阳 长春 通辽 哈尔滨 齐齐哈尔 大连 泰安 徐州 南京 上海 石家庄 郑州 武昌 长沙 株洲 广州 襄阳 柳州 贵阳 西安 兰州 成都
    # 京哈线及东北地区 京沪线及华东地区 京九线 京广线及中南地区 陇海线及西南、西北地区 宝成线及西南地区 侯月、京原、京包、南北同蒲

    citys = re.split(r'[\n,*]+', u'''北京,北京西,北京南,北京北,北京东,清河,昌平北
上海,上海南,上海虹桥,上海西
广州,广州南,广州东,广州北,新塘南
石家庄,石家庄北,石家庄东,高邑,藁城南,藁城
郑州,郑州东,郑州西,南阳寨
武昌,汉口,武汉
长沙,长沙南,长沙西
深圳,深圳北,福田,深圳东,深圳西,深圳机场,深圳机场北
香港西九龙
香港红磡
海口,海口东,海  口东
南宁,南宁东,南宁西
太原,太原南,太原东,汾河
西安,西安北,西安南
成都,成都东,犀浦,成都西,成都南
重庆,重庆北,重庆西,重庆南,沙坪坝
贵阳,贵阳北,贵阳东
昆明,昆明南,王家营西
天津,天津西,天津北,塘沽,天津南,滨海西,滨海,杨柳青,军粮城北,蓟州
沈阳,沈阳北,沈阳南,裕国,沈阳西
大连,大连北
长春,长春西
哈尔滨,哈尔滨东,哈尔滨北,哈尔滨西,香坊
济南,济南西,济南东,大明湖,章丘,章丘北
青岛,青岛北,青岛西
南京,南京南,仙林
合肥,合肥南,合肥北城
杭州,杭州东
南昌,南昌西,南 昌
福州,福州南,福州 南
厦门,厦门北,厦 门
呼和浩特,呼和浩特东
银川
兰州,兰州西,兰州新区,西固,永登,皋兰,榆中,河口南,兰州东,夏官营
西宁
乌鲁木齐,乌鲁木齐南
拉萨

徐州,徐州东
蚌埠,蚌埠南
株洲,株洲南,株洲西
衡阳,衡阳东
襄阳,襄阳东
怀化,怀化南
柳州
鹰潭,鹰潭北
宝鸡,宝鸡南
内江,内江北
六盘水

集宁南,乌兰察布
二连

满洲里
海拉尔
阿尔山北
阿尔山
塔尔气
伊图里河
根河
塔河
加格达奇
富拉尔基
三间房
齐齐哈尔,齐齐哈尔南
大庆,大庆西,大庆东
黑河
北安
海伦
绥化
伊春
乌伊岭
鹤岗
同江
前进镇
双鸭山
佳木斯,佳木斯西
桦南
鸡西
牡丹江
绥芬河
扶余,扶余北
德惠,德惠西
吉林
辽源
通化
集安
白山市
延吉,延吉西
图们,图们北
松原
白城
乌兰浩特
公主岭,公主岭南
四平,四平东
铁岭,铁岭西
抚顺,抚顺北
丹东,五龙背,五龙背东
庄河北
安平
本溪
营口,营口东
辽阳
鞍山,鞍山西
锦州,锦州南
阜新,阜新南
叶柏寿
赤峰南,平庄,赤峰东
通辽
库伦
霍林郭勒

山海关
秦皇岛
北戴河
唐山,唐山北,唐山南,古冶,曹妃甸东,唐海南,南堡北
承德,上板城,承德南,承德县北,平泉北,平泉,承德东,上板城南
张家口,张家口南,太子城
保定,保定东
邯郸,邯郸东
衡水,衡水北
廊坊,廊坊北
沧州,沧州西
德州,德州东
通州西
兴隆县
大涧
燕郊

古北口
大兴机场

蓟州北
宝坻

柴沟堡
大同,大同南
朔州
忻州,忻州西
岢岚
宁武
轩岗
原平,原平西
榆次,晋中
阳泉,阳泉北
介休,介休东
洪洞,洪洞西
临汾,临汾西
侯马,侯马西
运城,运城北
沁县
长治,长治北
韩城
吕梁

包头,包头东,昆都仑召,包头西,包头北
乌海,乌海西,乌海北
东胜西,鄂尔多斯,东胜东

聊城
菏泽
德州,德州东
泰山,泰安
枣庄,枣庄西,枣庄东
东营,东营南
淄博,淄博北
潍坊,潍坊北
烟台,烟台南,烟台西
威海,威海北,文登东,文登
荣成
临沂,临沂东
日照,日照西

连云港,连云港东
宿迁
淮安,淮安东
盐城,盐城北
扬州,江都
泰州,姜堰
南通
启东

苏州,苏州北,苏州园区,苏州新区
无锡,无锡东,无锡新区,惠山
常州,常州北,戚墅堰
昆山,昆山南,阳澄湖

金山卫
车墩

诸暨
宁波,庄桥
温州,温州南

阜阳
淮北,淮北北
马鞍山,马鞍山东
芜湖,弋江
安庆
黄山,黄山北

上饶
萍乡,萍乡北
九江
赣州,赣州西,赣县北
瑞金
井冈山,龙市
抚州

福鼎,太姥山
武夷山,武夷山东,武夷山北
南平北,延平西,南平南
三明,三明北
龙岩
漳州

焦作
新郑机场
宋城路
安阳,安阳东
新乡,新乡东
许昌,许昌东
信阳,信阳东
潢川
商丘,商丘南
洛阳,洛阳龙门,洛阳东,关林
宝丰,平顶山,平顶山西
南阳

孝感,孝感东,孝感北
咸宁,咸宁北,咸宁南,咸宁东
黄冈,黄冈东,黄冈西
黄石,黄石北,大冶北,花湖
麻城,麻城北
荆门
荆州
宜昌东
恩施
利川
十堰

湘潭
娄底,娄底南
常德
邵阳,邵阳北
岳阳,岳阳东
石门县北
张家界,张家界西
永州

佛山,佛山西,狮山,狮山北
肇庆,肇庆东,鼎湖东,大旺,端州,鼎湖山,四会
茂名,茂名西,电白,马踏
信宜
新会
珠海,明珠,唐家湾,珠海北,前山
道滘
东莞,常平,东莞东,东莞西,常平东,常平南,樟木头东,银瓶,虎门北
惠州,惠州南,小金口,云山,仲恺,惠环,沥林北,西湖东,龙丰,惠东
梅州,梅州西
潮州
潮汕,饶平
汕头
陆丰,汕尾,鲘门

三亚,三  亚

金城江
桂林,桂林北,桂林西
凭祥
防城港北
北海
玉林
梧州,梧州南
贺州

广元
江油,江油北
绵阳
德阳
万州,万州北
南充,南充北
达州,石梯
广安,广安南
资中,资中北
隆昌,隆昌北
永川,永川东
宜宾,宜宾南,宜宾西
青城山
离堆公园
都江堰
彭州
邛崃
雅安
眉山,眉山东
峨眉,峨眉山,燕岗
普雄
西昌
攀枝花,攀枝花南

毕节
遵义,遵义西
铜仁
铜仁南,玉屏
凯里,凯里南
安顺,安顺西
麻尾

元谋西
广通北
昭通,昭通南,昭通北
宣威
曲靖,曲靖北
弥勒
富宁
玉溪
大理
红果

榆林
延安
阎良
韩城
华山,华山北
渭南,渭南北
安康
汉中
阳平关,宁强南,燕子砭

石嘴山,大武口
汝箕沟
中卫

白银西,白银市
干塘
中川机场
平凉,平凉南
张家川
天水,天水南,新阳镇,渭南镇
陇西
陇南
武威,武威南
金昌
张掖,张掖西
嘉峪关,嘉峪关南
绿化
镜铁山
敦煌
柳园,柳园南

门源
德令哈
格尔木
那曲
日喀则

哈密
吐鲁番,吐鲁番北
达坂城
库尔勒
喀什
和田
石河子
奎屯
克拉玛依
塔城
阿勒泰
四棵树
阿拉山口
伊宁
霍尔果斯''')
    for i in range(-datediff(now, base_date), 32):
        date = date_add(now, i)
        freq = re.split(
            r'[\s\n,*]+', u'''北京 天津 沈阳 长春 哈尔滨 徐州 南京 上海 杭州 石家庄 郑州 武昌 长沙 株洲 广州 贵阳 西安 兰州 成都 昆明''')
        samecity_arr = []
        samecity_map = {}
        for name in citys:
            cache = 1
            if i == 0:
                cache = 0
            if i > 29:
                cache = 0
            if i < 0:  # min -8
                cache = 2
            if (i >= -1) and (name in freq):
                cache = 0
            t1 = telecode(name, station)
            if len(t1) == 0:
                continue
            if name in samecity_map:
                continue
            for retry in range(5):
                c, samecity, ret = getczxx(t1, date, cache)
                if ret > -1:
                    break
                time.sleep(1 << retry)
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
    #
    '''for i in range(31, -1, -1):
        # st = ["90", "50", "10", "C", "D", "G", "", "K", "Y", "P", "T", "Z"]
        st = ["D9", "G9", "3", "T", "Z", "K5", "K4", "D4", "G4"]
        date = date_add(now, i)
        #diff = datediff(date, base_date)
        #if diff >= size:
        #    size = diff + 1
        cache = 1
        if i == 0:
            cache = 0
        for retry in range(3):
            st = searchAll12306(train_map, base_date, date, st, cache)
            if len(st) == 0:
                break
            time.sleep(2 << retry)
        print(date, st)'''
    #
    print('base_date %s size %d' % (base_date, size))
    #
    train_arr = mapToArr(train_map)
    #
    ret = checkSchdatebintocsv(train_arr, base_date, size, station)
    num = writecsv("delay/time.csv", ret)
    print(num)
    #
    buffer = trainlistStr(train_arr, base_date, size, station)
    writebyte(fn0 + '.txt', buffer)
    #
    #
    for i in range(size):
        mask = 1 << i
        date = date_add(base_date, i)
        ret = checkSchdatemasktocsv(train_arr, base_date, size, mask, station)
        num = writecsv("delay/sort"+date+".csv", ret)
        print('%s %6d' % (date, num))

r'''
from view_train_list import *

station = getStation()
# saveallcsv(t,station)

lines = [
[u'京沪高速线', r'(?!G7[012356]\d{1,3})[G]\d{1,4}|(?!D7\d{1,3})[D]\d{1,4}'],
[u'京广高速线', r'[GDC]\d{1,4}'],
[u'沪昆高速线', r'[GDC]\d{1,4}'],
[u'京包高速线', r'[GDC]\d{1,4}'],
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

c = readcsv('delay/time.csv')
for line in lines:
    fni = u'test/%s里程.txt' % (line[0])
    fn = u'test/191230%s.svg' % (line[0])
    restr = line[1]
    m = openMilage(fni)
    buffer,_ = csvToSvg(m, c, restr, station)
    print('%10d %s' % (len(buffer), fn))
    with open(fn, "wb") as f:  # use wb on win, or get more \r \r\n
        if f.tell() == 0:
            f.write('\xef\xbb\xbf')
        f.write(buffer.encode('utf-8'))

'''

r'''
fn = "C:\\Users\\Administrator\\ticket1\\2018-09-23_XJA_CBQ.json"

with open(fn,'r') as f: #py2
    data=f.read();

j = json.loads(data)

buffer= '';
for obj in j:
    # obj['TRNO'].encode('utf-8')
    # obj['FST'].encode('utf-8')
    # obj['EST'].encode('utf-8')
    # getSch12306(obj['FST'].encode('utf-8'), obj['EST'].encode('utf-8'), obj['TRNO'].encode('utf-8'), date)
    train_code = obj['STCODE'].encode('utf-8')
    # getSchT(obj['STCODE'].encode('utf-8'), date)
    with open('sch/'+ train_code +'_T.json','r') as f:
        f.read(3);
        data = f.read();
    s = json.loads(data)
    day = 0;
    last = 0;
    time_list = [];
    print(s[0]['STCODE'].encode('utf-8') + "\n")
    buffer += (s[0]['STCODE'].encode('utf-8') + "\n")
    for i in range(0, len(s)):
                print (s[i]['STNO'].encode('utf-8') + ',' + s[i]['SNAME'].encode('utf-8')\
                       + ',' + re.sub('(\d\d)(\d\d)', r"\1:\2", s[i]['ATIME'].encode('utf-8'))\
                       + ',' + re.sub('(\d\d)(\d\d)', r"\1:\2", s[i]['STIME'].encode('utf-8')) + "\n");
                buffer += (s[i]['STNO'].encode('utf-8') + ',' + s[i]['SNAME'].encode('utf-8')\
                       + ',' + re.sub('(\d\d)(\d\d)', r"\1:\2", s[i]['ATIME'].encode('utf-8'))\
                       + ',' + re.sub('(\d\d)(\d\d)', r"\1:\2", s[i]['STIME'].encode('utf-8')) + "\n");
    buffer += ("\n");

print(buffer.decode('utf-8'));

with open('XJA.txt','wb') as f:
            if f.tell() == 0:
                f.write('\xef\xbb\xbf');
            f.write(buffer)


bin_count11(0b000000000001111111111111000011111111111111000)
bin_count12(0b0000001010101010101010101010100)
bin_count17(0b0001000000000000110000011000001)
bin_count17(0b011000011100001110000111000011)
bin_count17(0b011000011100001110000111000011)
bin_count17(0b011000011100001110000111000011) Mon
56000D210510|QEH|NCG|D2105|13|0100001010000101000011111101010 consecutive6 Thu
'''

'''
python
from view_train_list import *
station = getStation()
buffer = compress_train_list('js/train_list.js',station) # TODO
exit()
gzip -c9 ${path}cycle.txt > ${path}cycle.txt.gz

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
# all train_list_*.js in file
import os
import glob
from view_train_list import *

for fn0 in glob.glob(r'js\train_list_*.js'):
    # print('%s %s'%(fn0,time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(os.path.getmtime(fn0)))))
    t0 = os.path.getmtime(fn0)
    t = 0
    fn1 = 'js/station_name_180112.js'
    for fn in glob.glob(r'js\station_name_*.js'):
        t1 = os.path.getmtime(fn)
        if t < t1 and t1 < t0:
            fn1 = fn
            t = t1
    print('%s %s'%(fn0,fn1))
    station = getStation(fn1)
    buffer = compress_train_list(fn0,station) # TODO
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
import json
import re
import time
import requests

def hash_tele(s):
    if len(s) < 3:
        return 0
    return (ord(s[2])-65) * 26 *26 + (ord(s[0])-65) * 26 + (ord(s[1])-65)

def unhash_tele(n):
    return chr(n/26%26+65) + chr(n%26+65) + chr(n/26/26+65)

def getsearch(kw, cache=1):
    fn = ''
    if cache and os.path.exists(fn):
        with open(fn, 'r') as f:
            data = f.read()
        search = json.loads(data)
        return search, len(search)
    #
    url = "http://dynamic.12306.cn/yjcx/doPickJZM?param=" + kw + "&type=1&czlx=0"
    # header = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:59.0) Gecko/20100101 Firefox/59.0"}
    header = {
        "User-Agent": "Netscape 5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36"}
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
        with open(fn, 'wb') as f:
            f.write(resp.content)
        print('save  %-3s %2d' % (
            kw, len(search)
        ))
        return search, len(search)
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

kw = ''
st = []
for i in range(ord('Z'), ord('@'), -1):
            k = kw + chr(i)
            if chr(i) not in 'IOUV':
                st.append(k)

map = [None for i in range(26*26*26)]

dfsSearchAll(map, st)

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

writecsv("DBM.csv", ret)
'''
