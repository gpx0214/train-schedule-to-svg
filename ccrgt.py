#!/usr/bin/python
# -*- coding: utf-8 -*-

from view_train_list import *
import re
import os


date = nowdate()
ret = ccrgtcsv(date)

yyyymmdd = re.sub(
    r'(\d\d)(\d\d)-(\d+)-(\d+)',
    r"\1\2\3\4",
    date
)
name = 'emu/ccrgt%s.csv' % (yyyymmdd)
try:
    fn1 = os.path.join(os.path.dirname(os.path.abspath(__file__)), name)
except:
    fn1 = name

writecsv(fn1, ret)

# awk -F '[,]' '{print $2","$6}' ccrgt.csv|sort|uniq>车型.csv
