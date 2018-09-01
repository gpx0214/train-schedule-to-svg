#!/usr/bin/python  
# -*- coding: utf-8 -*-
#from __future__ import print_function

#TODO 临时文件 train_list 和 station_name 需要抽模块

import requests #
import re
import json
import math
import random
import time
import os     #for cls
import sys
import csv

def cmpbyTime(a1, a2):
    if (len(a1)<5):
        return 0;
    if (len(a2)<5):
        return 0;
    t1 = getmin(a1[4]);
    t2 = getmin(a2[4]);
    if t1 > t2:
        return 1;
    if t1 < t2:
        return -1;
    return 0;

def getmin(str):
    try:
        a,b=str.split(':')[0:2]
        return int(a)*60+int(b);
    except:
        return -1;

def getStation(fn):
    #f = open(fn,'r',encoding = 'utf8'); #py3
    with open(fn,'r') as f: #py2
        str=f.read();
    a=re.findall(r'\'\@([^\']+)\'', str , re.I|re.M)[0];
    s = a.split('@');
    for i in range(len(s)):
        s[i] = s[i].split('|');
    s.append(["tsn", "唐山南", "TNP", "tangshannan", "tsn", "-1"]);
    s.append(["gye", "古冶", "GYP", "guye", "gy", "-1"]);
    s.append(["jlo", "九龙", "JLO", "jiulong", "jl", "-1"]);
    s.append(['jsw', '金山卫', 'BGH', 'jinshanwei', 'jsw', '-1']);
    s.append(['mji', '梅江', 'MKQ', 'meijiang', 'mj', '-1']);
    s.append(['ylo', '元龙', 'YLY', 'yuanlong', 'yl', '-1']);
    s.append(['bdl', '八达岭', 'ILP', 'badaling', 'bdl', '-1']);
    s.append(['nsb', '南山北', 'NBQ', 'nanshanbei', 'nsb', '-1']);
    s.append(['', '车墩', 'CDH', 'chedun', 'cd', '-1']);
    s.append(['', '羊木', 'YMJ', 'yangmu', 'ym', '-1']);
    return s;

def telecode(str):
    for i in range(len(station)):
        if str ==  station[i][1]:
            return station[i][2];
    #print(str)
    return '';

def openTrainList(fn):
    #f = open(fn,'r',encoding= 'utf8') #py3
    with open(fn,'r') as f: #py2
        f.read(16);
        data = f.read();
    return json.loads(data);

def processA(a):
    match = re.findall(r'(.*)\((.*)-(.*)\)', a['station_train_code'] , re.I|re.M)[0];
    t1 = telecode(match[1].encode('utf-8'));
    t2 = telecode(match[2].encode('utf-8'));
    if not t1:
        #print(match[1].encode('utf-8') + " telecode not found!");
        return '';
    if not t2:
        #print(match[2].encode('utf-8') + " telecode not found!");
        return '';
    url = "https://kyfw.12306.cn/otn/czxx/queryByTrainNo?train_no="+ a['train_no'] +"&from_station_telecode="+ t1 +"&to_station_telecode="+ t2 +"&depart_date=" + date;
    #header = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:59.0) Gecko/20100101 Firefox/59.0"}
    header = {"User-Agent":"Netscape 5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36"}
    try:
        resp = requests.get(url,headers=header);
    except requests.exceptions.ConnectionError:
        print('ConnectionError ' + match[0].encode('utf-8'));
        return '';
    body = resp.content.decode('utf-8');   #bytes -> str (ucs2)
    try:
        sch = json.loads(body);
    except ValueError:
        print('ValueError ' + match[0].encode('utf-8'));
        return '';
    if sch['status'] == True and sch['httpstatus'] == 200 and len(sch['data']['data']) :
        with open('sch/'+a['train_no'].encode('utf-8')+'.json','wb') as f:
            f.write(resp.content)
        print(match[0].encode('utf-8') + ' ' + str(len(sch['data']['data'])));
        return match[0].encode('utf-8');
    else:
        print ("data error " + match[0].encode('utf-8'));
        return '';

def Tprint(t):
  s = '';
  for date in sorted(t.keys()):
    s += (date.encode('utf-8'));
    for type in t[date]:
      s += ('\t' + type.encode('utf-8') + ' ' + str(len(t[date][type])));
    s += '\n'
  return s;

if __name__ == '__main__':
    try:
        fn0 = sys.argv[1];
    except:
        fn0 = 'train_list.js';

    print('input file:' + fn0);
    try:
        t = openTrainList(fn0);
        print(Tprint(t))
        os.system('pause');
    except Exception, e:
        print(str(Exception))
        os.system('pause');
