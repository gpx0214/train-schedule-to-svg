#!/usr/bin/python  
# -*- coding: utf-8 -*-
#python3.5.3 win10 64bit MSC v.1900 64 bit (AMD64)
#from __future__ import print_function
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

# TODO

def getmin(str):
    try:
        a,b=str.split(':')[0:2]
        return int(a)*60+int(b);
    except:
        return -1;


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

    match = re.findall(r'(.*)\((.*)-(.*)\)',a['station_train_code'], re.I | re.M)[0]
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
        "User-Agent": "Netscape 5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36"}
    try:
        resp = requests.get(url, headers=header, timeout = 20)
    except:
        print('Error ' + train_no)
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



LeftTicketUrl = "leftTicket/query";

def getLeftTicket(t1,t2,date):
    url = "https://kyfw.12306.cn/otn/" + LeftTicketUrl + "?leftTicketDTO.train_date=" + date + "&leftTicketDTO.from_station=" + t1 + "&leftTicketDTO.to_station=" + t2 + "&purpose_codes=ADULT";
    #header = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:59.0) Gecko/20100101 Firefox/59.0"}
    header = {"User-Agent":"Netscape 5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36"}
    try:
        resp = requests.get(url,headers=header);
    except requests.exceptions.ConnectionError:
        print('ConnectionError '  + t1 +' '+ t2);
        return '';
    body = resp.content.decode('utf-8');   #bytes -> str (ucs2)
    try:
        ticket = json.loads(body);
    except ValueError:
        print('ValueError ' + t1 +' '+ t2);
        return '';
    if ticket['status'] == True and ticket['httpstatus'] == 200 and len(ticket['data']['result']) :
        with open('ticket/'+ date + '_' + t1 +'_'+ t2 +'.json','wb') as f:
            f.write(resp.content)
        print(t1 + ' ' + t2  +' '+ str(len(ticket['data']['result'])));
        for i in ticket['data']['result']:
            sp = i.split('|');
            if len(sp)>36:
                print(sp[3] +' '+ sp[2]+' '+ sp[4]+' '+ sp[5]);
                if not os.path.exists('sch/'+sp[2].encode('utf-8')+'.json'):
                    s = getSch12306(sp[4], sp[5], sp[2], date);
                    #with open("20180808.csv","a") as f:
                        #f.write(b);
        return t1 +' '+ t2;
    else:
        print ("data error " + t1 +' '+ t2);
        return '';

for date in ['2018-08-09','2018-08-10','2018-08-11','2018-08-12','2018-08-13','2018-08-14','2018-08-15']:
  print(date);
  getLeftTicket('BJP','TJP',date);
  getLeftTicket('TJP','BJP',date);
  getLeftTicket('TJP','YKP',date);
  getLeftTicket('YKP','TJP',date);

getSch12306('BJP','TJP','280000260415','2018-08-08');
getLeftTicket('YKP','TXP','2018-08-08');

for date in ['2018-11-20','2018-11-21','2018-11-22','2018-11-23','2018-11-24','2018-11-25','2018-11-26','2018-11-27']:
  print(date);
  getLeftTicket('BJP','SYT',date);
  getLeftTicket('SYT','BJP',date);


# https://kyfw.12306.cn/otn/leftTicket/query?leftTicketDTO.train_date=2018-08-11&leftTicketDTO.from_station=BJP&leftTicketDTO.to_station=TJP&purpose_codes=ADULT

buffer = '';
time_list = [];
num = 0;
stat = [0 for i in range(1440)];


with open('/var/ftp/delay/sort2018-07-27.csv','r') as f:
    if f.read(3)!='\xef\xbb\xbf':
        f.seek(0,0);
    data = f.read();

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