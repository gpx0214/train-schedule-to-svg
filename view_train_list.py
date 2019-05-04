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


def date_diff(date, diff):
    match = re.findall(r'(\d+)-(\d+)-(\d+)', date, re.I | re.M)[0]
    y = int(match[0])
    m = int(match[1])
    d = int(match[2])
    day_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    day_month[2 - 1] = 28
    if y % 4 == 0:
        day_month[2 - 1] = 29
    if y % 100 == 0:
        day_month[2 - 1] = 28
    if y % 400 == 0:
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
            if y % 4 == 0:
                day_month[2 - 1] = 29
            if y % 100 == 0:
                day_month[2 - 1] = 28
            if y % 400 == 0:
                day_month[2 - 1] = 29
    #
    while d < 1:
        m -= 1
        while m < 1:
            y -= 1
            day_month[2 - 1] = 28
            if y % 4 == 0:
                day_month[2 - 1] = 29
            if y % 100 == 0:
                day_month[2 - 1] = 28
            if y % 400 == 0:
                day_month[2 - 1] = 29
            m += 12
        d += day_month[(m-1) % 12]
    #
    return '%04d-%02d-%02d' % (y, m, d)


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


def cmpby0_i2_i3_m4_i5(a1, a2):
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
    n1 = int(a1[2])
    n2 = int(a2[2])
    if n1 > n2:
        return 1
    if n1 < n2:
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
    if int(a1[5]) > int(a2[5]):
        return 1
    if int(a1[5]) < int(a2[5]):
        return -1
    return 0


# station_name.js
def getStation(fn):
    # f = open(fn, 'r',encoding = 'utf8'); #py3
    with open(fn, 'r') as f:  # py2
        s = f.read()
    a = re.findall(r'\'\@([^\']+)\'', s, re.I | re.M)[0]
    s = a.split('@')
    for i in range(len(s)):
        s[i] = s[i].split('|')
    print('read %d stations in %s' % (len(s), fn))
    s.append(["tsn", "唐山南", "TNP", "tangshannan", "tsn", "-1"])
    s.append(["gye", "古冶", "GYP", "guye", "gy", "-1"])
    s.append(["", "香港红磡", "JQO", "xiangganghongkan", "xghk", "-1"])
    s.append(["jlo", "九龙", "JQO", "jiulong", "jl", "-1"])
    s.append(["xgl", "香港西九龙", "XJA", "hkwestkowloon", "xgxjl", "-1"])
    s.append(['jsw', '金山卫', 'BGH', 'jinshanwei', 'jsw', '-1'])
    s.append(['mji', '梅江', 'MKQ', 'meijiang', 'mj', '-1'])
    s.append(['ylo', '元龙', 'YLY', 'yuanlong', 'yl', '-1'])
    s.append(['bdl', '八达岭', 'ILP', 'badaling', 'bdl', '-1'])
    s.append(['nsb', '南山北', 'NBQ', 'nanshanbei', 'nsb', '-1'])
    s.append(['', '车墩', 'CDH', 'chedun', 'cd', '-1'])
    s.append(['', '羊木', 'YMJ', 'yangmu', 'ym', '-1'])
    return s


def telecode(s, station):
    for i in range(len(station)):
        if s == station[i][1]:
            return station[i][2]
    # print(s)
    return ''


# train_list.js
def openTrainList(fn):
    # f = open(fn, 'r',encoding= 'utf8') #py3
    with open(fn, 'r') as f:  # py2
        _ = f.read(16)
        data = f.read()
    return json.loads(data)


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
    t1 = telecode(a['from_station'].encode('utf-8'), station)
    t2 = telecode(a['to_station'].encode('utf-8'), station)
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


# timetable train_list.js
def processA(a, date, station):
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
    match = re.findall(r'(.*)\((.*)-(.*)\)',
                       a['station_train_code'], re.I | re.M)[0]
    t1 = telecode(match[1].encode('utf-8'), station)
    t2 = telecode(match[2].encode('utf-8'), station)
    if not t1:
        if platform.system() == "Windows":
            print(match[1].encode('gbk') +
                  " telecode not found! " + match[0].encode('gbk'))
        else:
            print(match[1].encode('utf-8') +
                  " telecode not found! " + match[0].encode('utf-8'))
        t1 = "AAA"
        # return []
    if not t2:
        if platform.system() == "Windows":
            print(match[2].encode('gbk') +
                  " telecode not found! " + match[0].encode('gbk'))
        else:
            print(match[2].encode('utf-8') +
                  " telecode not found! " + match[0].encode('utf-8'))
        t2 = "AAA"
        # return []
    return getSch12306(t1, t2, a['train_no'], date)


