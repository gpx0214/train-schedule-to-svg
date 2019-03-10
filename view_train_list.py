#!/usr/bin/python
# -*- coding: utf-8 -*-
# tested in python 2.7.15 on win10 x64
# tested in python 2.7.5 on centos7 x64

from __future__ import print_function

import os
import sys
import platform
import re
import json
import csv
import time
#import math
#import random

import requests


import datetime


def date_diff(date, diff):
    match = re.findall(r'(\d+)-(\d+)-(\d+)', date, re.I | re.M)[0]
    y = int(match[0])
    m = int(match[1])
    d = int(match[2])
    day_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
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


def bin_cnt(x):
    ans = 0
    while x:
        x &= x - 1
        ans += 1
    return ans


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


def cmpbyTrain(a1, a2):
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
    d1 = int(a1[2])
    d2 = int(a2[2])
    if d1 > d2:
        return 1
    if d1 < d2:
        return -1
    t1 = getmin(a1[3])
    t2 = getmin(a2[3])
    if t1 > t2:
        return 1
    if t1 < t2:
        return -1
    if int(a1[4]) > int(a2[4]):
        return 1
    if int(a1[4]) < int(a2[4]):
        return -1
    return 0


def cmpbyTrain0(a1, a2):
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
    if int(a1[4]) > int(a2[5]):
        return 1
    if int(a1[4]) < int(a2[5]):
        return -1
    return 0


def getmin(str):
    try:
        a, b = str.split(':')[0:2]
        return int(a)*60+int(b)
    except:
        return -1


# station_name.js
def getStation(fn):
    # f = open(fn, 'r',encoding = 'utf8'); #py3
    with open(fn, 'r') as f:  # py2
        str = f.read()
    a = re.findall(r'\'\@([^\']+)\'', str, re.I | re.M)[0]
    s = a.split('@')
    for i in range(len(s)):
        s[i] = s[i].split('|')
    s.append(["tsn", "唐山南", "TNP", "tangshannan", "tsn", "-1"])
    s.append(["gye", "古冶", "GYP", "guye", "gy", "-1"])
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


def telecode(str, station):
    for i in range(len(station)):
        if str == station[i][1]:
            return station[i][2]
    # print(str)
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
    #header = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:59.0) Gecko/20100101 Firefox/59.0"}
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
        print ('data error %s %s %s %s' % (train_no, t1, t2, date))
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
            print('read  %-3s %3d %5s-%5s' % (kw, len(search['data']),
                                              search['data'][0]['station_train_code'],
                                              search['data'][-1]['station_train_code']))
            return search['data'], len(search['data'])

    url = "https://search.12306.cn/search/v1/train/search?keyword=" + \
        kw + "&date=" + yyyymmdd
    #header = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:59.0) Gecko/20100101 Firefox/59.0"}
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
    if search['status'] == True and len(search['data']):
        with open(fn, 'wb') as f:
            f.write(resp.content)
        print('save  %-3s %3d %5s-%5s' % (kw, len(search['data']),
                                          search['data'][0]['station_train_code'],
                                          search['data'][-1]['station_train_code']))
        return search['data'], len(search['data'])
    else:
        print ('empty %-3s' % (kw))
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
            arr[hash_no(res[i]['station_train_code'].encode(
                'utf-8')) - 1] = res[i]
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
        sch = processS(arr[i], date, station)
        if len(sch) == 0:
            processS(arr[i], date, station)


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
                #stat[minute] += 1
                ret[minute].append(row)
            #tele = telecode(row[1]);
            # if True or tele and tele[2] == 'P':
            #num = num+1;
            #stat[minute] = stat[minute]+1;
    # print(num)
    #sort = sorted(time_list, cmpbyTime)
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
    for type in d:
        for i in range(0, len(d[type])):
            sch = processA(d[type][i], date, station)
            if len(sch) == 0:
                processA(d[type][i], date, station)


def savecsv(t, station):
    for date in sorted(t.keys()):
        print(date)
        savedatecsv(t[date], station, date)


