#!/bin/bash 

path="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )/"

${path}carcode.py>>${path}log/log_carcode.txt
wait
${path}emu.py>>${path}log/log_getemu.txt
