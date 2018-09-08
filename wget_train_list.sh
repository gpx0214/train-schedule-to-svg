#!/bin/bash 

date=`date -d today +"%y%m%d"`
echo ${date}
/usr/bin/wget --no-check-certificate https://kyfw.12306.cn/otn/resources/js/query/train_list.js -O /var/ftp/train_list_${date}.js && /var/ftp/view_train_list.py /var/ftp/train_list_${date}.js
#/usr/bin/wget --no-check-certificate -N https://kyfw.12306.cn/otn/resources/js/query/train_list.js -O /var/ftp/train_list.js && /var/ftp/view_train_list.py /var/ftp/train_list_${date}.js

