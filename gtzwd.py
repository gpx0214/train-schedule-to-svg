#!/usr/bin/python
# -*- coding: utf-8 -*-

from view_train_list import *

print(gtzwdjsp())
date = nowdate()

for c in 'ztkgdcy':
    j = gtzwd(date, c)
    print(c)
    #print(j)
