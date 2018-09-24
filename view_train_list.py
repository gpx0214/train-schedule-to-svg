#!/usr/bin/python
# -*- coding: utf-8 -*-
# tested in python 2.7.14 on win10 x64

from __future__ import print_function

import os
import sys
import platform
import re
import json
import csv
import time
import math
import random

import requests


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


def getmin(str):
    try:
        a, b = str.split(':')[0:2]
        return int(a)*60+int(b)
    except:
        return -1


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


def openTrainList(fn):
    # f = open(fn, 'r',encoding= 'utf8') #py3
    with open(fn, 'r') as f:  # py2
        f.read(16)
        data = f.read()
    return json.loads(data)


def processA(a, date, station):
    try:
        fn = os.path.join(os.path.dirname(os.path.abspath(
            __file__)), 'sch/' + a['train_no'].encode('utf-8')+'.json')
    except:
        fn = 'sch/' + a['train_no'].encode('utf-8')+'.json'
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


def getSch12306(t1, t2, train_no, date):
    try:
        fn = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          'sch/' + train_no + '.json')
    except:
        fn = 'sch/' + train_no + '.json'
    if os.path.exists(fn):
        with open(fn, 'r') as f:
            data = f.read()
        sch = json.loads(data)
        if sch['status'] == True and sch['httpstatus'] == 200 and len(sch['data']['data']):
            return sch['data']['data']

    url = "https://kyfw.12306.cn/otn/czxx/queryByTrainNo?train_no=" + train_no + \
        "&from_station_telecode=" + t1 + \
        "&to_station_telecode=" + t2 + "&depart_date=" + date
    #header = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:59.0) Gecko/20100101 Firefox/59.0"}
    header = {
        "User-Agent": "Netscape 5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36"}
    try:
        resp = requests.get(url, headers=header)
    except requests.exceptions.ConnectionError:
        print('ConnectionError ' + train_no)
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
        print(train_no + ' ' + str(len(sch['data']['data'])))
        return sch['data']['data']
    else:
        print ("data error " + train_no)
        return []


def checkAllSch12306(t, station):
    for date in sorted(t.keys()):
        print(date)
        for type in t[date]:
            for i in range(0, len(t[date][type])):
                processA(t[date][type][i], date, station)


def savecsv(t, station):
    for date in sorted(t.keys()):
        print(date)
        #buffer = ''
        #time_list = []
        num = 0
        stat = [0 for i in range(1440)]
        ret = [[] for i in range(1440)]
        for type in t[date]:
            for i in range(0, len(t[date][type])):
                a = t[date][type][i]
                match = re.findall(r'(.*)\((.*)-(.*)\)',
                                   a['station_train_code'], re.I | re.M)[0]
                if (match[0] in a['train_no']) == False:
                    # print(match[0] +' '+ a['train_no']); #切换上下行
                    continue
                schdata = processA(t[date][type][i], date, station)
                s = schToCsv(schdata)
                num += len(s)
                for row in s:
                    #time_list.append(row)
                    if len(row) >= 6:
                        minute = getmin(row[4])
                        #stat[minute] += 1
                        ret[minute].append(row)
                    #tele = telecode(row[1]);
                    # if True or tele and tele[2] == 'P':
                    #num = num+1;
                    #stat[minute] = stat[minute]+1;
        print(num)
        #sort = sorted(time_list, cmpbyTime)
        sort = []
        for key in range(len(ret)):
            stat[key] = len(ret[key])
            for row in ret[key]:
                sort.append(row)
        print(print_stat(stat))

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
            '''buffer += (s[0]['station_train_code'].encode('utf-8') + ',' + s[i]['station_name'].encode('utf-8') + ',' + s[i]['station_no'].encode('utf-8')
                       + ',' + str(day) + ',' + s[i]['arrive_time'].encode('utf-8') + ',' + '0'+'\n')'''
            ret.append([
                s[0]['station_train_code'].encode('utf-8'), s[i]['station_name'].encode('utf-8'), s[i]['station_no'].encode('utf-8'),
                str(day), s[i]['arrive_time'].encode('utf-8'), '0'
            ])

        if getmin(s[i]['start_time'].encode('utf-8')) > -1 and i < len(s)-1:
            minute = getmin(s[i]['start_time'].encode('utf-8'))
            if minute < last:
                day += 1
            last = minute
            #print(s[0]['station_train_code'].encode('utf-8') + ',' + s[i]['station_name'].encode('utf-8') + ',' + s[i]['start_time'].encode('utf-8') + ',' + '1');
            #print(s[0]['station_train_code'].encode('utf-8') + ',' + s[i]['station_name'].encode('utf-8') + ',' + s[i]['station_no'].encode('utf-8') + ',' + str(day) + ',' + s[i]['start_time'].encode('utf-8') + ',' + '1');
            '''buffer += (s[0]['station_train_code'].encode('utf-8') + ',' + s[i]['station_name'].encode('utf-8') + ',' + s[i]['station_no'].encode('utf-8')
                       + ',' + str(day) + ',' + s[i]['start_time'].encode('utf-8') + ',' + '1'+'\n')'''
            ret.append([
                s[0]['station_train_code'].encode('utf-8'), s[i]['station_name'].encode('utf-8'), s[i]['station_no'].encode('utf-8'),
                str(day), s[i]['start_time'].encode('utf-8'), '1'
            ])
    # return buffer
    return ret

