#!/bin/bash 

path="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )/"

${path}view_train_list.py
gzip -c9 ${path}js/train.csv > ${path}js/train.csv.gz
gzip -c9 ${path}js/time.csv > ${path}js/time.csv.gz