# timetable
def getSch12306(t1, t2, train_no, date):
    name = 'sch/' + train_no + '.json'
    try:
        fn = os.path.join(os.path.dirname(os.path.abspath(__file__)), name)
    except:
        fn = name
    if os.path.exists(fn):
        with open(fn, 'r') as f:
            data = f.read()
        sch = json.loads(data)
        if sch['status'] == True and sch['httpstatus'] == 200 and len(sch['data']['data']):
            return sch['data']['data']
    #
    url = "https://kyfw.12306.cn/otn/czxx/queryByTrainNo?train_no=" + train_no + \
        "&from_station_telecode=" + t1 + \
        "&to_station_telecode=" + t2 + "&depart_date=" + date
    # header = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:59.0) Gecko/20100101 Firefox/59.0"}
    header = {
        "User-Agent": "Netscape 5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36"}
    try:
        resp = requests.get(url, headers=header, timeout=20)
    except:
        print('Net Error ' + train_no)
        return []
    body = resp.content.decode('utf-8')  # bytes -> str (ucs2)
    try:
        sch = json.loads(body)
    except ValueError:
        print('ValueError ' + train_no)
        return []
    if sch['status'] == True and sch['httpstatus'] == 200 and len(sch['data']['data']):
        with open(fn, 'wb') as f:
            f.write(resp.content)
        print('%s %s %s %2d' % (train_no, t1, t2, len(sch['data']['data'])))
        return sch['data']['data']
    else:
        print('data error %s %s %s %s' % (train_no, t1, t2, date))
        return []


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
        search = json.loads(data)
        if search['status'] == True and len(search['data']):
            print('read  %-3s %3d %5s-%5s' % (
                kw, len(search['data']),
                search['data'][0]['station_train_code'],
                search['data'][-1]['station_train_code'])
            )
            return search['data'], len(search['data'])
    #
    url = "https://search.12306.cn/search/v1/train/search?keyword=" + \
        kw + "&date=" + yyyymmdd
    # header = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:59.0) Gecko/20100101 Firefox/59.0"}
    header = {
        "User-Agent": "Netscape 5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36"}
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
    if not 'data' in search:
        print('key data not exist' + kw)
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


def searchAll12306(date, cache=1):
    st = ["90", "50", "10", "C", "D", "G", "", "K", "Y", "P", "T", "Z"]
    maxlen = 70000
    arr = [None for i in range(maxlen)]
    while(len(st)):
        kw = st.pop()
        jump = 0
        if kw == "Y" or kw == "":
            jump = 1
        max_depth = 3
        res = []
        if not jump:
            res, ret = getsearch12306(kw, date, cache)
            if ret == -1:
                res, ret = getsearch12306(kw, date, cache)
        max_index = -1
        for i in range(len(res)):
            arr[hash_no(
                res[i]['station_train_code'].encode('utf-8')
            ) - 1] = res[i]
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
    return arr


def checkSearch12306(arr, station, date):
    for i in range(0, len(arr)):
        if arr[i] == None:
            continue
        for retry in range(3):
            sch = processS(arr[i], date, station)
            if len(sch):
                break
            time.sleep(1 << retry)


def savedatecsvS(arr, station, date):
    num = 0
    stat = [0 for i in range(1440)]
    ret = [[] for i in range(1440)]
    for i in range(0, len(arr)):
        if arr[i] == None:
            continue
        a = arr[i]
        if (a['station_train_code'] in a['train_no']) == False:
            # print(a['station_train_code'] +' '+ a['train_no']); #切换上下行
            continue
        schdata = processS(a, date, station)
        s = schToCsv(schdata)
        num += len(s)
        for row in s:
            if len(row) >= 6:
                minute = getmin(row[4])
                # stat[minute] += 1
                ret[minute].append(row)
            # tele = telecode(row[1]);
            # if True or tele and tele[2] == 'P':
            # num = num+1;
            # stat[minute] = stat[minute]+1;
    # print(num)
    # sort = sorted(time_list, cmpbyTime)
    sort = []
    for key in range(len(ret)):
        stat[key] = len(ret[key])
        for row in ret[key]:
            sort.append(row)
    # print(print_stat(stat))
    if len(sort):
        try:
            fn = os.path.join(os.path.dirname(
                os.path.abspath(__file__)), "delay/sort"+date+".csv")
        except:
            fn = "delay/sort"+date+".csv"
        with open(fn, "wb") as f:  # use wb on win, or get more \r \r\n
            if f.tell() == 0:
                f.write('\xef\xbb\xbf')
            writer = csv.writer(f)
            writer.writerows(sort)
    return num


