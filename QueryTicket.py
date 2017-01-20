#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
"""
author='Mr RaoJL',
author_email='dasinenge@gmail.com',
description=' Train ticket inquiry Script'
aothor Date='Wed Jan 11 17:42:14 2017'
"""
import urllib2
import ssl
import json
import sys
import re
import time
import smtplib
# from City_code import City_Code
from email.mime.text import MIMEText
email_FROM_city=''
email_TO_city=''
email_DATE_city=''
DESC_title = """
 __  __        ____                 _ _
|  \/  |_ __  |  _ \ __ _  ___     | | |
| |\/| | '__| | |_) / _` |/ _ \ _  | | |
| |  | | |    |  _ < (_| | (_) | |_| | |___
|_|  |_|_|    |_| \_\__,_|\___/ \___/|_____|

"""
HELPR="""
 1 查询
 2 将查询的信息发送邮件
 Q 查询可用站点 用法: 1> Q [站点名] 2> Q ALL 列出全部(较长)
 F 监控余票 使用: F [出发地] [目的地] [日期,标准格式:xxxx-xx-xx] [座位类型,如:硬座] [列车编号,如:K935] [查询次数,默认为1次]
 exit 退出程序
"""
send_head = {
                "Host": "kyfw.12306.cn",
                "User-Agent": 'Mozilla / 5.0(X11;Fedora;Linux x86_64;rv:50.0) Gecko / 20100101Firefox / 50.0',
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                'Connection': 'keep-alive'
            }
City_Code = {}
reload(sys)
sys.setdefaultencoding('utf-8')
ssl._create_default_https_context = ssl._create_unverified_context
Faile = 0
#curl="leftTicket/queryZ"
def HTTP_query(trainDate, From_city, To_city):
    try:
        try:
            bagful = "https://kyfw.12306.cn/otn/leftTicket/queryZ?" \
                     "leftTicketDTO.train_date={0}&" \
                     "leftTicketDTO.from_station={1}&" \
                     "leftTicketDTO.to_station={2}" \
                     "&purpose_codes=ADULT" \
                     "".format(trainDate, City_Code[From_city], City_Code[To_city])
            req = urllib2.Request(bagful, headers=send_head)
        except KeyError:
            print "无法找到的站点"
            return False
        except NameError:
            print "无法找到输入的站点"
            return False

        global GET_INFO
        GET_INFO = urllib2.urlopen(req).read()
        #print urllib2.urlopen(req).read()
        return True
    except urllib2.HTTPError as alter:
        print "错误: [%s]!"% alter
        pass
def Get_City_code():
    print "读取站点数据库..."
    try:
        Ci_url = 'https://kyfw.12306.cn/otn/resources/js/framework/station_name.js?station_version=1.8994'
        Ci_text = urllib2.urlopen(Ci_url).read()
        Ci_text = Ci_text.replace('\'', '').replace('var station_names =\'', '')
        city = re.findall('\|\W+\|[A-Z]{3}', Ci_text)
        for i in city:
            City_Code[re.split('\|', i)[1]] = re.split('\|', i)[2]
        print "读取成功!\n输入h或help获取帮助"
    except urllib2.URLError as erron:
        print "错误:%s无法读取站点数据,请检查网络后重试!"%erron
        sys.exit()
def Get_Data(trainDate, From_city, To_city):
    global info
    json._default_encoder = 'UTF-8'
    try:
        data = json.loads(GET_INFO, encoding='UTF-8')
    except NameError:
        print "无法找到输入的站点"
        return False
    tables = []
    info = []
    try:
        for i in data['data']:
            tables.append(i)
        if True:
            for j in tables:
                info.append(j['queryLeftNewDTO'])

    except KeyError:
        print "\033[31m未查询到数据\033[0m"
        pass
        return Faile
    List_Data(From_city, To_city, trainDate)
