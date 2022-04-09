#!/bin/bash 

path="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )/"

${path}view_train_list.py
${path}getcompress.sh &

${path}getemu.sh
wait