# train_list.js
def checkAllSch12306(t, station):
    for date in sorted(t.keys()):
        print(date)
        checkDateSch12306(t[date], station, date)


def checkDateSch12306(d, station, date):
    for train_class in d:
        for i in range(0, len(d[train_class])):
            for retry in range(3):
                sch = processA(d[train_class][i], date, station)
                if len(sch):
                    break
                time.sleep(1 << retry)


def savecsv(t, station):
    for date in sorted(t.keys()):
        print(date)
        savedatecsv(t[date], station, date)


def savedatecsv(d, station, date):
    num = 0
    stat = [0 for i in range(1440)]
    ret = [[] for i in range(1440)]
    for train_class in d:
        for i in range(0, len(d[train_class])):
            a = d[train_class][i]
            match = re.findall(r'(.*)\((.*)-(.*)\)',
                               a['station_train_code'], re.I | re.M)[0]
            if (match[0] in a['train_no']) == False:
                # print(match[0] +' '+ a['train_no']); #切换上下行
                continue
            schdata = processA(d[train_class][i], date, station)
            s = schToCsv(schdata)
            num += len(s)
            for row in s:
                if len(row) >= 6:
                    minute = getmin(row[4])
                    # stat[minute] += 1
                    ret[minute].append(row)
                # tele = telecode(row[1]);
                # if True or tele and tele[2] == 'P':
                # num = num+1;
                # stat[minute] = stat[minute]+1;
    # print(num)
    # sort = sorted(time_list, cmpbyTime)
    sort = []
    for key in range(len(ret)):
        stat[key] = len(ret[key])
        for row in ret[key]:
            sort.append(row)
    # print(print_stat(stat))
    #
    if len(sort):
        try:
            fn = os.path.join(os.path.dirname(
                os.path.abspath(__file__)), "delay/sort"+date+".csv")
        except:
            fn = "delay/sort"+date+".csv"
        with open(fn, "wb") as f:  # use wb on win, or get more \r \r\n
            if f.tell() == 0:
                f.write('\xef\xbb\xbf')
            writer = csv.writer(f)
            writer.writerows(sort)
    return num

# savecsv(t, station)


def schToCsv(s):
    # buffer = ''
    ret = []
    day = 0
    last = 0
    for i in range(0, len(s)):
        # print(s[0]['station_train_code'].encode('utf-8') + ',' + s[i]['station_name'].encode('utf-8') + ',' + s[i]['start_time'].encode('utf-8') + ',' + s[i]['arrive_time'].encode('utf-8')); # 打印时刻
        if getmin(s[i]['arrive_time'].encode('utf-8')) > -1 and i > 0:
            minute = getmin(s[i]['arrive_time'].encode('utf-8'))
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
                s[i]['station_name'].encode('utf-8'),
                s[i]['station_no'].encode('utf-8'),
                str(day),
                s[i]['arrive_time'].encode('utf-8'),
                '0'
            ])
        #
        if getmin(s[i]['start_time'].encode('utf-8')) > -1 and i < len(s)-1:
            minute = getmin(s[i]['start_time'].encode('utf-8'))
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
                s[i]['station_name'].encode('utf-8'),
                s[i]['station_no'].encode('utf-8'),
                str(day),
                s[i]['start_time'].encode('utf-8'),
                '1'
            ])
    # return buffer
    return ret


def readcsv(fn):
    with open(fn, 'r') as f:  # py2
        if f.read(3) != '\xef\xbb\xbf':
            f.seek(0, 0)
        data = f.read()
    c = data.split('\n')
    for i in range(len(c)):
        c[i] = c[i].split(',')
    return c