def Filter_Data(From, To, Date, zw_type, tr_Num):
    HTTP_query(Date, From, To)
    F_info = []
    F_table = []
    json._default_encoder = 'uft-8'
    try:
        assert isinstance(GET_INFO, object)
        data = json.loads(GET_INFO, encoding='UTF-8')
    except NameError:
        print "无法找到输入的站点"
        return False
    try:
        for i in data['data']:
            F_table.append(i)
        if True:
            for j in F_table:
                F_info.append(j['queryLeftNewDTO'])

    except KeyError:
        print "\033[31m未查询到数据\033[0m"
    try:
        exchange_name(zw_type)
        for i in F_info:
            if i['station_train_code'] == tr_Num and (i[zw_type] == '有' or re.search('\d+', i[zw_type])):
                print '从{0}到{1},日期为{2},列车 {3} {4}:{7}{5}{8} 出发时间:{7}{6}{8} '.format(From, To, Date, i['station_train_code'], ZW_NAME, i[zw_type], i['start_time'], StartColor, EndColor)

    except KeyError:
        print "输入错误"
        return False

def exchange_name(self):
    global ZW_NAME
    ZW_NAME=''
    if self == 'yz_num':
        ZW_NAME = '硬座'
    if self == 'rw_num':
        ZW_NAME = '软我'
    if self == 'yw_num':
        ZW_NAME = '硬卧'
    if self == 'wz_num':
        ZW_NAME = '无座'
    else:
        print ""
        return False
def List_Data(From_city, To_city, trainDate):
    if True:
        seq = 0
        print "查询结果:"
        global StartColor
        global EndColor
        StartColor = '\033[32m'
        EndColor = '\033[0m'
        try:
            from prettytable import PrettyTable
            List_train = PrettyTable(['序列', '列车类型', '出发时间', '到达时间', '历时', '硬座', '硬卧', '软卧', '无座', '起始站','终点站','列车状态'])
            for z in info:
                seq += 1
                if re.search('K', z['station_train_code']):
                    liche_code = "快速 "
                elif re.search('G', z['station_train_code']):
                    liche_code = "高铁 "
                elif re.search('Z', z['station_train_code']):
                    liche_code = "直达 "
                elif re.search('T', z['station_train_code']):
                    liche_code = "特快 "
                elif re.search('D', z['station_train_code']):
                    liche_code = "动车组 "
                elif re.search('Y', z['station_train_code']):
                    liche_code = "旅行专列 "
                elif re.search('C', z['station_train_code']):
                    liche_code = "城际 "
                elif re.search('\d+', z['station_train_code']):
                    liche_code = '普通 '
                else:
                    liche_code = ""
                List_train.add_row(
                    [StartColor + str(seq) + EndColor, StartColor + liche_code + z['station_train_code'] + EndColor,
                     StartColor + z['start_time'] + EndColor,
                     StartColor + z['arrive_time'] + EndColor, StartColor + z['lishi'] + EndColor,
                     StartColor + z['yz_num'] + EndColor, StartColor + z['yw_num'] + EndColor,
                     StartColor + z['rw_num'] + EndColor, StartColor + z['wz_num'] + EndColor,
                     StartColor + z['start_station_name'] + EndColor, StartColor+z['end_station_name']+EndColor,
                     StartColor + z['controlled_train_message'] + EndColor])
            print List_train
            print "查询完成,从 {2} 到 {3},日期为{1}的列车,共{0}条记录.".format(len(info), trainDate, From_city, To_city, trainDate)
            return True
        except ImportError:
            for z in info:
                seq += 1
                if re.search('K', z['station_train_code']):
                    liche_code = "快速 "
                elif re.search('G', z['station_train_code']):
                    liche_code = "高铁 "
                elif re.search('Z', z['station_train_code']):
                    liche_code = "直达 "
                elif re.search('T', z['station_train_code']):
                    liche_code = "特快 "
                elif re.search('D', z['station_train_code']):
                    liche_code = "动车组 "
                elif re.search('Y', z['station_train_code']):
                    liche_code = "旅行专列 "
                elif re.search('C', z['station_train_code']):
                    liche_code = "城际 "
                elif re.search('\d+', z['station_train_code']):
                    liche_code = '普通 '
                else:
                    liche_code = ""
                print "-" * 140
                print "{5}\t{4}:\033[32m{0}\033[0m\t出发时间:\033[32m{1}\033[0m\t到达时间:\033[32m{2}\033[0m\t历时:\033[32m{3}\033[0m\t" \
                    .format(z['station_train_code'], z['start_time'], z['arrive_time'], z['lishi'], liche_code, seq),
                print '硬座:\033[32m{0}\033[0m\t硬卧:\033[32m{2}\033[0m\t软卧:\033[32m{3}\033[0m\t\033[0m无座:\033[32m{4}\033[0m\t列车状态:\033[32m{1}\033[0m' \
                    .format(z['yz_num'], z['controlled_train_message'], z['yw_num'], z['rw_num'], z['wz_num'])
            print "查询完成,从 {2} 到 {3},日期为{1}的列车,共{0}条记录.".format(len(info), trainDate, From_city, To_city, trainDate)


