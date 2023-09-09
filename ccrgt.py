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
        print("set cache = 2")
        cache=2
except:
    cache=1


yyyymmdd = re.sub(
    r'(\d\d)(\d\d)-(\d+)-(\d+)',
    r"\1\2\3\4",
    date
)

path = 'ccrgt%s' % (yyyymmdd[2:-2])
touchdir(path)


name = 'js/train%s.csv'%(base_yymmdd())
ret = ccrgtcsv(name, date, cache)

name = 'emu/ccrgt%s.csv' % (yyyymmdd)
try:
    fn1 = os.path.join(os.path.dirname(os.path.abspath(__file__)), name)
except:
    fn1 = name

writecsv(fn1, ret)

# awk -F '[,]' '{print $2","$6}' ccrgt.csv|sort|uniq>车型.csv