# line
def openMilage(fn):
    with open(fn, 'r') as f:  # py2
        if f.read(3) != '\xef\xbb\xbf':
            f.seek(0, 0)
        data = f.read()
    m = data.split('\n')
    ret = []
    for i in range(len(m)):
        sp = m[i].split(' ')
        if len(sp) >= 2:
            ret.append(sp)
    return ret


def getkm(s, m):
    for i in range(len(m)):
        if len(m[i]) > 1 and s == m[i][0]:
            return m[i][1]
    return -1


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
    buffer += '<polyline name="%s" class="%s" points="' % (
        s[0]['station_train_code'].encode('utf-8'),
        s[0]['station_train_code'].encode('utf-8')[:1])
    for i in range(0, len(s)):
        x = getmin(s[i]['arrive_time'].encode('utf-8'))
        y = getkm(s[i]['station_name'].encode('utf-8'), m)
        if y > -1 and i > 0:
            if x < lastx:
                day += 1
                # 1440, (lasty-y)*x/((1440+x-lastx))+y
                buffer += '%d,%d "/>\n<polyline name="%s+%d" class="polyline%s" points="%d,%d ' % (
                    1440,
                    (int(lasty)-int(y))*int(x) /
                    ((1440+int(x)-int(lastx)))+int(y),
                    s[0]['station_train_code'].encode('utf-8'), day,
                    s[0]['station_train_code'].encode('utf-8')[:1],
                    0,
                    (int(lasty)-int(y))*int(x) /
                    ((1440+int(x)-int(lastx)))+int(y)
                )
            lastx = x
            lasty = y
            buffer += '%s,%s ' % (x, y)
        #
        x = getmin(s[i]['start_time'].encode('utf-8'))
        y = getkm(s[i]['station_name'].encode('utf-8'), m)
        if y > -1 and i < len(s)-1:
            if x < lastx:
                day += 1
                buffer += '%d,%d "/>\n<polyline name="%s+%d" class="polyline%s" points="%d,%d ' % (
                    1440,
                    (int(lasty)-int(y))*int(x) /
                    ((1440+int(x)-int(lastx)))+int(y),
                    s[0]['station_train_code'].encode('utf-8'), day,
                    s[0]['station_train_code'].encode('utf-8')[:1],
                    0,
                    (int(lasty)-int(y))*int(x) /
                    ((1440+int(x)-int(lastx)))+int(y)
                )
            lastx = x
            lasty = y
            buffer += '%s,%s ' % (x, y)
    buffer += '"/>\n'
    return buffer


def csvToPolyline(c, m):
    # ['K868,\xe6\xb3\x8a\xe5\xa4\xb4,05,1,00:00,0']
    if (len(c)) <= 0:
        return ''
    buffer = ''
    day = 0
    lastx = 0
    lasty = 0
    buffer += '<polyline name="%s" class="polyline%s" points="' \
        % (c[0][0], c[0][0][:1])
    for i in range(0, len(c)):
        x = getmin(c[i][4])  # + (3 if int(c[i][5])>0 else (-2)) #
        y = getkm(c[i][1], m)
        if y > -1:
            if x < lastx:
                day += 1
                # 1440, (lasty-y)*x/((1440+x-lastx))+y
                buffer += '%d,%d "/>\n<polyline name="%s+%d" class="polyline%s" points="%d,%d ' % (
                    1440,
                    (int(lasty)-int(y))*int(x) /
                    ((1440+int(x)-int(lastx)))+int(y),
                    c[0][0], day, c[0][0][:1],
                    0,
                    (int(lasty)-int(y))*int(x) /
                    ((1440+int(x)-int(lastx)))+int(y)
                )
            lastx = x
            lasty = y
            buffer += '%s,%s ' % (x, y)
    buffer += '"/>\n'
    return buffer


def csvToSvg(m, c, rule=''):
    r = re.compile('^' + rule + '$', re.IGNORECASE | re.MULTILINE)
    maxlen = 70000
    arr = [[] for i in range(maxlen)]

    for i in range(len(c)):
        if len(c[i]) < 2:
            continue
        if getkm(c[i][1], m) > -1:
            # print(hash_no(c[i][0]))
            arr[hash_no(c[i][0])].append(c[i])
    #
    buffer = ''
    buffer += '<?xml version="1.0" standalone="no"?>\n'
    buffer += '<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" \n'
    buffer += '"http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">\n'
    buffer += '<svg width="%s" height="%s" version="1.1" \n' % (1440, 2450)
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
            arr[i] = sorted(arr[i], cmpby0_i2_i3_m4_i5)
            buffer += csvToPolyline(arr[i], m)
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


