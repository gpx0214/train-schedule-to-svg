#!/bin/bash 

path="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )/"

${path}view_train_list.py
#gzip -c9 ${path}js/train.csv > ${path}js/train.csv.gz
#gzip -c9 ${path}js/time.csv > ${path}js/time.csv.gz
#gzip -c9 ${path}js/time.min.csv > ${path}js/time.min.csv.gz

rm -f ${path}js/train.csv.gz
7za a -tgzip -mx9 ${path}js/train.csv.gz ${path}js/train.csv >/dev/null
rm -f ${path}js/time.csv.gz
7za a -tgzip -mx9 ${path}js/time.csv.gz ${path}js/time.csv >/dev/null
rm -f ${path}js/time.min.csv.gz
7za a -tgzip -mx9 ${path}js/time.min.csv.gz ${path}js/time.min.csv >/dev/null

${path}getemu.sh