def Get_Input():
    """global From_city
    global To_city
    global trainDate
    """
    print "\033[32m-->>\033[0m进入12306查票控制台"
    From_city = raw_input("请输入出发城市(中文): ")
    To_city = raw_input("请输入目的城市(中文): ")
    trainDate = raw_input("请输入乘车日期(如:{0})默认即回车为今日: ".format(time.strftime('%Y-%m-%d')))
    if trainDate == '':
        trainDate = time.strftime('%Y-%m-%d')
        print "请稍等,正在查询从{0}到{1}日期:{2}的列车......".format(From_city, To_city, trainDate)
    else:
        CheckDate = re.search('[0-9]{4}.[0-9]{2}.[0-9]{2}', trainDate)
        if CheckDate:
            print "请稍等,正在查询从{0}到{1},日期:{2}的列车......".format(From_city, To_city, trainDate)
        else:
            print "日期格式错误!请重试!"
            return False
    email_DATE_city = trainDate
    email_FROM_city  = From_city
    email_TO_city = To_city
    HTTP_query(trainDate, From_city, To_city)
    Get_Data(trainDate, From_city, To_city)


def Check_Input():
    if True:
        print "12306查票脚本(收录全国{0}个站点,作者Mr RaoJL".format(City_Code.__len__())
        print DESC_title
        if True:
            while True:
                snedmail = raw_input("控制台 >>> ")
                if snedmail == '2':
                    print "发送邮件..."
                    Get_Msg(email_FROM_city, email_TO_city, email_DATE_city)
                    if True:
                        print "发送成功"
                        continue
                    else:
                        print "发送失败"
                        continue
                elif snedmail == '1':
                    Get_Input()
                    if False:
                        print "查询失败"
                        continue
                elif re.findall('Q \S+', snedmail):
                    search_wd = re.findall('Q \S+', snedmail)[0]
                    search_wd = search_wd.split(' ')[1]
                    for key in City_Code:
                        if search_wd in key:
                            print '\t' + key
                        elif search_wd == 'ALL':
                            print '\t' + key
                        else:
                            pass
                    if False:
                        print "无法找到你输入的站点"

                elif re.findall('F \S+', snedmail):
                    if len(snedmail.split(' ')) < 6:
                        print "请输入完整信息!"
                    else:
                        In_info = snedmail.split(' ')
                        s_city = In_info[1]
                        e_city = In_info[2]
                        s_date = In_info[3]
                        zw_type = ''
                        if In_info[4] == '硬座':
                            zw_type = 'yz_num'
                        elif In_info[4] == '硬卧':
                            zw_type = 'rw_num'
                        elif In_info[4] == '无座':
                            zw_type = 'wz_num'
                        elif In_info[4] == '软卧':
                            zw_type = 'rw_num'
                        else:
                            print "参数错误"
                            continue
                        train_num = In_info[5]
                        i=0
                        cish = 1
                        try:
                            if In_info.__len__() == 7 and re.search('\d+',In_info[6]):
                                cish = int(In_info[6])
                                try:
                                    while i < cish:
                                        i += 1
                                        print "第%s次查询" % i
                                        Filter_Data(s_city, e_city, s_date, zw_type, train_num)
                                except NameError:
                                    print "请先查询"
                                    continue
                            else:
                                Filter_Data(s_city, e_city, s_date, zw_type, train_num)
                        except IndexError as esa:
                            Filter_Data(s_city, e_city, s_date, zw_type, train_num)
                elif snedmail == '':
                    continue
                elif snedmail == 'h' or snedmail == 'help':
                   print HELPR
                elif snedmail == 'exit':
                    print "退出程序!"
                    break
                else:
                    print "输入 h 或者 help 获取帮助"
                    continue
    else:
        print ""
        sys.exit()