def hash_no(s):
    items = [('Z', 10000), ('T', 20000), ('K', 30000),
             ('G', 40000), ('D', 50000), ('C', 60000),
             ('Y', 00000), ('S', 60000), ('P', 00000)]  # ('Y',70000),('S',71000),('P',80000)
    d = dict(items)
    train_class = d[s[0]] if s[0] in d else 0
    n = int(re.sub(r'\D+', '', s))
    return train_class + n


def unhash_no(n):
    items = [('Z', 10000), ('T', 20000), ('K', 30000),
             ('G', 40000), ('D', 50000), ('C', 60000),
             ('Y', 00000), ('S', 60000), ('P', 00000)]  # ('Y',70000),('S',71000),('P',80000)
    head = ["", "Z", "T", "K", "G", "D", "C"]
    if n > 70000:
        return ""
    train_class = head[(n-1) // 10000]
    if n <= 1000:
        train_class = "Y"
    if n <= 100:
        train_class = "P"
    if n > 60000 and n <= 61000:
        train_class = "C"
    for i in range(len(items)):
        if train_class == items[i][0]:
            return train_class + str(n-items[i][1])
    return str(n)


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


LeftTicketUrl = "leftTicket/queryX"


def getLeftTicket(t1, t2, date):
    url = "https://kyfw.12306.cn/otn/" + LeftTicketUrl + "?leftTicketDTO.train_date=" + date + \
        "&leftTicketDTO.from_station=" + t1 + \
        "&leftTicketDTO.to_station=" + t2 + "&purpose_codes=ADULT"
    # header = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:59.0) Gecko/20100101 Firefox/59.0"}
    header = {
        "User-Agent": "Netscape 5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36"}
    try:
        resp = requests.get(url, headers=header, timeout=20)
    except:
        print('Net Error ' + t1 + ' ' + t2 + ' ' + date)
        return []
    body = resp.content.decode('utf-8')  # bytes -> str (ucs2)
    try:
        ticket = json.loads(body)
    except ValueError:
        print('ValueError ' + t1 + ' ' + t2 + ' ' + date)
        return []
    if ticket['status'] == True and ticket['httpstatus'] == 200 and len(ticket['data']['result']):
        with open('ticket/' + date + '_' + t1 + '_' + t2 + '.json', 'wb') as f:
            f.write(resp.content)
        print(t1 + ' ' + t2 + ' ' + date + ' ' +
              str(len(ticket['data']['result'])))
        return ticket['data']['result']
    else:
        print("data error " + t1 + ' ' + t2 + ' ' + date)
        return []


def checkLeftTicket(t1, t2, date):
    ticket = getLeftTicket(t1, t2, date)
    for i in ticket['data']['result']:
        sp = i.split('|')
        if len(sp) > 36:
            print(sp[3] + ' ' + sp[2]+' ' + sp[4]+' ' + sp[5])
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
        "User-Agent": "Netscape 5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36"}
    resp = requests.get(url, headers=header, timeout=20)
    body = resp.content.decode('utf-8')
    match = re.findall(r'<p class="warring">最后更新时间为(\d+)月(\d+)日 (\d+)点(\d+)分。</p>',
                       body, re.I | re.M)[0]
    ret = '%s-%s %s:%s' % (
        match[0].encode('utf-8'),
        match[1].encode('utf-8'),
        match[2].encode('utf-8'),
        match[3].encode('utf-8')
    )
    return ret


