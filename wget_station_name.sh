#!/bin/bash 

path="/var/ftp/"

t0=''
if [ -f "${path}station_name.js" ];then
t0=`stat -c %Y ${path}station_name.js`
else
t0=''
fi
#echo ${t0}

#download only new file
/usr/bin/wget -N --no-check-certificate https://kyfw.12306.cn/otn/resources/js/framework/station_name.js -P ${path}

t1=''
if [ -f "${path}station_name.js" ];then
t1=`stat -c %Y ${path}station_name.js`
else
t1=''
fi
#echo ${t1}

#echo $((${t1}-${t0}))
if ((${t1} > ${t0}));then
echo t1 newer
yymmdd=`date +"%y%m%d" -d "$(stat -c %y ${path}station_name.js)"`
cp -p ${path}station_name.js ${path}station_name_${yymmdd}.js
else
echo t0 newer or same
fi


t0=''
if [ -f "${path}qss.js" ];then
t0=`stat -c %Y ${path}qss.js`
else
t0=''
fi
#echo ${t0}

#download only new file
/usr/bin/wget -N --no-check-certificate https://kyfw.12306.cn/otn/resources/js/query/qss.js -P ${path}

t1=''
if [ -f "${path}qss.js" ];then
t1=`stat -c %Y ${path}qss.js`
else
t1=''
fi
#echo ${t1}

#echo $((${t1}-${t0}))
if ((${t1} > ${t0}));then
echo t1 newer
yymmdd=`date +"%y%m%d" -d "$(stat -c %y ${path}qss.js)"`
cp -p ${path}qss.js ${path}qss_${yymmdd}.js
else
echo t0 newer or same
fi
