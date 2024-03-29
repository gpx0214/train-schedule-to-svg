#!/bin/bash 

path="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )/"

t0='0'
if [ -f "${path}js/saletime.json" ];then
t0=`md5sum ${path}js/saletime.json|awk '{print $1}'`
else
t0='0'
fi
echo ${t0}

#download only new file
/usr/bin/wget -N -nv -S --no-check-certificate https://kyfw.12306.cn/index/otn/index12306/queryAllCacheSaleTime -O ${path}js/saletime.json

t1='0'
if [ -f "${path}js/saletime.json" ];then
t1=`md5sum ${path}js/saletime.json|awk '{print $1}'`
else
t1='0'
fi
echo ${t1}

if [ "$t0" != "$t1" ];then
echo t1 newer
yymmdd=`date +"%y%m%d" -d "$(stat -c %y ${path}js/saletime.json)"`
cp -p ${path}js/saletime.json ${path}js/saletime${yymmdd}.json
#gzip -c9 ${path}js/saletime.json > ${path}js/saletime.json.gz
rm -f ${path}js/saletime.json.gz
7za a -tgzip -mx9 ${path}js/saletime.json.gz ${path}js/saletime.json >/dev/null
else
echo t0 newer or same
fi


t0='0'
if [ -f "${path}js/station_name.js" ];then
t0=`stat -c %Y ${path}js/station_name.js`
else
t0='0'
fi
#echo ${t0}

#download only new file
#/usr/bin/wget -N -nv -S --no-check-certificate https://www.12306.cn/index/script/core/common/station_name.js -P ${path}js/
/usr/bin/wget -N -nv -S --no-check-certificate https://kyfw.12306.cn/otn/resources/js/framework/station_name.js -P ${path}js/

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
#gzip -c9 ${path}js/station_name.js > ${path}js/station_name.js.gz
rm -f ${path}js/station_name.js.gz
7za a -tgzip -mx9 ${path}js/station_name.js.gz ${path}js/station_name.js >/dev/null
${path}view_train_list.py station
#gzip -c9 ${path}js/station.csv > ${path}js/station.csv.gz
#gzip -c9 ${path}js/station.min.csv > ${path}js/station.min.csv.gz
rm -f ${path}js/station.csv.gz
7za a -tgzip -mx9 ${path}js/station.csv.gz ${path}js/station.csv >/dev/null
rm -f ${path}js/station.min.csv.gz
7za a -tgzip -mx9 ${path}js/station.min.csv.gz ${path}js/station.min.csv >/dev/null
${path}github_auto_update.py js/station.csv js/station.min.csv
${path}micromsg.py update station `date +"%y%m%d %H:%M:%S" -d@${t1}`
rm -f ${path}js.7z
7za a -t7z ${path}js.7z ${path}js/ -xr\!*.gz
${path}micromsg.py js.7z finish `date +"%y%m%d %H:%M:%S" -d "$(stat -c %y ${path}js.7z)"`
${path}station_change.py
else
echo t0 newer or same
fi