def gtzwd(date, s):
    name = 'delay/gt_' + date + '_' + s + '.json'
    try:
        fn = os.path.join(os.path.dirname(os.path.abspath(__file__)), name)
    except:
        fn = name
    url = 'http://www.gtbyxx.com/wxg/inter/ky/getTrainZwd'
    j = {"trainNo": s}
    header = {
        "User-Agent": "Netscape 5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36"}
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
    #kv = 0
    lastq = -1
    lastcolon = -1
    lastkey = ''
    quot = 0
    while index < len(data):
        c = data[index]
        if c == "{":
            #if layer == 1:
                # print("%s %d"%(data[index],index))
                #kv = 0
            layer += 1
        elif c == "[":
            layer += 1
        elif c == "}":
            if layer == 1:
                # print("%s %d"%(data[index],index))
                #kv = 0
                #print("%s %d %d %s %s" % (lastkey, lastcolon+1, index, data[lastcolon+1], data[index-1]))
                ret.append([lastkey, lastcolon+1, index])
            layer -= 1
        elif c == "]":
            layer -= 1
        elif c == ":":
            if layer == 1:
                # print("%s %d"%(data[index],index))
                #kv = 1
                lastcolon = index
        elif c == ",":
            if layer == 1:
                # print("%s %d"%(data[index],index))
                #kv = 0
                #print("%s %d %d %s %s" % (lastkey, lastcolon+1, index, data[lastcolon+1], data[index-1]))
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


def bin_count11(n):
    ans = 0
    temp = n
    while temp:
        ans += 1
        # print('{:0>45b}'.format(temp))
        temp &= n >> ans
    return ans


def bin_count12(n):
    ans = 0
    temp = n
    while temp:
        ans += 2
        # print('{:0>45b}'.format(temp))
        temp &= n >> ans
    return ans


def bin_count17(n):
    ans = 0
    temp = n
    while temp:
        ans += 7
        # print('{:0>45b}'.format(temp))
        temp &= n >> ans
    return ans


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


def get_one_slice(n, size):
    ret = []
    a = -1
    b = -1
    status = 0
    for i in range(size):
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


def get_zero_slice(n, size):
    ret = []
    a = -1
    b = -1
    status = 1
    for i in range(size):
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
            ans += ","
        if ret[i][0] == ret[i][1]:
            ans += re.sub(r'(\d\d)(\d\d)-(\d+)-(\d+)',
                          r"\3\4", date_diff(base_date, ret[i][0]))
            continue
        else:
            ans += '%s-%s' % (
                re.sub(r'(\d\d)(\d\d)-(\d+)-(\d+)',
                       r"\3\4", date_diff(base_date, ret[i][0])),
                re.sub(r'(\d\d)(\d\d)-(\d+)-(\d+)',
                       r"\3\4", date_diff(base_date, ret[i][1]))
            )
    return ans


def compress_bin_vector(date_bin, base_date, size):
    if date_bin == all1(size):  # 图定
        return "", 1
    one_slice = get_one_slice(date_bin, size)
    zero_slice = get_zero_slice(date_bin, size)
    bin_weight = bin_cnt(date_bin)
    if bin_weight < size / 7:  # bin_weight / bin_cnt(mask) < 1/7
        return slice_to_str(one_slice, base_date), 10
    if len(one_slice) <= len(zero_slice):
        if len(one_slice) <= 2:
            return slice_to_str(one_slice, base_date), 8
    else:
        if len(zero_slice) <= 1:
            return "停" + slice_to_str(zero_slice, base_date), 9
    if bin_weight > size - size / 7:  # bin_weight / bin_cnt(mask) > 6/7
        return "停" + slice_to_str(zero_slice, base_date), 11
    for step in [7, 2, 3, 4, 5, 6]:
        size_floor = size//step*step
        if ((date_bin & all1(size_floor)) % all01(size_floor, step, 1)) == 0:
            # 取循环节
            c = (date_bin & all1(size_floor)) // all01(size_floor, step, 1)
            if (all1(size) & all01(size, step, c)) == date_bin:
                if step == 7:
                    return 'w' + cycle7(c, weekday(base_date)), step
                return ('{:0>'+str(step)+'b}').format(c), step
            else:
                return ('{:0>'+str(step)+'b} 不完整').format(c) + " " + ('{:0>'+str(size)+'b}').format(date_bin), step
    return ('{:0>'+str(size)+'b}').format(date_bin) + ' consecutive' + str(bin_count11(date_bin)), 0


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


def add_map(train_map, a):
    '''
    add s obj to train_map
    map[key][idx].date |= date
    '''
    key = hash_no(a['station_train_code']) - 1
    found = 0
    for train in train_map[key]:
        if train['train_no'] == a['train_no']:
            train['date'] |= a['date']
            found = 1
            break
    if found == 0:
        train_map[key].append(a)


