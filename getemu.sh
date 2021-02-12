#!/bin/bash 

path="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )/"

${path}equip.py
${path}ccrgt.py
${path}emu_equip_ccrgt.py

