import os
import glob
from view_train_list import *
import copy


buffer = ""
lastmap = ["" for i in range(26*26*26)]
fns = sorted(glob.glob(r'js/station_name_*.js'))
for fi in range(len(fns)):
    curmap = ["" for i in range(26*26*26)]
    fn = fns[fi]
    t1 = os.path.getmtime(fn)
    #print('%d %s'%(t1,fn))
    station = getStation(fn)
    fdate = re.sub(r'js[/\\]station_name_(\d+).js', r'\1', fn)
    for row in station:
        curmap[hash_tele(row[2])] = row[1]
    if fi == 0:
        for i in range(26*26*26):
            if curmap[i]:
                buffer += ('%3s:%s\n' % (unhash_tele(i), curmap[i]))
        lastmap = copy.deepcopy(curmap)
        continue
    for i in range(26*26*26):
        if curmap[i] and not lastmap[i]:
            buffer += ('%s + %3s:%s\n' % (fdate, unhash_tele(i), curmap[i]))
        if (not curmap[i]) and lastmap[i]:
            buffer += ('%s - %3s:%s\n' % (fdate, unhash_tele(i), lastmap[i]))
        if curmap[i] and lastmap[i] and curmap[i] != lastmap[i]:
            buffer += ('%s   %3s:%s->%s\n' %
                       (fdate, unhash_tele(i), lastmap[i], curmap[i]))
    lastmap = copy.deepcopy(curmap)

with open('station_change.txt', 'wb') as f:
    if f.tell() == 0:
        f.write('\xef\xbb\xbf')
    f.write(buffer.encode('utf-8'))