def compress_train_list(fn0, station=None):
    print('compress_train_list() %s %s' % (fn0, 'station' if station else ''))
    with open(fn0, 'r') as f:
        # with open(fn0, 'r', encoding='utf-8') as f: #py3
        _ = f.read(16)
        data = f.read()
    #
    slice_mark = sorted(mark_json_slice(data))
    print(slice_mark)
    base_date = slice_mark[0][0]
    mask = 0
    maxlen = 70000
    train_map = [[] for i in range(maxlen)]
    for i in range(len(slice_mark)):
        # date_diff(base_date, i)
        date = slice_mark[i][0]
        d = json.loads(data[slice_mark[i][1]:slice_mark[i][2]])
        # print(date)
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
                a['date'] = (1 << i)
                add_map(train_map, a)
                #
        ss += '\t%d' % (cnt)
        if cnt:
            mask |= (1 << i)
        print(ss)
    #
    size = bin_cnt(mask)
    train_arr = []
    for key in range(maxlen):
        for train in train_map[key]:
            for retry in range(3):
                one_slice = get_one_slice(train['date'], size)
                if len(one_slice):
                    date = date_diff(base_date, one_slice[0][0])
                else:
                    date = base_date
                sch = processS(train, date, station)
                train['total_num'] = len(sch)
                if len(sch):
                    break
                time.sleep(1 << retry)
            train_arr.append(train)
    #
    #
    stat = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    buffer = ''
    for train in train_arr:
        t1 = ''
        t2 = ''
        if station != None:
            t1 = telecode(train['from_station'].encode('utf-8'), station)
            t2 = telecode(train['to_station'].encode('utf-8'), station)
        if not t1:
            t1 = train['from_station'].encode('utf-8')
        if not t2:
            t2 = train['to_station'].encode('utf-8')
        #
        val, status = compress_bin_vector(train['date'], base_date, size)
        stat[status] += 1
        #
        buffer += '%s|%s|%s|%s|%d|%s\n' % (
            train['train_no'].encode('utf-8'),
            t1,
            t2,
            train['station_train_code'].encode('utf-8'),
            train['total_num'],
            val
        )
    #
    print(stat)
    #
    fn = os.path.join(os.path.dirname(
        os.path.abspath(__file__)), fn0 + '.txt')
    with open(fn, 'wb') as f:
        if f.tell() == 0:
            f.write('\xef\xbb\xbf')
        f.write(buffer)
    #
    return buffer


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
        arr = train_list_train_no_array(t, 70000)
        stat, train_num = train_list_stat_block(arr, 100, 70000)
        s, block = print_block(stat)
        print(str(train_num) + " trains")
        print(str(block) + " blocks")
        print(s)
        print(train_list_class_str(t))
        station = getStation(fn1)
        checkAllSch12306(t, station)
        savecsv(t, station)
        if platform.system() == "Windows":
            os.system('pause')
    except Exception, e:
        print(str(Exception))
        if platform.system() == "Windows":
            os.system('pause')
    '''

    station = getStation(fn1)

    buffer = compress_train_list(fn0, station)

    with open(fn0, 'r') as f:
        _ = f.read(16)
        data = f.read()

    slice_mark = sorted(mark_json_slice(data))

    for i in range(len(slice_mark)):
        s = ''
        d = json.loads(data[slice_mark[i][1]:slice_mark[i][2]])
        date = slice_mark[i][0]
        # s += train_list_day_class_str(d, date)
        # checkDateSch12306(d, station, date)
        n = savedatecsv(d, station, date)
        s += '\t%d' % (n)
        print(s)
        del d

'''
from view_train_list import *

station = getStation('js/station_name.js')

import datetime
base_date = datetime.datetime.now().strftime('%Y-%m-%d');
for d in range(1,2):
    date = date_diff(base_date,d)
    arr = searchAll12306(date,cache=0)
    checkSearch12306(arr, station, date)
    savedatecsvS(arr, station, date)
    stat, train_num = train_list_stat_block(arr, 100, 70000)
    s, block = print_block(stat)
    print(str(train_num) + " trains")
    print(str(block) + " blocks")
    print(s)

'''

'''
from view_train_list import *

station = getStation('js/station_name.js')
# savecsv(t,station)

m = openMilage('test/京沪高速线里程.txt')
c = readcsv('delay/sort2018-04-12.csv')
buffer,_ = csvToSvg(m, c, "(?!G7[012356]\d{1,3})|[G]\d{1,4}")

