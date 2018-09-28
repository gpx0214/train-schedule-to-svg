#!/bin/bash 

path="/var/ftp/"

t0='0'
if [ -f "${path}js/station_name.js" ];then
t0=`stat -c %Y ${path}js/station_name.js`
else
t0='0'
fi
#echo ${t0}

#download only new file
/usr/bin/wget -N --no-check-certificate https://kyfw.12306.cn/otn/resources/js/framework/station_name.js -P ${path}js/

t1='0'
if [ -f "${path}js/station_name.js" ];then
t1=`stat -c %Y ${path}js/station_name.js`
else
t1='0'
fi
#echo ${t1}

#echo $((${t1}-${t0}))
if ((${t1} > ${t0}));then
echo t1 newer
yymmdd=`date +"%y%m%d" -d "$(stat -c %y ${path}js/station_name.js)"`
cp -p ${path}js/station_name.js ${path}js/station_name_${yymmdd}.js
gzip -c9 ${path}js/station_name.js > ${path}js/station_name.js.gz
else
echo t0 newer or same
fi


t0='0'
if [ -f "${path}js/qss.js" ];then
t0=`stat -c %Y ${path}js/qss.js`
else
t0='0'
fi
#echo ${t0}

#download only new file
/usr/bin/wget -N --no-check-certificate https://kyfw.12306.cn/otn/resources/js/query/qss.js -P ${path}js/

t1='0'
if [ -f "${path}js/qss.js" ];then
t1=`stat -c %Y ${path}js/qss.js`
else
t1='0'
fi
#echo ${t1}

#echo $((${t1}-${t0}))
if ((${t1} > ${t0}));then
echo t1 newer
yymmdd=`date +"%y%m%d" -d "$(stat -c %y ${path}js/qss.js)"`
cp -p ${path}js/qss.js ${path}js/qss_${yymmdd}.js
else
echo t0 newer or same
fi