def readcsv(fn):
    with open(fn, 'r') as f:  # py2
        if f.read(3)!='\xef\xbb\xbf':
            f.seek(0,0)
        data = f.read()
    c = data.split('\n')
    for i in range(len(c)):
        c[i] = c[i].split(' ')
    return c

def openMilage(fn):
    with open(fn, 'r') as f:  # py2
        if f.read(3)!='\xef\xbb\xbf':
            f.seek(0,0)
        data = f.read()
    m = data.split('\n')
    for i in range(len(m)):
        m[i] = m[i].split(' ')
    return m

def getkm(s, m):
    for i in range(len(m)):
        if len(m[i]) > 1 and s == m[i][0]:
            return m[i][1]
    return -1

#(1440-x0)/x1=(y-y0)(y1-y) = k
#(y-y0)=(y1-y)*(1440-x0)/x1
#(y-y0)=(y1-y)*k  
#y=y0+y1*k-y*k
#(1+k)y=y0+y1*k
#y=(y0+y1*k)/(1+k)
#k:
#y=y0/(1+k)+y1*(1+k-1)/(1+k)
#y=y0/(1+k)+y1-y1/(1+k)
#y=(y0-y1)/(1+k)+y1
#(lasty-y)/(1+(1440-lastx)/x)+y
#(lasty-y)*x/((1440+x-lastx))+y
#1/k:
#y=y0(1+k-k)/(1+k)+y1*k/(1+k)
#y=y0-y0*k/(1+k)+y1*k/(1+k)
#y=y0+(y1-y0)*k/(1+k)
#y=y0+(y1-y0)*(1/(1/k))/((1/k)/(1/k)+(1/(1/k)))
#y=y0+(y1-y0)*1/((1/k)+1)
#lasty+(lasty-y)/(1+x/(1440-lastx))

def schToPolyline(s, m):
    if (len(s)) <= 0:
        return ''
    buffer = ''
    day = 0
    lastx = 0
    lasty = 0
    buffer += '<polyline name="%s" class="G" style="fill:none;stroke:blue;stroke-width:1;opacity:0.8" points="' % (s[0]['station_train_code'].encode('utf-8'))
    for i in range(0, len(s)):
        x = getmin(s[i]['arrive_time'].encode('utf-8'))
        y = getkm(s[i]['station_name'].encode('utf-8'), m)
        if getmin(s[i]['arrive_time'].encode('utf-8')) > -1 and i > 0:
            if x < lastx:
                day += 1
                #1440, (lasty-y)*x/((1440+x-lastx))+y
                buffer += '%d,%d "/>\n<polyline name="%s+%d" class="G" style="fill:none;stroke:blue;stroke-width:1;opacity:0.8" points="%d,%d' \
                    % (1440, (int(lasty)-int(y))*int(x)/((1440+int(x)-int(lastx)))+int(y), s[0]['station_train_code'].encode('utf-8'), day,\
                    1440, (int(lasty)-int(y))*int(x)/((1440+int(x)-int(lastx)))+int(y) )
            lastx = x
            lasty = y
        buffer += '%s,%s ' % (x, y)
        
        x = getmin(s[i]['start_time'].encode('utf-8'))
        y = getkm(s[i]['station_name'].encode('utf-8'), m)
        if getmin(s[i]['start_time'].encode('utf-8')) > -1 and i < len(s)-1:
            if x < lastx:
                day += 1
                buffer += '%d,%d "/>\n<polyline name="%s+%d" class="G" style="fill:none;stroke:blue;stroke-width:1;opacity:0.8" points="%d,%d' \
                    % (1440, (int(lasty)-int(y))*int(x)/((1440+int(x)-int(lastx)))+int(y), s[0]['station_train_code'].encode('utf-8'), day,\
                    1440, (int(lasty)-int(y))*int(x)/((1440+int(x)-int(lastx)))+int(y) )
            lastx = x
            lasty = y
        buffer += '%s,%s ' % (x, y)
    buffer += '"/>\n'
    return buffer


def train_list_type_str(t):
    s = ''
    for date in sorted(t.keys()):
        s += (date.encode('utf-8'))
        for type in t[date]:
            s += ('\t' + type.encode('utf-8') + ' ' + str(len(t[date][type])))
        s += '\n'
    return s


def hash_no(s):
    items = [('Z', 10000), ('T', 20000), ('K', 30000),
             ('G', 40000), ('D', 50000), ('C', 60000),
             ('Y', 00000), ('S', 60000), ('P', 00000)]  # ('Y',70000),('S',71000),('P',80000)
    d = dict(items)
    type = d[s[0]] if s[0] in d else 0
    n = int(re.sub(r'\D+', '', s))
    return type + n


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


if __name__ == '__main__':
    try:
        fn0 = sys.argv[1]
    except:
        fn0 = os.path.join(os.path.dirname(
            os.path.abspath(__file__)), 'train_list.js')
    try:
        fn1 = sys.argv[2]
    except:
        fn1 = os.path.join(os.path.dirname(
            os.path.abspath(__file__)), 'station_name.js')
    print('input train_list file:   ' + fn0)
    print('input station_name file: ' + fn1)

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
        savecsv(t,station)
        if platform.system() == "Windows":
            os.system('pause')
    except Exception, e:
        print(str(Exception))
        if platform.system() == "Windows":
            os.system('pause')


'''
from view_train_list import *

t = openTrainList('train_list.js')
station = getStation('station_name.js')
savecsv(t,station)
m = openMilage('test/京广高速线里程.txt')
'''
