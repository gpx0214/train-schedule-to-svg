def getSchT(train_code, date):
    url = "http://61.161.203.55/mobile.myweixin.com/GetRsultInfo2?train_date=" + date.replace("-","") + "&train_code=" +  train_code;
    #header = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:59.0) Gecko/20100101 Firefox/59.0"}
    header = {"User-Agent":"Netscape 5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36"}
    try:
        resp = requests.get(url,headers=header);
    except requests.exceptions.ConnectionError:
        print('ConnectionError ' + train_code +'_T');
        return '';
    body = resp.content.decode('utf-8');   #bytes -> str (ucs2)
    try:
        sch = json.loads(body);
    except ValueError:
        print('ValueError ' + train_code +'_T');
        return '';
    if len(sch) :
        with open('sch/'+ train_code +'_T.json','wb') as f:
            if f.tell() == 0:
                f.write('\xef\xbb\xbf');
            f.write(resp.content)
        print(train_code +'_T' + ' ' + str(len(sch)));
        s = sch;
        day = 0;
        last = 0;
        buffer= '';
        time_list = [];
        for i in range(0, len(s)):
                print(s[i]['STNO'] + ',' + s[i]['SNAME'] + ',' + s[i]['ATIME'] + ',' + s[i]['STIME'])
                buffer += (s[i]['STNO'] + ',' + s[i]['SNAME'] + ',' + s[i]['ATIME'] + ',' + s[i]['STIME'])
                '''
                #print(s[0]['station_train_code'] + ',' + s[i]['station_name'] + ',' + s[i]['start_time'] + ',' + s[i]['arrive_time']);
                if getmin(s[i]['arrive_time']) > -1 and i > 0:
                    min = getmin(s[i]['arrive_time']);
                    tele = telecode(s[i]['station_name']);
                    if min < last:
                        day += 1;
                    last = min;
                    #print(s[0]['station_train_code'] + ',' + s[i]['station_name'] + ',' + s[i]['arrive_time'] + ',' + '0');
                    if True:
                        #print(s[0]['station_train_code'] + ',' + s[i]['station_name'] + ',' + s[i]['station_no'] + ',' + str(day) + ',' + s[i]['arrive_time'] + ',' + '0');
                        buffer+= (s[0]['station_train_code'] + ',' \
                        + s[i]['station_name'] + ',' \
                        + s[i]['station_no'] + ',' \
                        + str(day) + ',' \
                        + s[i]['arrive_time'] + ',' \
                        + '0'+'\n');
                        time_list.append([\
                        s[0]['station_train_code'], \
                        s[i]['station_name'], \
                        s[i]['station_no'], \
                        str(day), \
                        s[i]['arrive_time'], \
                        '0']);
                if getmin(s[i]['start_time']) > -1 and i < len(s)-1:
                    min = getmin(s[i]['start_time']);
                    tele = telecode(s[i]['station_name']);
                    if min < last:
                        day += 1;
                    last = min;
                    #print(s[0]['station_train_code'] + ',' + s[i]['station_name'] + ',' + s[i]['start_time'] + ',' + '1');
                    if True:
                        #print(s[0]['station_train_code'] + ',' + s[i]['station_name'] + ',' + s[i]['station_no'] + ',' + str(day) + ',' + s[i]['start_time'] + ',' + '1');
                        buffer+= (s[0]['station_train_code'] + ',' + s[i]['station_name'] + ',' + s[i]['station_no'] + ',' + str(day) + ',' + s[i]['start_time'] + ',' + '1'+'\n');
                        time_list.append([s[0]['station_train_code'], s[i]['station_name'], s[i]['station_no'], str(day), s[i]['start_time'], '1']);
        return buffer;
                '''
    else:
        print ("data error " + train_code +'_T');
        return '';
