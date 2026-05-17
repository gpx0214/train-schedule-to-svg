#!/usr/bin/python
# -*- coding: utf-8 -*-

from view_train_list import *
import re
import os
import sys


try:
    date = sys.argv[1]
except:
    date = nowdate()

try:
    if sys.argv[2] == "cache":
        cache=2
    if sys.argv[2] == "cache0":
        cache=0
except:
    cache=1

yyyymmdd = date_yyyymmdd(date)
path = 'carcode%s' % (yyyymmdd[2:-2])
touchdir(path)


name = 'js/train%s.csv'%(base_yymmdd())
ret = carcodecsv(name, date, cache)


name = 'emu/carcode%s.csv' % (yyyymmdd)
try:
    fn1 = os.path.join(os.path.dirname(os.path.abspath(__file__)), name)
except:
    fn1 = name

writecsv(fn1, ret)
