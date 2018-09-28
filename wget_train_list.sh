#!/bin/bash 

path="/var/ftp/"

t0='0'
if [ -f "${path}js/train_list.js" ];then
t0=`stat -c %Y ${path}js/train_list.js`
else
t0='0'
fi
#echo ${t0}

#download only new file
/usr/bin/wget -N --no-check-certificate https://kyfw.12306.cn/otn/resources/js/query/train_list.js -P ${path}js/
#/usr/bin/wget -N --no-check-certificate https://kyfw.12306.cn/otn/resources/js/query/train_list.js -P ${path}js/ && ${path}js/view_train_list.py ${path}js/train_list.js

#always teain_list_yymmdd.js
#date=`date -d today +"%y%m%d"`
#echo ${date}
#/usr/bin/wget --no-check-certificate https://kyfw.12306.cn/otn/resources/js/query/train_list.js -O ${path}js/train_list_${date}.js && ${path}js/view_train_list.py ${path}js/train_list_${date}.js

#always train_list.js
#/usr/bin/wget --no-check-certificate https://kyfw.12306.cn/otn/resources/js/query/train_list.js -O ${path}js/train_list.js && ${path}js/view_train_list.py ${path}js/train_list.js

t1='0'
if [ -f "${path}js/train_list.js" ];then
t1=`stat -c %Y ${path}js/train_list.js`
else
t1='0'
fi
#echo ${t1}

#echo $((${t1}-${t0}))
if ((${t1} > ${t0}));then
echo t1 newer
${path}view_train_list.py ${path}js/train_list.js
yymmdd=`date +"%y%m%d" -d "$(stat -c %y ${path}js/train_list.js)"`
cp -p ${path}js/train_list.js ${path}js/train_list_${yymmdd}.js
gzip -c9 ${path}js/train_list.js > ${path}js/train_list.js.gz
else
echo t0 newer or same
fi