def Send_Mail(content):
    mail = smtplib.SMTP('smtp.sina.com.cn')
    mail_addr = '15173678774@sina.cn'
    mail_pass = 'rjl@1239015423'
    mail.login(mail_addr, mail_pass)
    To = mail_addr
    msg = MIMEText(content, _subtype='html', _charset='utf-8')
    msg['Subject'] = "12306 Inspection results TIME:{0}".format(time.ctime())
    msg['From'] = mail_addr
    msg['To'] = To
    mail.sendmail(mail_addr, To, msg.as_string())


def Get_Msg(From_city, To_city, trainDate):
    TdSty = "style='color:#fff;width:100px;text-align:center'"
    TdstyT = "style='text-align:center'"
    content = "<center><table><tr bgcolor='#333'><td {0}>列车类别</td><td {0}>出发时间</td>" \
              "<td {0}>到达时间</td>" \
              "<td {0}>历时</td>" \
              "<td {0}>硬座</td>" \
              "<td {0}>硬卧</td>" \
              "<td {0}>软卧</td>" \
              "<td {0}>无座</td>" \
              "<td {0}>列车状态</td></tr>".format(TdSty)
    seq = 0
    for i in info:
        seq += 1
        if re.search('K', i['station_train_code']):
            liche_code = "快速"
        elif re.search('G', i['station_train_code']):
            liche_code = "高铁"
        elif re.search('Z', i['station_train_code']):
            liche_code = "直达"
        elif re.search('T', i['station_train_code']):
            liche_code = "特快"
        elif re.search('D', i['station_train_code']):
            liche_code = "动车组"
        elif re.search('Y', i['station_train_code']):
            liche_code = "旅行专列"
        else:
            liche_code = "列车编号"
        content += \
            "<tr style='color:blue'><td>{0}</td>" \
            "<td {9}>{1}</td>" \
            "<td {9}>{2}</td>" \
            "<td {9}>{3}</td>" \
            "<td {9}>{4}</td>" \
            "<td {9}>{5}</td>" \
            "<td {9}>{6}</td>" \
            "<td {9}>{7}</td>" \
            "<td {9}>{8}</td></tr>" \
                .format(liche_code + i['station_train_code'], i['start_time'], i['arrive_time'], i['lishi'],
                        i['yz_num'], i['yw_num'], i['rw_num'], i['wz_num'], i['controlled_train_message'], TdstyT)
    content += "</table></center><h1 style='color:red'> {0} => {1} Time: {2}; Total: {3}; QueryTime: {4}".format(
        From_city, To_city, trainDate, seq, time.strftime('%F %H:%M:%S'))
    try:
        Send_Mail(content)
        return True
    except smtplib.SMTPAuthenticationError as e:
        print "验证失败", e
        return False


try:
    Get_City_code()
    Check_Input()
except KeyboardInterrupt:
    print "\n\033[31m程序终止,已退出!\033[0m"
