#!/bin/bash 

path="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )/"

${path}ccrgt.py>>${path}log/log_ccrgt.txt &
${path}equip.py>>${path}log/log_equip.txt &
wait
${path}emu_equip_ccrgt.py>>${path}log/log_getemu.txt
