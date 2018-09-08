#!/usr/bin/python
# -*- coding: utf-8 -*-
#from __future__ import print_function

# TODO 临时文件 train_list 和 station_name 需要抽模块

import os
import sys
import platform
import time
import math
import random
import re
import json
import csv
import requests


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
    # f = open(os.path.join(path, fn),'r',encoding = 'utf8'); #py3
    with open(os.path.join(path, fn), 'r') as f:  # py2
        str = f.read()
    a = re.findall(r'\'\@([^\']+)\'', str, re.I | re.M)[0]
    s = a.split('@')
    for i in range(len(s)):
        s[i] = s[i].split('|')
    s.append(["tsn", "唐山南", "TNP", "tangshannan", "tsn", "-1"])
    s.append(["gye", "古冶", "GYP", "guye", "gy", "-1"])
    s.append(["jlo", "九龙", "JLO", "jiulong", "jl", "-1"])
    s.append(["", "香港西九龙", "XJA", "xianggangxijiulong", "xgxjl", "-1"])
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
    # f = open(os.path.join(path, fn),'r',encoding= 'utf8') #py3
    with open(os.path.join(path, fn), 'r') as f:  # py2
        f.read(16)
        data = f.read()
    return json.loads(data)


def processA(a, date, station):
    match = re.findall(r'(.*)\((.*)-(.*)\)', a['station_train_code'], re.I | re.M)[0]
    t1 = telecode(match[1].encode('utf-8'), station)
    t2 = telecode(match[2].encode('utf-8'), station)
    if not t1:
        #print(match[1].encode('utf-8') + " telecode not found!");
        return ''
    if not t2:
        #print(match[2].encode('utf-8') + " telecode not found!");
        return ''
    url = "https://kyfw.12306.cn/otn/czxx/queryByTrainNo?train_no=" + \
        a['train_no'] + "&from_station_telecode=" + t1 + \
        "&to_station_telecode=" + t2 + "&depart_date=" + date
    #header = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:59.0) Gecko/20100101 Firefox/59.0"}
    header = {
        "User-Agent": "Netscape 5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.81 Safari/537.36"}
    try:
        resp = requests.get(url, headers=header)
    except requests.exceptions.ConnectionError:
        print('ConnectionError ' + match[0].encode('utf-8'))
        return ''
    body = resp.content.decode('utf-8')  # bytes -> str (ucs2)
    try:
        sch = json.loads(body)
    except ValueError:
        print('ValueError ' + match[0].encode('utf-8'))
        return ''
    if sch['status'] == True and sch['httpstatus'] == 200 and len(sch['data']['data']):
        with open(os.path.join(path, 'sch/'+a['train_no'].encode('utf-8')+'.json'), 'wb') as f:
            f.write(resp.content)
        print(match[0].encode('utf-8') + ' ' + str(len(sch['data']['data'])))
        return match[0].encode('utf-8')
    else:
        print ("data error " + match[0].encode('utf-8'))
        return ''


def downloadAllSch12306(t, station):
    for date in sorted(t.keys()):
        print(date)
        #date = '1970-01-01';
        for type in t[date]:
            for i in range(0, len(t[date][type])):
                a = t[date][type][i]
                if os.path.exists(os.path.join(path, \
                        'sch/' + a['train_no'].encode('utf-8')+'.json')):
                    f = open(os.path.join(path, \
                        'sch/' + a['train_no'].encode('utf-8')+'.json'), 'r')
                    data = f.read()
                    sch = json.loads(data)
                    if len(sch['data']['data']) == 0:
                        print(a['train_no'].encode('utf-8') + " zero")
                        processA(t[date][type][i], date, station)
                    # else:
                        #print(a['train_no'].encode('utf-8') + ' local');
                else:
                    r = processA(t[date][type][i], date, station)


def train_list_type_str(t):
    s = ''
    for date in sorted(t.keys()):
        s += (date.encode('utf-8'))
        for type in t[date]:
            s += ('\t' + type.encode('utf-8') + ' ' + str(len(t[date][type])))
        s += '\n'
    return s


def hash_no(s):
    items = [('Z', 10000), ('T', 20000), ('K', 30000), \
             ('G', 40000), ('D', 50000), ('C', 60000), \
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
    global path
    path = os.path.dirname(os.path.realpath(__file__))
    try:
        fn0 = sys.argv[1]
    except:
        fn0 = os.path.join(path, 'train_list.js')
    try:
        fn1 = sys.argv[2]
    except:
        fn1 = os.path.join(path, 'station_name.js')
    print('input train_list file:   ' + fn0)
    print('input station_name file: ' + fn1)

    try:
        t = openTrainList(fn0)
        arr = train_list_train_no_array(t, 70000)
        stat, train_num = train_list_stat_block(arr, 100, 70000)
        s, block = print_block(stat)
        print(str(train_num) + " trains")
        print(str(block) + " blocks")
        print(s)
        print(train_list_type_str(t))
        station = getStation(fn1)
        #downloadAllSch12306(t, station)
        if platform.system() == "Windows":
            os.system('pause')
    except Exception, e:
        print(str(Exception))
        if platform.system() == "Windows":
            os.system('pause')