def savedatecsv(d, station, date):
    num = 0
    stat = [0 for i in range(1440)]
    ret = [[] for i in range(1440)]
    for type in d:
        for i in range(0, len(d[type])):
            a = d[type][i]
            match = re.findall(r'(.*)\((.*)-(.*)\)',
                               a['station_train_code'], re.I | re.M)[0]
            if (match[0] in a['train_no']) == False:
                # print(match[0] +' '+ a['train_no']); #切换上下行
                continue
            schdata = processA(d[type][i], date, station)
            s = schToCsv(schdata)
            num += len(s)
            for row in s:
                if len(row) >= 6:
                    minute = getmin(row[4])
                    #stat[minute] += 1
                    ret[minute].append(row)
                #tele = telecode(row[1]);
                # if True or tele and tele[2] == 'P':
                #num = num+1;
                #stat[minute] = stat[minute]+1;
    # print(num)
    #sort = sorted(time_list, cmpbyTime)
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

#savecsv(t, station)


def schToCsv(s):
    #buffer = ''
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
            #print(s[0]['station_train_code'].encode('utf-8') + ',' + s[i]['station_name'].encode('utf-8') + ',' + s[i]['arrive_time'].encode('utf-8') + ',' + '0');
            #print(s[0]['station_train_code'].encode('utf-8') + ',' + s[i]['station_name'].encode('utf-8') + ',' + s[i]['station_no'].encode('utf-8') + ',' + str(day) + ',' + s[i]['arrive_time'].encode('utf-8') + ',' + '0');
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
            #print(s[0]['station_train_code'].encode('utf-8') + ',' + s[i]['station_name'].encode('utf-8') + ',' + s[i]['start_time'].encode('utf-8') + ',' + '1');
            #print(s[0]['station_train_code'].encode('utf-8') + ',' + s[i]['station_name'].encode('utf-8') + ',' + s[i]['station_no'].encode('utf-8') + ',' + str(day) + ',' + s[i]['start_time'].encode('utf-8') + ',' + '1');
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
                #1440, (lasty-y)*x/((1440+x-lastx))+y
                buffer += '%d,%d "/>\n<polyline name="%s+%d" class="polyline%s" points="%d,%d ' \
                    % (1440, (int(lasty)-int(y))*int(x)/((1440+int(x)-int(lastx)))+int(y),
                       s[0]['station_train_code'].encode('utf-8'), day,
                       s[0]['station_train_code'].encode('utf-8')[:1],
                       0, (int(lasty)-int(y))*int(x)/((1440+int(x)-int(lastx)))+int(y))
            lastx = x
            lasty = y
            buffer += '%s,%s ' % (x, y)
        #
        x = getmin(s[i]['start_time'].encode('utf-8'))
        y = getkm(s[i]['station_name'].encode('utf-8'), m)
        if y > -1 and i < len(s)-1:
            if x < lastx:
                day += 1
                buffer += '%d,%d "/>\n<polyline name="%s+%d" class="polyline%s" points="%d,%d ' \
                    % (1440, (int(lasty)-int(y))*int(x)/((1440+int(x)-int(lastx)))+int(y),
                       s[0]['station_train_code'].encode('utf-8'), day,
                       s[0]['station_train_code'].encode('utf-8')[:1],
                       0, (int(lasty)-int(y))*int(x)/((1440+int(x)-int(lastx)))+int(y))
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
                #1440, (lasty-y)*x/((1440+x-lastx))+y
                buffer += '%d,%d "/>\n<polyline name="%s+%d" class="polyline%s" points="%d,%d ' \
                    % (1440, (int(lasty)-int(y))*int(x)/((1440+int(x)-int(lastx)))+int(y),
                       c[0][0], day, c[0][0][:1],
                       0, (int(lasty)-int(y))*int(x)/((1440+int(x)-int(lastx)))+int(y))
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
            arr[i] = sorted(arr[i], cmpbyTrain0)
            buffer += csvToPolyline(arr[i], m)
    #
    buffer += ('</svg>')
    return buffer, num


def train_list_type_str(t):
    s = ''
    for date in sorted(t.keys()):
        s += train_list_day_type_str(t[date], date)
    return s


def train_list_day_type_str(d, date):
    ss = ''
    ss += (date.encode('utf-8'))
    for type in d:
        ss += ('\t' + type.encode('utf-8') + ' ' + str(len(d[type])))
    #ss += '\n'
    return ss


def hash_no(s):
    items = [('Z', 10000), ('T', 20000), ('K', 30000),
             ('G', 40000), ('D', 50000), ('C', 60000),
             ('Y', 00000), ('S', 60000), ('P', 00000)]  # ('Y',70000),('S',71000),('P',80000)
    d = dict(items)
    type = d[s[0]] if s[0] in d else 0
    n = int(re.sub(r'\D+', '', s))
    return type + n


