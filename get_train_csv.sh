#!/bin/bash 

path="/home/ec2-user/"

${path}view_train_list.py
gzip -c9 ${path}js/train.csv > ${path}js/train.csv.gz
gzip -c9 ${path}js/time.csv > ${path}js/time.csv.gz
gzip -c9 ${path}js/station.csv > ${path}js/station.csv.gz
gzip -c9 ${path}js/station.min.csv > ${path}js/station.min.csv.gz
