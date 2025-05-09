#!/bin/bash 

path="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )/"

basedate="$(${path}view_train_list.py basedate)"

#gzip -c9 ${path}js/train${basedate}.csv > ${path}js/train${basedate}.csv.gz
#gzip -c9 ${path}js/time${basedate}.csv > ${path}js/time${basedate}.csv.gz
#gzip -c9 ${path}js/time${basedate}.min.csv > ${path}js/time${basedate}.min.csv.gz
#gzip -c9 ${path}js/cr${basedate}.min.csv > ${path}js/cr${basedate}.min.csv.gz

rm -f ${path}js/train${basedate}.csv.gz
7za a -tgzip -mx9 ${path}js/train${basedate}.csv.gz ${path}js/train${basedate}.csv >/dev/null
rm -f ${path}js/time${basedate}.csv.gz
7za a -tgzip -mx9 ${path}js/time${basedate}.csv.gz ${path}js/time${basedate}.csv >/dev/null
rm -f ${path}js/cr${basedate}.min.csv.gz
7za a -tgzip -mx9 ${path}js/cr${basedate}.min.csv.gz ${path}js/cr${basedate}.min.csv >/dev/null
