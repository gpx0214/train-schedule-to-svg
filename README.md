# train-schedule-to-svg
12306sch.py old version read schedule and stations in *.txt files, output a svg graph.

##sch.txt will like follow,and a blank line are needed between two table.
<pre>
G65
01 北京西 ---- 10:33 ---- 
02 保定东 11:14 11:16 2分钟 
03 定州东 11:34 11:36 2分钟 
04 石家庄 11:59 12:02 3分钟 
05 邢台东 12:30 12:36 6分钟 
06 安阳东 13:04 13:06 2分钟 
07 郑州东 13:48 13:51 3分钟 
08 许昌东 14:13 14:15 2分钟 
09 信阳东 15:04 15:08 4分钟 
10 武汉 15:52 15:55 3分钟 
11 咸宁北 16:19 16:21 2分钟 
12 岳阳东 16:51 16:53 2分钟 
13 长沙南 17:27 17:31 4分钟 
14 衡山西 18:00 18:02 2分钟 
15 郴州西 18:44 18:46 2分钟 
16 清远 19:44 19:46 2分钟 
17 广州南 20:16 20:16 ---- 

</pre>
##station.txt will like follow,and each line have a station name and a millage.
<pre>
北京西 0
涿州东 62
高碑店东 83
保定东 139
定州东 201
正定机场 244
石家庄 281
高邑西 332
邢台东 403
邯郸东 456
安阳东 516
鹤壁东 562
新乡东 626
郑州东 693
许昌东 784
漯河西 848
驻马店西 912
信阳东 1030
孝感北 1103
武汉 1229
咸宁北 1314
赤壁北 1357
岳阳东 1444
长沙南 1591
株洲西 1643
衡山西 1727
衡阳东 1768
郴州西 1921
耒阳西 1823
韶关 2071
清远 2215
广州南 2298
虎门 2348
深圳北 2400
福田 2409
香港西九龙 2439
</pre>
