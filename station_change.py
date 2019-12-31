import os
import glob
from view_train_list import *
import copy


def hash_tele(s):
    if len(s) < 3:
        return 0
    return (ord(s[2])-65) * 26 * 26 + (ord(s[0])-65) * 26 + (ord(s[1])-65)


def unhash_tele(n):
    return chr(n/26 % 26+65) + chr(n % 26+65) + chr(n/26/26+65)


buffer = ""
lastmap = ["" for i in range(26*26*26)]
map = ["" for i in range(26*26*26)]
fns = sorted(glob.glob(r'js/station_name_*.js'))
for fi in range(len(fns)):
    fn = fns[fi]
    t1 = os.path.getmtime(fn)
    #print('%d %s'%(t1,fn))
    station = getStation(fn)
    fdate = re.sub(r'js[/\\]station_name_(\d+).js', r'\1', fn)
    for row in station:
        map[hash_tele(row[2])] = row[1]
    if fi == 0:
        for i in range(26*26*26):
            if map[i]:
                buffer += ('%3s:%s\n' % (unhash_tele(i), map[i]))
        lastmap = copy.deepcopy(map)
        continue
    for i in range(26*26*26):
        if map[i] and not lastmap[i]:
            buffer += ('%s + %3s:%s\n' % (fdate, unhash_tele(i), map[i]))
        if not map[i] and lastmap[i]:
            buffer += ('%s - %3s:%s\n' % (fdate, unhash_tele(i), lastmap[i]))
        if map[i] and lastmap[i] and map[i] != lastmap[i]:
            buffer += ('%s   %3s:%s->%s\n' %
                       (fdate, unhash_tele(i), lastmap[i], map[i]))
    lastmap = copy.deepcopy(map)

with open('station_change.txt', 'wb') as f:
    if f.tell() == 0:
        f.write('\xef\xbb\xbf')
    f.write(buffer.encode('utf-8'))
