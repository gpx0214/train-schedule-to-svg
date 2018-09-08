#!/bin/bash 

#date=`date -d today +"%y%m%d"`
#echo ${date}

t0=''
if [ -f "/var/ftp/train_list.js" ];then
t0=`stat -c %Y /var/ftp/train_list.js`
else
t0=''
fi
echo ${t0}

#/usr/bin/wget -N --no-check-certificate https://kyfw.12306.cn/otn/resources/js/query/train_list.js && /var/ftp/view_train_list.py /var/ftp/train_list.js
#/usr/bin/wget --no-check-certificate https://kyfw.12306.cn/otn/resources/js/query/train_list.js -O /var/ftp/train_list_${date}.js && /var/ftp/view_train_list.py /var/ftp/train_list_${date}.js
/usr/bin/wget --no-check-certificate https://kyfw.12306.cn/otn/resources/js/query/train_list.js -O /var/ftp/train_list.js && /var/ftp/view_train_list.py /var/ftp/train_list.js

t1=''
if [ -f "/var/ftp/train_list.js" ];then
t1=`stat -c %Y /var/ftp/train_list.js`
else
t1=''
fi
echo ${t1}

echo $((${t1}-${t0}))
if ((${t1} > ${t0}));then
echo t1 newer
yymmdd=`date +"%y%m%d" -d "$(stat -c %y /var/ftp/train_list.js)"`
cp -p /var/ftp/train_list.js /var/ftp/train_list_${yymmdd}.js
else
echo t0 newer
fi