def unhash_no(n):
    items = [('Z', 10000), ('T', 20000), ('K', 30000),
             ('G', 40000), ('D', 50000), ('C', 60000),
             ('Y', 00000), ('S', 60000), ('P', 00000)]  # ('Y',70000),('S',71000),('P',80000)
    head = ["", "Z", "T", "K", "G", "D", "C"]
    if n > 70000:
        return ""
    type = head[(n-1) // 10000]
    if n <= 1000:
        type = "Y"
    if n <= 100:
        type = "P"
    if n > 60000 and n <= 61000:
        type = "C"
    for i in range(len(items)):
        if type == items[i][0]:
            return type + str(n-items[i][1])
    return str(n)


def train_list_train_no_array(t, maxlen):
    arr = ['' for i in range(maxlen)]
    for date in sorted(t.keys()):
        for type in t[date]:
            # for type in ['Z']:
            for i in range(0, len(t[date][type])):
                # for i in range(0,1):
                a = t[date][type][i]
                match = re.findall(r'(.*)\((.*)-(.*)\)',
                                   a['station_train_code'], re.I | re.M)[0]
                arr[hash_no(match[0].encode('utf-8')) -
                    1] = a['train_no'].encode('utf-8')
    return arr


def train_list_stat_block(arr, step, maxlen):
    cnt = 0
    #step = 100;
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
    #header = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:59.0) Gecko/20100101 Firefox/59.0"}
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
        print ("data error " + t1 + ' ' + t2 + ' ' + date)
        return []


def checkLeftTicket(t1, t2, date):
    ticket = getLeftTicket(t1, t2, date)
    for i in ticket['data']['result']:
        sp = i.split('|')
        if len(sp) > 36:
            print(sp[3] + ' ' + sp[2]+' ' + sp[4]+' ' + sp[5])
            if not os.path.exists('sch/'+sp[2].encode('utf-8')+'.json'):
                s = getSch12306(sp[4], sp[5], sp[2], date)
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


def markJsonSlice(data):
    ret = []
    layer = 0
    index = 0
    kv = 0
    lastq = -1
    lastcolon = -1
    lastkey = ''
    quot = 0
    while index < len(data):
        c = data[index]
        if c == "{":
            if layer == 1:
                #print("%s %d"%(data[index],index))
                kv = 0
            layer += 1
        elif c == "[":
            layer += 1
        elif c == "}":
            if layer == 1:
                #print("%s %d"%(data[index],index))
                kv = 0
                print("%s %d %d %s %s" %
                      (lastkey, lastcolon+1, index, data[lastcolon+1], data[index-1]))
                ret.append([lastkey, lastcolon+1, index])
            layer -= 1
        elif c == "]":
            layer -= 1
        elif c == ":":
            if layer == 1:
                #print("%s %d"%(data[index],index))
                kv = 1
                lastcolon = index
        elif c == ",":
            if layer == 1:
                #print("%s %d"%(data[index],index))
                kv = 0
                print("%s %d %d %s %s" %
                      (lastkey, lastcolon+1, index, data[lastcolon+1], data[index-1]))
                ret.append([lastkey, lastcolon+1, index])
        elif c == '"':
            if layer == 1:
                #print("%s %d %d"%(data[index],index,quot))
                if quot == 0:
                    lastq = index
                    quot = 1
                elif quot == 1:
                    # print("%s"%(data[lastq+1:index]))
                    lastkey = data[lastq+1:index]
                    quot = 0
        index += 1
    return ret


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
    print('input station_name file: ' + fn1)

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
        print(train_list_type_str(t))
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

    with open(fn0, 'r') as f:
        _ = f.read(16)
        data = f.read()

    ret = sorted(markJsonSlice(data))

    for i in range(len(ret)):
        # print(i)
        #start = ret[i][1]
        #end = ret[i][2]
        # print(start)
        # print(end)
        #d = json.loads(data[start:end])
        s = ''
        d = json.loads(data[ret[i][1]:ret[i][2]])
        date = ret[i][0]
        s += (train_list_day_type_str(d, date))
        checkDateSch12306(d, station, date)
        n = savedatecsv(d, station, date)
        s += "\t" + str(n)
        print(s)
        del d


'''
from view_train_list import *

station = getStation('js/station_name.js')

base = datetime.datetime.now().strftime('%Y-%m-%d');
for d in range(1,2):
    date = date_diff(base,d)
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

t = openTrainList('js/train_list.js')
station = getStation('js/station_name.js')
#savecsv(t,station)
m = openMilage('test/京沪高速线里程.txt')
c = readcsv('delay/sort2018-09-30.csv')
buffer,_ = csvToSvg(m, c, "(?!G7[012356]\d{1,3})[G]\d{1,4}")

fn = 'test/180930京沪高速.svg'
with open(fn, "wb") as f:  # use wb on win, or get more \r \r\n
    if f.tell() == 0:
        f.write('\xef\xbb\xbf')
    f.write(buffer)

m = openMilage('test/京广高速线里程.txt')
c = readcsv('delay/sort2018-09-30.csv')
buffer,_ = csvToSvg(m, c, "[GDC]\d{1,4}")

fn = 'test/180930京广高速.svg'
with open(fn, "wb") as f:  # use wb on win, or get more \r \r\n
    if f.tell() == 0:
        f.write('\xef\xbb\xbf')
    f.write(buffer)

m = openMilage('test/京沪线里程.txt')
c = readcsv('delay/sort2019-03-10.csv')
buffer,_ = csvToSvg(m, c, "[ZTK]\d{1,4}|^\d{1,4}|D7\d{1,3}")

fn = 'test/190310京沪线.svg'
with open(fn, "wb") as f:  # use wb on win, or get more \r \r\n
    if f.tell() == 0:
        f.write('\xef\xbb\xbf')
    f.write(buffer)

m = openMilage('test/京广线里程.txt')
c = readcsv('delay/sort2019-03-10.csv')
buffer,_ = csvToSvg(m, c, "[ZTK]\d{1,4}|C7[01]\d{2}|D75\d{2}|D6[67]\d{2}")

fn = 'test/190310京广线.svg'
with open(fn, "wb") as f:  # use wb on win, or get more \r \r\n
    if f.tell() == 0:
        f.write('\xef\xbb\xbf')
    f.write(buffer)

m = openMilage('test/京九线里程.txt')
c = readcsv('delay/sort2019-03-10.csv')
buffer,_ = csvToSvg(m, c, "[ZTK]\d{1,4}|^\d{1,4}")

fn = 'test/190310京九线.svg'
with open(fn, "wb") as f:  # use wb on win, or get more \r \r\n
    if f.tell() == 0:
        f.write('\xef\xbb\xbf')
    f.write(buffer)

'''
#s = processA(t['2018-09-30']['G'][1525], '2018-09-30', station)


'''
fn = "C:\\Users\\Administrator\\ticket1\\2018-09-23_XJA_CBQ.json"

with open(fn,'r') as f: #py2
    data=f.read();

j = json.loads(data)

buffer= '';
for obj in j:
    #obj['TRNO'].encode('utf-8')
    #obj['FST'].encode('utf-8')
    #obj['EST'].encode('utf-8')
    #getSch12306(obj['FST'].encode('utf-8'), obj['EST'].encode('utf-8'), obj['TRNO'].encode('utf-8'), date)
    train_code = obj['STCODE'].encode('utf-8')
    #getSchT(obj['STCODE'].encode('utf-8'), date)
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
'''


'''
from view_train_list import *

fn0 = 'js/train_list.js'

with open(fn0, 'r') as f:
        _ = f.read(16)
        data = f.read()

ret = sorted(markJsonSlice(data))

base = ret[0][0]
base_week = 0
mask = 0
cnt = 0
maxlen = 70000
arr = [None for i in range(maxlen)]
stat = [0 for i in range(maxlen)]
for i in range(len(ret)):
    #date_diff(base, i)
    date = ret[i][0]
    d = json.loads(data[ret[i][1]:ret[i][2]])
    print(date)
    mask |= (1 << i)
    for type in d:
        for ii in range(0, len(d[type])):
            match = re.findall(r'(.*)\((.*)-(.*)\)',d[type][ii]['station_train_code'], re.I | re.M)[0]
            a = {}
            a['station_train_code'] = match[0]
            a['from_station'] = match[1]
            a['to_station'] = match[2]
            a['train_no'] = d[type][ii]['train_no']
            a['total_num'] = 0
            a['date'] = 0
            key = hash_no(match[0].encode('utf-8')) - 1
            if arr[key] == None:
                arr[key] = a
            #输出不同train_no的车次
            if arr[key]['train_no'] != a['train_no']:
                print('%s %s %s %s'%(arr[key]['train_no'], a['train_no'], date, arr[key]['station_train_code']))
                arr[key]['train_no'] = a['train_no']
                cnt += 1
            arr[key]['date'] |= (1 << i)


cnt = [0,0,0,0,0,0,0,0,0,0,0,0]
x = bin_cnt(mask)
f = '{:>5} {:0>'+str(x)+'b}'
flag = 0
for i in range(maxlen):
    if arr[i]:
        if arr[i]['date'] == mask:
            cnt[1]+=1
            continue
        if bin_cnt(arr[i]['date']) * 7 < x: # bin_cnt(arr[i]['date']) / bin_cnt(mask) < 1/7
            #print((f + ' 开行{:>3}日 ').format(arr[i]['station_train_code'].encode('utf-8'), arr[i]['date'], bin_cnt(arr[i]['date'])))
            cnt[9] += 1
            continue
        if bin_cnt(arr[i]['date']) * 7 > x * 6: # bin_cnt(arr[i]['date']) / bin_cnt(mask) > 6/7
            #print((f + ' 停运{:>3}日 ').format(arr[i]['station_train_code'].encode('utf-8'), arr[i]['date'], x - bin_cnt(arr[i]['date'])))
            cnt[10] += 1
            continue
        flag = 0
        for step in [2,3,4,5,6,7]:
            if ((arr[i]['date'] & all1(x//step*step)) % all01(x//step*step, step, 1)) == 0:
                c = (arr[i]['date'] & all1(x//step*step)) // all01(x//step*step, step, 1) # 取循环节
                #if ( all01(x//step*step, step, c) & all01(x//step*step, step, c) ) == arr[i]['date']:
                if ( all01(x, step, c) & all1(x)) == arr[i]['date']:
                    print((f + ' '+ str(step) +'日 {:0>'+str(step)+'b}').format(arr[i]['station_train_code'].encode('utf-8'), arr[i]['date'], c))
                    if step == 2:
                        print("双" if (c == 0b01) else "单")
                    if step == 7:
                        print(cycle7(c, base_week))
                    cnt[step]+=1
                else:
                    print((f + ' '+ str(step) +'日 {:0>'+str(step)+'b} 不完整').format(arr[i]['station_train_code'].encode('utf-8'), arr[i]['date'], c))
                    cnt[step]+=1
                flag = 1
                break
        if flag:
            continue
        #print(f.format(arr[i]['station_train_code'].encode('utf-8'), arr[i]['date']) + ' ' + str(bin_count11(arr[i]['date'])))
        cnt[0] += 1


def all1(x):
    ans = 0
    while x:
        x -= 1
        ans |= 1 << x
    return ans

def all01(x, y, c):
    ans = 0
    ii = 0
    while ii < x:
        ans |= c << ii
        ii += y
    return ans

def bin_count11(n):
    ans = 0
    temp = n
    while temp:
        ans += 1
        #print('{:0>45b}'.format(temp))
        temp &= n >> ans
    return ans

bin_count11(0b000000000001111111111111000011111111111111000)

def bin_count12(n):
    ans = 0
    temp = n
    while temp:
        ans += 2
        #print('{:0>45b}'.format(temp))
        temp &= n >> ans
    return ans

bin_count12(0b0000001010101010101010101010100)

def bin_count17(n):
    ans = 0
    temp = n
    while temp:
        ans += 7
        print('{:0>45b}'.format(temp))
        temp &= n >> ans
    return ans

bin_count17(0b0001000000000000110000011000001)

def cycle7(c, base_week):
    model = '71234567'
    ret = ''
    #c = c | c << 7
    for i in range(1,8):
        if c & (1 << (i - base_week) % 7):
            ret += model[i]
    return ret

cycle7(0b1000001, 0)
cycle7(0b1000001, 1)
cycle7(0b1000001, 2)
cycle7(0b1000001, 3)
cycle7(0b1000001, 4)
cycle7(0b1000001, 5)
cycle7(0b1000001, 6)
cycle7(0b1000001, 7)

'''