fn = 'test/180412京沪高速.svg'
with open(fn, "wb") as f:  # use wb on win, or get more \r \r\n
    if f.tell() == 0:
        f.write('\xef\xbb\xbf')
    f.write(buffer)

m = openMilage('test/京广高速线里程.txt')
c = readcsv('delay/sort2019-04-12.csv')
buffer,_ = csvToSvg(m, c, "[GDC]\d{1,4}")

fn = 'test/190412京广高速.svg'
with open(fn, "wb") as f:  # use wb on win, or get more \r \r\n
    if f.tell() == 0:
        f.write('\xef\xbb\xbf')
    f.write(buffer)

m = openMilage('test/京沪线里程.txt')
c = readcsv('delay/sort2019-04-12.csv')
buffer,_ = csvToSvg(m, c, "[ZTKPQWY]\d{1,4}|^\d{1,4}|D7\d{1,3}")

fn = 'test/190412京沪线.svg'
with open(fn, "wb") as f:  # use wb on win, or get more \r \r\n
    if f.tell() == 0:
        f.write('\xef\xbb\xbf')
    f.write(buffer)

m = openMilage('test/京广线里程.txt')
c = readcsv('delay/sort2019-04-12.csv')
buffer,_ = csvToSvg(m, c, "[ZTKPQWY]\d{1,4}|C7[01]\d{2}|D75\d{2}|D6[67]\d{2}")

fn = 'test/190412京广线.svg'
with open(fn, "wb") as f:  # use wb on win, or get more \r \r\n
    if f.tell() == 0:
        f.write('\xef\xbb\xbf')
    f.write(buffer)

m = openMilage('test/京九线里程.txt')
c = readcsv('delay/sort2019-04-12.csv')
buffer,_ = csvToSvg(m, c, "[ZTKPQWY]\d{1,4}|^\d{1,4}")

fn = 'test/190412京九线.svg'
with open(fn, "wb") as f:  # use wb on win, or get more \r \r\n
    if f.tell() == 0:
        f.write('\xef\xbb\xbf')
    f.write(buffer)

m = openMilage('test/成昆线里程.txt')
c = readcsv('delay/sort2019-04-12.csv')
buffer,_ = csvToSvg(m, c, "[ZTKPQWY]\d{1,4}|^\d{1,4}")

fn = 'test/190412成昆线.svg'
with open(fn, "wb") as f:  # use wb on win, or get more \r \r\n
    if f.tell() == 0:
        f.write('\xef\xbb\xbf')
    f.write(buffer)

m = openMilage('test/陇海线里程.txt')
c = readcsv('delay/sort2019-04-12.csv')
buffer,_ = csvToSvg(m, c, "[ZTKPQWY]\d{1,4}|^\d{1,4}")

fn = 'test/190412陇海线.svg'
with open(fn, "wb") as f:  # use wb on win, or get more \r \r\n
    if f.tell() == 0:
        f.write('\xef\xbb\xbf')
    f.write(buffer)

m = openMilage('test/京沪高速线里程.txt')
c = readcsv('delay/sort2019-04-12.csv')
buffer,_ = csvToSvg(m, c, "(?!G7[012356]\d{1,3})[G]\d{1,4}")

fn = 'test/190412京沪高速.svg'
with open(fn, "wb") as f:  # use wb on win, or get more \r \r\n
    if f.tell() == 0:
        f.write('\xef\xbb\xbf')
    f.write(buffer)

'''

'''
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
56000D210510|QEH|NCG|D2105|13|0100001010000101000011111101010 consecutive6 Thu
'''

'''
python
from view_train_list import *
station = getStation('js/station_name.js')
buffer = compress_train_list('js/train_list.js',station)
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

'''
import os
import glob
from view_train_list import *

for fn0 in glob.glob(r'js\train_list_*.js'):
    #print('%s %s'%(fn0,time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(os.path.getmtime(fn0)))))
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
    buffer = compress_train_list(fn0,station)
'''

'''
train_map = [[] for i in range(maxlen)]

a = {}
a['station_train_code'] = u"Z1"
a['from_station'] = u"Z1"
a['to_station'] = u"Z1"
a['train_no'] = u"24000000Z101"
a['total_num'] = 6
a['date'] = 2

addmap(train_map,a)
'''