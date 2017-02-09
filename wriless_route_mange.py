#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
"""
    author='Mr RaoJL',
    author_email='dasinenge@gmail.com',
    description='TL-WR886N wireless route manger script(terminal)'

"""
import json
import requests
import time
import re
import sys
import urllib
import getpass
from prettytable import PrettyTable

help_text = """
    lan     查看局域网信息
    wan     查看广域网信息
    wriless 查看无线信息
    dhcpd   查看dhcp服务器信息
    host    查看在线主机
    log     查看日志,使用: log [页码],默认为1
    bind    查看IP与MAC绑定
    scan    扫描WIFI
    block   查看已禁用的设备
    rule    查看防火墙转发规则
    set     设置功能
    systeminfo  系统信息
    download    下载日志和配置文件,用法: download log(日志) download config(配置文件)
    delete  清除日志,用法: delete log
    relogin 重新登入
    reboot  重启路由器
    exit    退出
    quit    退出
"""
sys_Log = """
     _____ _       __        ______  ___   ___   __   _   _
    |_   _| |      \ \      / /  _ \( _ ) ( _ ) / /_ | \ | |
      | | | |   ____\ \ /\ / /| |_) / _ \ / _ \| '_ \|  \| |
      | | | |__|_____\ V  V / |  _ < (_) | (_) | (_) | |\  |
      |_| |_____|     \_/\_/  |_| \_\___/ \___/ \___/|_| \_|

"""
auth = """
     __  __        ____                 _ _
    |  \/  |_ __  |  _ \ __ _  ___     | | |
    | |\/| | '__| | |_) / _` |/ _ \ _  | | |
    | |  | | |    |  _ < (_| | (_) | |_| | |___
    |_|  |_|_|    |_| \_\__,_|\___/ \___/|_____|

"""
Set_clsss_help = """
    限速              Use:set limit Hostname Mac Limit_up Limit_down
    设置LAN网络         use:set net lan MODE IP_addr Netmask
    设置PPPOEmac地址      use : set mac auto|Mac_addr:xx:xx:xx:xx:xx
    设置WIFI密码        use: set key APname[guest|tp] passwd
    设置DHCP服务器       usag:set dhcp pool 0[enable:0;disable:1] [start_ip] [end_ip] [GW] [dns1] [dns2] [leases]
    PPPoe用户名密码        use:set pppoe MODE[default|manult] username password
    修改密码:           用法:set passwd 老密码 新密码
    设置局域网管理主机   use:set lan mange MODE[host|all] MAC_ADDR
    设置IP与MAC绑定      set ip bind Number[seq] IP MAC Hostname
    设置防火墙规则         use: set firewalld [num] [add|change|delete] src_port dest_port dest_IP
    禁用主机            use : set block METHOD[bloc|unblock] Mac Hostname
    开启或禁用热点        enable [guest|tp]/disable [guest|tp]
    设置上网时间         use: set plan rule [name] [host_mac] [mon{0|1}] [tue{0|1}] [wed{0|1}] [thu{0|1}] [fri{0|1}] [sat{0|1}] [sun{0|1}]  [start_time] [end_time]
    设备命名            use: set name [mac] [name]
    解除上网时间限制    use: unset rule [MAC]
    开启热点            enable [guest|tp]
    关闭热点            disable [guest|tp]
    断开广域网连接       set wan disable
    连接广域网           set wan connect

"""
reload(sys)
sys.setdefaultencoding('utf-8')


def Login():
    print "\033[32m%s\033[0m" % auth
    global url
    global post_data
    global get_data
    global full_url
    error_code = 0
    try:
        url = sys.argv[1]
        if re.search('[0-9]{1,3}(\.[0-9]{1,3}){3}',url):
            url = 'http://'+sys.argv[1]+'/'
            try:
                requests.get(url=url,timeout=12)
            except requests.ConnectionError:
                print "网络不可达"
                Log_out()
                return False 
        else:
            print "IP格式错误:",url
            Log_out()
            return False
    except IndexError:
        url = 'http://10.10.10.10/'
    Y_passwd = getpass.getpass('输入登录密码 >>> ')
    En_passwd = Encrypt(passwd=Y_passwd).encrypt_passwd()
    post_data = {'login': {'password': En_passwd}, 'method': 'do'}
    try:
        get_Text = requests.post(url=url, json=post_data).text
        get_data = json.loads(get_Text)
        full_url = url + 'stok=' + get_data['stok'] + '/ds'
        print "已登入,URL: %s" % urllib.unquote(full_url)
        print "\033[32m%s\033[0m" % sys_Log
    except requests.HTTPError as L_error:
        print L_error
        return False
    except requests.ConnectionError as C_error:
        print C_error
        return False
    except KeyError:
        print "密码错误,输入 relogin 重试"



def Json_Post_Data(cmdcode):
    online_host = {"hosts_info": {"table": "online_host"}, "method": "get"}
    wan_status_da = dict(network={"name": ["wan_status", "lan_status"]}, method="get")
    wlan_status_data = {"wireless": {"name": "wlan_host_2g"}, "method": "get"}
    dhcpd_data = {"dhcpd": {"name": ["udhcpd"], "table": ["dhcp_clients"]}, "network": {"name": ["lan"]},
                  "method": "get"}
    lan_ip_status = {"network": {"name": "lan"}, "method": "get"}
    Reboot = {"system": {"reboot": "null"}, "method": "do"}
    ip_mac_get = {"ip_mac_bind": {"table": ["user_bind", "sys_arp"]}, "method": "get"}
    try:

        sock = 'stok='
        try:
            prixe_t = get_data['stok']
        except KeyError as e:
            print "\033[32m请先登录\033[0m"
            return False
        fist_get = url + sock + prixe_t
        if cmdcode == 'wan':
            wan_status = requests.post(url=full_url, json=wan_status_da).json()
            WAN_Status(wan_status)
        elif cmdcode == 'wriless':
            wlan_stat = requests.post(url=full_url, json=wlan_status_data).json()
            WLAN_STATUS(wlan_stat)
        elif cmdcode == 'dhcpd':
            dhcpd_info = requests.post(url=full_url, json=dhcpd_data).json()
            DHCP_SERVER(dhcpd_info)
        elif cmdcode == 'host':
            online_host_info = requests.post(url=full_url, json=online_host).json()
            Online_host(online_host_info)
        elif re.search('log?', cmdcode):
            try:
                if re.search('log(.\d+)?', cmdcode).group() == 'log':
                    Log_file = {"system": {"read_logs": {"page": 1, "num_per_page": 20}}, "method": "do"}
                else:
                    page = cmdcode.split(' ')[1]
                    Log_file = {"system": {"read_logs": {"page": page, "num_per_page": 20}}, "method": "do"}
                log_table = PrettyTable(['日志', '内容'])
                try:
                    log_data = requests.post(url=full_url, json=Log_file).json()
                    log_length = log_data['syslog'].__len__()
                    for i in list(range(log_length)):
                        log_table.add_row(
                            [log_data['syslog'][i].keys()[0], urllib.unquote(log_data['syslog'][i].values()[0])])
                    print log_table
                except requests.exceptions.ConnectionError:
                    pass
            except AttributeError:
                pass
        elif cmdcode == 'scan':
            wireless_scan()
        elif cmdcode == 'bind':
            b_data = requests.post(url=full_url, json=ip_mac_get).json()
            Bind_info(b_data)
        elif cmdcode == 'rule':
            Show_firewalld_rule()
        elif cmdcode == 'lan':
            lan_data = requests.post(url=full_url, json=lan_ip_status).json()
            Lan_info(lan_data)

        elif cmdcode == 'reboot':
            reboot_route = requests.post(url=full_url, json=Reboot).json()
            print "重启中....等待(%s)秒" % reboot_route['wait_time']
            time.sleep(int(reboot_route['wait_time']))
            if reboot_route['error_code'] == int('0'):
                print "重启成功"
            Login()
        else:
            return False
    except KeyError as ERRON:
        print ERRON


def Bind_info(info):
    B_INF = info['ip_mac_bind']['user_bind']
    B_table = PrettyTable(['主机名', 'IP', 'MAC'])
    for i in list(range(B_INF.__len__())):
        B_table.add_row([B_INF[i].values()[0]['hostname'], B_INF[i].values()[0]['ip'], B_INF[i].values()[0]['mac']])
    print B_table


def WAN_Status(wan_status_data):
    print "广域网状态"
    wan_lan = wan_status_data['network']['lan_status']
    pppoe = {"protocol": {"name": ["wan", "pppoe"]}, "network": {"name": ["wan_status", "iface_mac"]}, "method": "get"}
    pppoe_data = requests.post(url=full_url, json=pppoe).json()['protocol']['pppoe']
    username = pppoe_data['username']
    password = pppoe_data['password']
    wan_Status = wan_status_data['network']['wan_status']
    wan_table = PrettyTable(
        ['物理状态', '上线时间', '下载速度', '链路状态', '广域网协议', '上传速度', 'IP地址', 'DNS服务器(主)', '子网掩码', 'DNS服务器(次)', '网关', '用户名', '密码'])
    wan_table.add_row([wan_Status['phy_status'], wan_Status['up_time'], wan_Status['down_speed'],
                       wan_Status['link_status'], wan_Status['proto'], wan_Status['up_speed'],
                       wan_Status['ipaddr'], wan_Status['snd_dns'],
                       wan_Status['netmask'], wan_Status['pri_dns'], wan_Status['gateway'], username, password])
    print wan_table


def WLAN_STATUS(wlan_info_data={}):
    print "无线状态"
    data = wlan_info_data['wireless']['wlan_host_2g']
    wan_table = PrettyTable(['AP', '带宽', '加密方式', '密码', '开启'])
    wan_table.add_row([data['ssid'], data['bandwidth'], data['encryption'], data['key'], data['enable']])
    print wan_table


def DHCP_SERVER(dhcp_info):
    print "DHCP服务器信息"
    dhcp_info = dhcp_info['dhcpd']['udhcpd']
    dhcp_table = PrettyTable(['状态', '地址租期', '起始IP', '结束IP', 'DNS服务器(首)', 'DNS服务器(次)', '网关'])
    dhcp_table.add_row(
        [dhcp_info['enable'], dhcp_info['lease_time'], dhcp_info['pool_start'], dhcp_info['pool_end'],
         dhcp_info['snd_dns'], dhcp_info['pri_dns'], dhcp_info['gateway']])
    print dhcp_table


def Online_host(host_info):
    print "在线主机"
    info = host_info['hosts_info']['online_host']
    hostINFO = PrettyTable(['主机名', 'IP地址', '上行速度(KB)', '下行速度(KB)', '下行限速(KB)', '上行限速(KB)', 'Mac地址', '连接方式', '规则'])
    for i in list(range(len(info))):
        if info[i].values()[0]['type'] == '1':
            TyPe = '无线连接'
        else:
            TyPe = '有线连接'
        if urllib.unquote(info[i].values()[0]['hostname']) == '':
            Hostname = "匿名主机"
        else:
            Hostname = urllib.unquote(info[i].values()[0]['hostname'])
        hostINFO.add_row([Hostname, info[i].values()[0]['ip'],
                          int(info[i].values()[0]['down_speed']) / 1024,
                          int(info[i].values()[0]['up_speed']) / 1024, info[i].values()[0]['down_limit'],
                          info[i].values()[0]['up_limit'], info[i].values()[0]['mac'], TyPe,
                          info[i].values()[0]['plan_rule']])
    print hostINFO


def Lan_info(info):
    L_info = info['network']['lan']
    L_table = PrettyTable(['接口', 'IP', 'MAC', 'IP模式', '子网掩码'])
    L_table.add_row(['lan', L_info['ipaddr'], L_info['macaddr'], L_info['ip_mode'], L_info['netmask']])
    print L_table


def wireless_scan():
    wire_json = {"wireless": {"table": "wlan_scan_2g"}, "method": "get"}
    wire_data = requests.post(url=full_url, json=wire_json).json()
    wire_list = wire_data['wireless']['wlan_scan_2g']
    wire_table = PrettyTable(['AP', 'MAC地址', '加密方式', '信号强度', '信道'])
    for i in list(range(wire_list.__len__())):
        i = wire_list[i].values()[0]
        wire_table.add_row([i['ssid'], i['bssid'], 'WPA2-PSK/WPA-PSK', i['rssi'], i['channel']])
    print wire_table


def DownloadL():
    down_log = {"system": {"download_logs": "null"}, "method": "do"}
    downLogInfo = requests.post(url=full_url, json=down_log).json()['url']
    log_url = full_url.replace('/ds', downLogInfo)
    print "下载日志文件: %s" % downLogInfo, log_url
    data = requests.get(log_url)
    with open('/tmp/syslog.txt', 'wb') as Data:
        Data.write(data.content)


def Show_firewalld_rule():
    rule_json = {"firewall": {"table": "redirect"}, "method": "get"}
    rule_data = requests.post(url=full_url, json=rule_json).json()
    rule_info = rule_data['firewall']['redirect']
    rule_table = PrettyTable(['编号', '协议', '源地址', '源端口', '外部端口'])
    for i in list(range(rule_info.__len__())):
        rule_table.add_row([rule_info[i].keys()[0].replace('redirect_', ''), rule_info[i].values()[0]['proto'],
                            rule_info[i].values()[0]['dest_ip'],
                            rule_info[i].values()[0]['dest_port'], rule_info[i].values()[0]['src_dport_start']])
    print rule_table


def Delete_log():
    delete_log = {"system": {"delete_logs": "null"}, "method": "do"}
    deleteLOG = requests.post(url=full_url, json=delete_log).json()['error_code']
    if deleteLOG == 0:
        print '已删除日志'


def Download_conf():
    down_conf = {"system": {"download_conf": "null"}, "method": "do"}
    downloadCONF = requests.post(url=full_url, json=down_conf).json()['url']
    config_url = full_url.replace('/ds', downloadCONF)
    print "下载配置文件: %s" % downloadCONF, config_url
    data = requests.get(config_url)

    with open('/tmp/config.bin', 'wb') as Data:
        Data.write(data.content)


def Log_out():
    log_option = {"system": {"logout": "null"}, "method": "do"}
    try:
        logOut_code = requests.post(url=full_url, json=log_option).json()
        if str(logOut_code['error_code']) == '0':
            print "退出,\033[32mBye,Bye!\033[0m"
    except requests.HTTPError:
        print "退出,\033[32mBye,Bye!\033[0m"
        return False
    except NameError:
        return False


def Show_block():
    print "禁用设备:"
    block_json = {"hosts_info": {"table": "blocked_host"}, "method": "get"}
    block_data = requests.post(url=full_url, json=block_json).json()
    block_list = block_data['hosts_info']['blocked_host']
    block_table = PrettyTable(['主机名', 'MAC'])
    for i in list(range(block_list.__len__())):
        iem = block_list[i].values()[0]
        block_table.add_row([iem['hostname'], iem['mac']])
    print block_table


def systeminfo():
    get_info = {"device_info": {"name": "info"}, "cloud_config": {"name": ["new_firmware", "upgrade_info"]},
                "method": "get"}
    disk_info = {"plugin_config": {"get_storage_info": 'null'}, "method": "do"}
    disk_data = requests.post(url=full_url, json=disk_info).json()
    total = disk_data['total']
    used = disk_data['used']
    free = (int(total) - int(used)) / 1024
    get_data = requests.post(url=full_url, json=get_info).json()
    uptede = get_data['cloud_config']['new_firmware']
    up_stat = uptede['fw_update_type']
    update_info = get_data['cloud_config']['upgrade_info']
    sys = get_data['device_info']['info']
    sys_sw_version = sys['sw_version']
    sys_hw_version = sys['hw_version']
    Product_Id = sys['product_id']
    Language = sys['language']
    DM = sys['domain_name']
    revision = sys['sys_software_revision']
    devicee_Name = sys['device_name']
    devi_info = sys['device_info']
    UPdate = 'yes'
    if up_stat == '0':
        UPdate = 'no'
    SysT = PrettyTable(['设备名称', '设备信息', '软件版本', '硬件版本', '域名', '语言', '生产ID', '软件修订码', '更新状况', '可用磁盘空间'])
    SysT.add_row([devicee_Name, devi_info, sys_sw_version, sys_hw_version, DM, Language, Product_Id, revision, UPdate,
                  str(free) + ' KB'])
    print SysT


class Set_Rule:
    def __init__(self, limit={}, lan={}, wan={}, dhcp_poo={}, pppoe={}, M_mac={}, mange_mac={}, bind={}, key={},
                 Block={}, rule={}, password={}, ap_name=None, name={}, plan_rule={}, url=None):
        """
        :type limit: dict
        :type url: str
        :type dhcp_poo: dict
        :type pppoe: dict
        :type key: dict
        :type ap_name: str
        """
        self.password = password
        self.block = Block
        self.rule = rule
        self.ap_name = ap_name
        self.bind = bind
        self.mac = M_mac
        self.mange_mac = mange_mac
        self.lan = lan
        self.wan = wan
        self.limit = limit
        self.dhcp_pool = dhcp_poo
        self.pppoe = pppoe
        self.key = key
        self.url = url
        self.name = name
        self.plan_rule = plan_rule

    def limit_seepd(self):
        """
        Use: set limit Hostname Mac Limit_up Limit_down
        :return:
        """
        limit_net = dict(hosts_info={
            "set_block_flag": {"mac": self.limit['mac'], "is_blocked": "0", "name": self.limit['hostname'],
                               "down_limit": self.limit['down'], "up_limit": self.limit['up']}}, method="do")
        limit_data = requests.post(url=self.url, json=limit_net).json()['error_code']
        if limit_data == 0:
            print "ok"
        else:
            print "error"

    def lan_network(self):
        """
        use:set net lan MODE IP_addr Netmask
        :return:
        """
        if self.lan['ip_mod'] == 'dynamic':
            set_lan = {"network": {"lan": {"ip_mode": "dynamic"}}, "method": "set"}
        else:
            set_lan = {
                "network": {"lan": {"ip_mode": "manual", "ipaddr": self.lan['ipaddr'], "netmask": self.wan['netmask']}},
                "method": "set"}
        error_code = requests.post(url=self.url, json=set_lan).json()['error_code']
        if error_code == 0:
            print 'ok'
        else:
            print 'error'

    def set_pppoe_mac(self):
        """
        use : set mac auto|Mac_addr:xx:xx:xx:xx:xx
        :return:
        """
        if self.mac['mac'] == 'auto':
            route_mac = '8C-A6-DF-8D-94-D4'
        else:
            route_mac = self.mac['mac']
        adv_wan_set = {"protocol": {"wan": {"macaddr": route_mac, "wan_rate": "auto"},
                                    "pppoe": {"dial_mode": "auto", "conn_mode": "auto", "mtu": "1480", "access": "",
                                              "server": "", "ip_mode": "dynamic", "dns_mode": "dynamic",
                                              "proto": "none"}},
                       "method": "set"}
        error_code = requests.post(url=self.url, json=adv_wan_set).json()['error_code']
        if error_code == 0:
            print 'ok'
        else:
            print 'error'

    def set_key(self):
        """
        use: set key APname[guest|tp] passwd
        :return:
        """
        if self.key['ap'] == 'guest':
            set_key = dict(
                guest_network={"guest_2g": {"ssid": "TPGuest_94D3", "key": self.key['pass'], "encrypt": "1"}},
                method="set")

        elif self.key['ap'] == 'tp':
            set_key = {"method": "set", "wireless": {"wlan_host_2g": {"key": self.key['pass']}}}
        else:
            pass
            return False
        error_code = requests.post(url=self.url, json=set_key).json()['error_code']
        if error_code == 0:
            print 'ok'
        else:
            print 'error'

    def pppoeConnect(self):
        """
        use:set pppoe MODE[default|manult] username password
        :return:
        """
        if self.pppoe['mode'] == 'default':
            username = "gydc283"
            password = '888888'
        else:
            username = self.pppoe['user']
            password = self.pppoe['pass']
        set_pppoe_connect = {
            "protocol": {"wan": {"wan_type": "pppoe"}, "pppoe": {"username": username, "password": password}},
            "method": "set"}
        error_code = requests.post(url=self.url, json=set_pppoe_connect).json()['error_code']
        if error_code == 0:
            print 'ok'
        else:
            print 'error'

    def DhcpServer(self):
        """
        usag:set dhcp pool 0[enable:0;disable:1] [start_ip] [end_ip] [GW] [dns1] [dns2] [leases]
        :return:
        """
        dhcp_pool = {"dhcpd": {
            "udhcpd": {"enable": self.dhcp_pool['enable'], "auto": 0, "pool_start": self.dhcp_pool['start'],
                       "pool_end": self.dhcp_pool['end'], "lease_time": self.dhcp_pool['lesase'],
                       "gateway": self.dhcp_pool['gw'], "pri_dns": self.dhcp_pool['dns1'],
                       "snd_dns": self.dhcp_pool['dns2']}}, "method": "set"}
        error_code = requests.post(url=self.url, json=dhcp_pool).json()['error_code']
        if error_code == 0:
            print 'ok'
        else:
            print 'error'

    def ChangePass(self):
        """
        use:set passwd old_passwd new_passwd
        :return:
        """
        old_pwd = Encrypt(self.password['old_pd']).encrypt_passwd()
        new_pwd = Encrypt(self.password['new_pd']).encrypt_passwd()
        change_pass = {"system": {"chg_pwd": {"old_pwd": old_pwd, "new_pwd": new_pwd}}, "method": "do"}
        error_code = requests.post(url=self.url, json=change_pass).json()['error_code']
        if error_code == 0:
            print 'ok,登录密码已更改为%s' % self.password['new_pd']
        else:
            print 'error'
        Log_out()
        Login()

    def mac_while(self):
        set_whilte_addr = {
            "wlan_access": {"white_list": [{"white_list_1": {"mac": "18-4f-32-03-2b-bb", "name": "RL"}}]},
            "error_code": 0}
        quit_whilte_addr = {"wlan_access": {"config": {"enable": "0"}}, "error_code": 0}

    def lan_mangeHost(self):
        """
        use:set lan mange MODE[host|all] MAC_ADDR
        :return:
        """
        if self.mange_mac['mode'] == 'host':
            set_lan_mangen_host = {"firewall": {
                "lan_manage": {"enable_all": "0", "mac1": self.mange_mac['mac1'], "mac2": "00-00-00-00-00-00",
                               "mac3": "00-00-00-00-00-00", "mac4": "00-00-00-00-00-00"}}, "method": "set"}
        else:
            set_lan_mangen_host = {"firewall": {"lan_manage": {"enable_all": "1"}}, "method": "set"}
        error_code = requests.post(url=self.url, json=set_lan_mangen_host).json()['error_code']
        if error_code == 0:
            print 'ok'
        else:
            print 'error'

    def Bind_IP(self):
        """
        set ip bind Number[seq] IP MAC Hostname
        :return:
        """
        ip_mac_bind = {"ip_mac_bind": {"table": "user_bind", "name": "user_bind_%s" % self.bind['num'],
                                       "para": {"ip": self.bind['ip'], "mac": self.bind['mac'],
                                                "hostname": self.bind['hostname']}}, "method": "add"}
        error_code = requests.post(url=self.url, json=ip_mac_bind).json()['error']
        if error_code == 0:
            print 'ok'
        else:
            print 'error'

    def Firewalld_rule(self):
        """
        use: set rule method[add|change|delete] src_port dest_port dest_IP
        :return:
        """
        if self.rule['method'] == 'add':
            Rule = {"firewall": {"table": "redirect", "name": "redirect_%s" % self.rule['num'],
                                 "para": {"proto": "all", "src_dport_start": self.rule['src_port'],
                                          "src_dport_end": self.rule['src_port'],
                                          "dest_ip": self.rule['dest_ip'], "dest_port": self.rule['dest_port']}},
                    "method": "add"}
        elif self.rule['method'] == 'change':
            Rule = {"firewall": {
                "redirect_%s" % self.rule['num']: {"proto": "all", "src_dport_start": self.rule['src_port'],
                                                   "src_dport_end": self.rule['src_port'],
                                                   "dest_ip": self.rule['dest_ip'],
                                                   "dest_port": self.rule['dest_port']}}, "method": "set"}
        elif self.rule['method'] == 'delete':
            Rule = {"firewall": {"name": ["redirect_%s" % self.rule['num']]}, "method": "delete"}
        else:
            return False
            pass
        error_code = requests.post(url=full_url, json=Rule).json()['error_code']
        if error_code == 0:
            print "ok"
            Show_firewalld_rule()
        else:
            print "error"

    def Block_(self):
        """
        use : set block METHOD[bloc|unblock] Mac Hostname
        :return:
        """
        if self.block['method'] == 'block':
            block_host = {"hosts_info": {
                "set_block_flag": {"mac": self.block['mac'], "is_blocked": "1", "name": self.block['hostname'],
                                   "down_limit": "0",
                                   "up_limit": "0"}}, "method": "do"}
        elif self.block['method'] == 'unblock':
            block_host = {"hosts_info": {
                "set_block_flag": {"mac": self.block['mac'], "is_blocked": "0", "name": self.block['hostname'],
                                   "down_limit": "0",
                                   "up_limit": "0"}}, "method": "do"}
        else:
            return False
            pass
        error_code = requests.post(url=self.url, json=block_host).json()['error_code']
        if error_code == 0:
            print 'ok'
        else:
            print 'error'

    def enable_ap(self):
        tp = 'wlan_host_2g'
        if self.ap_name == 'enable guest':
            Enable_json = {"guest_network": {"guest_2g": {"enable": "1"}}, "method": "set"}
        elif self.ap_name == 'disable guest':
            Enable_json = {"guest_network": {"guest_2g": {"enable": "0"}}, "method": "set"}
        elif self.ap_name == 'enable tp':

            Enable_json = {"wireless": {"wlan_host_2g": {"enable": "1"}}, "method": "set"}
        elif self.ap_name == 'disable tp':
            Enable_json = {"wireless": {"wlan_host_2g": {"enable": "0"}}, "method": "set"}
        else:
            return False
        error_code = requests.post(url=self.url, json=Enable_json).json()['error_code']
        if error_code == 0:
            print "ok"
        else:
            print error_code

    def set_device_name(self):
        """
        use: set name [mac] [name]
        :return:
        """
        query = {"hosts_info": {
            "set_block_flag": {"mac": self.name['mac'], "is_blocked": "0", "name": self.name['name'], "down_limit": "0",
                               "up_limit": "0"}}, "method": "do"}
        error_code = requests.post(url=self.url, json=query).json()['error_code']
        if error_code == 0:
            print 'ok'
        else:
            print 'error:', error_code

    def net_time(self):
        """
        use: set plan rule [name] [host_mac] [mon{0|1}] [tue] [wed] [thu] [fri] [sat] [sun]  [start_time] [end_time]
        :return:
        """
        RULE = self.plan_rule
        rule = {"hosts_info": {"name": "%s_plan_rule_1" % RULE['mac'].replace('-', ''), "table": "plan_rule",
                               "para": {"mon": RULE['mon'], "tue": RULE['tue'], "wed": RULE['wed'], "thu": RULE['thu'],
                                        "fri": RULE['fri'], "sat": RULE['sat'],
                                        "sun": RULE['sun'], "name": RULE['name'], "start_time": RULE['start_time'],
                                        "end_time": RULE['end_time']}},
                "method": "add"}
        error_code = requests.post(url=self.url, json=rule).json()['error_code']
        if error_code == 0:
            print 'ok'
        else:
            print 'error: ', error_code

    def unset_time(self):
        delete_rule = {"hosts_info": {"name": "%s_plan_rule_1" % self.plan_rule['mac'].replace('-', '')},
                       "method": "delete"}
        error_code = requests.post(url=self.url, json=delete_rule).json()['error_code']
        if error_code == 0:
            print 'ok'
        else:
            print 'error: ', error_code
    def pppoe_connect(self):
        if self.plan_rule['flat'] == 'connect':
            conne={"network":{"change_wan_status":{"proto":"pppoe","operate":"connect"}},"method":"do"}
        else:
            conne={"network":{"change_wan_status": {"proto":"pppoe","operate":"disconnect"}},"method":"do"}
        error_code = requests.post(url=self.url, json=conne).json()['error_code']
        if error_code == 0:
            print 'ok'
        else:
            print error_code


def Select_class():
    global lan_dict, mac_dict
    print "-->>进入系统设置控制台"
    while True:
        cmd = raw_input("set ->> console # ")
        try:
            if cmd == 'exit':
                break
            elif cmd == 'help':
                print Set_clsss_help
            elif cmd == 'set':
                pass
            elif re.match('set limit \w+', cmd):
                limit_op = cmd.split(' ')
                if limit_op.__len__() == 6:
                    L_dict = {'hostname': limit_op[2], 'mac': limit_op[3], 'down': limit_op[5], 'up': limit_op[4]}
                    Set_Rule(limit=L_dict, url=full_url).limit_seepd()
                else:
                    pass
            elif re.match('set net lan', cmd):
                lan_op = cmd.split(' ')
                if lan_op.__len__() < 3 or lan_op.__len__() > 6:
                    pass
                else:
                    if lan_op[3] == 'd':
                        lan_dict = {'ip_mode': 'dynamic'}
                    elif lan_op[3] == 's':
                        lan_dict = {'ipaddr': lan_op[4], 'netmask': lan_op[5]}
                    Set_Rule(lan=lan_dict, url=full_url).lan_network()
            elif re.match('set mac \S+', cmd):
                mac_op = cmd.split(' ')
                if mac_op.__len__() != 3:
                    pass
                else:
                    if mac_op[3] == 'auto':
                        mac_dict = {'mac': 'auto'}
                    else:
                        mac_dict = {'mac': mac_op[3]}
                Set_Rule(url=full_url, M_mac=mac_dict)
            elif re.match('set key \S+', cmd):
                key_op = cmd.split(' ')
                if key_op.__len__() != 4 and key_op[4].__len__() < 8:
                    pass
                else:
                    key_dict = {'ap': key_op[2], 'pass': key_op[3]}
                    Set_Rule(url=full_url, key=key_dict).set_key()
            elif re.match('set pppoe', cmd):
                pppoe_op = cmd.split(' ')
                if pppoe_op.__len__() != 5:
                    pass
                else:
                    ppp_dict = {'mode': pppoe_op[2], 'user': pppoe_op[3], 'pass': pppoe_op[4]}
                    Set_Rule(url=full_url, pppoe=ppp_dict).pppoeConnect()
            elif re.match('set dhcp pool \S+', cmd):
                dhcp_op = cmd.split(' ')
                if dhcp_op.__len__() != 10:
                    pass
                else:
                    dhcp_dict = dict(enable=dhcp_op[3], start=dhcp_op[4], end=dhcp_op[5], gw=dhcp_op[6],
                                     dns1=dhcp_op[7],
                                     dns2=dhcp_op[8], lesase=dhcp_op[9])
                    Set_Rule(url=full_url, dhcp_poo=dhcp_dict).DhcpServer()
            elif re.match('set lan mange', cmd):
                mangge_op = cmd.split(' ')
                if mangge_op.__len__() < 4 or mangge_op.__len__() > 5:
                    pass
                else:
                    mange_dict = {'mode': mangge_op[3], 'mac1': mangge_op[4]}
                    Set_Rule(url=full_url, mange_mac=mange_dict).lan_mangeHost()
            elif re.match('set ip bind \S+', cmd):
                bind_op = cmd.split(' ')
                if bind_op.__len__() != 7:
                    pass
                else:
                    bind_dict = {'num': bind_op[3], 'ip': bind_op[4], 'mac': bind_op[5], 'hostname': bind_op[6]}
                    Set_Rule(url=full_url, bind=bind_dict).Bind_IP()
            elif re.match('set firewalld \S+', cmd):
                rule_op = cmd.split(' ')
                if rule_op.__len__() < 4 or rule_op.__len__() > 7:
                    pass
                elif rule_op.__len__() == 4:
                    rule_dict = {'method': rule_op[2], 'num': rule_op[3]}
                else:
                    rule_dict = {'method': rule_op[2], 'num': rule_op[3], 'src_port': rule_op[4],
                                 'dest_port': rule_op[5],
                                 'dest_ip': rule_op[6]}
                Set_Rule(url=full_url, rule=rule_dict).Firewalld_rule()
            elif re.match('set block \S+', cmd):
                block_op = cmd.split(' ')
                if block_op.__len__() < 4:
                    pass
                else:
                    block_dict = {'method': block_op[2], 'mac': block_op[3], 'hostname': block_op[4]}
                    Set_Rule(url=full_url, Block=block_dict).Block_()
            elif re.match('set passwd \S+', cmd):
                passwd_op = cmd.split(' ')
                if passwd_op.__len__() != 4:
                    pass
                else:
                    passwd_dict = {'old_pd': passwd_op[2], 'new_pd': passwd_op[3]}
                    Set_Rule(url=full_url, password=passwd_dict).ChangePass()
            elif re.match('enable \w+', cmd) or re.match('disable \w+', cmd):
                Set_Rule(url=full_url, ap_name=cmd).enable_ap()
            elif re.match('set name \S+', cmd):
                name_op = cmd.split(' ')
                if name_op.__len__() != 4:
                    pass
                else:
                    name_dict = {'mac': name_op[2], 'name': name_op[3]}
                    Set_Rule(url=full_url, name=name_dict).set_device_name()
            elif re.match('set plan rule \S+', cmd):
                plan = cmd.split(' ')
                if plan.__len__() == 14:
                    plan_dict = {'name': plan[3], 'mac': plan[4], 'mon': plan[5], 'tue': plan[6], 'wed': plan[7],
                                 'thu': plan[8], 'fri': plan[9], 'sat': plan[10], 'sun': plan[11],
                                 'start_time': plan[12], 'end_time': plan[13]}
                    Set_Rule(url=full_url, plan_rule=plan_dict).net_time()
            elif re.match('unset rule \S+', cmd):
                unset = cmd.split(' ')
                if unset.__len__() == 3:
                    unset_dict = {'mac': unset[2]}
                    Set_Rule(url=full_url, plan_rule=unset_dict).unset_time()
                else:
                    pass
            elif re.match('set wan \S+',cmd):
                wan = cmd.split(' ')
                if wan.__len__() == 3:
                    wan_dict = {'flat': wan[2]}
                    Set_Rule(url=full_url,plan_rule=wan_dict).pppoe_connect()
                else:
                    pass
            else:
                pass
        except IndexError as e:
            print "输入错误", e
            pass
        except NameError as s:
            print "输入错误", s
            pass
        except KeyError as f:
            print "输入错误", f
            pass


class Encrypt:
    def __init__(self, passwd=None, flat=1):
        self.passwd = passwd
        self.Flat = flat

    def encrypt_passwd(self):
        a = "RDpbLfCPsJZ7fiv"
        c = 'yLwVl0zKqws7LgKPRQ84Mdt708T1qQ3Ha7xv3H7NyU84p21BriUWBU43odz3iP4rBL3cD02KZciXTysVXiV8ngg6vL48rPJyAUw0HurW20xqxv9aYb4M9wK1Ae0wlro510qXeU07kV57fQMc8L6aLgMLwygtc0F10a0Dg70TOoouyFhdysuRMO51yY5ZlOZZLEal1h0t9YQW0Ko7oBwmCAHoic4HYbUyVeU3sfQ1xtXcPcf1aT303wAQhv66qzW'
        b = self.passwd
        e = ''
        f, g, h, k, l = 187, 187, 187, 187, 187
        n = 187
        g = len(a)
        h = len(b)
        k = len(c)
        if g > h:
            f = g
        else:
            f = h
        for p in list(range(0, f)):
            n = l = 187
            if p >= g:
                n = ord(b[p])
            else:
                if p >= h:
                    l = ord(a[p])
                else:
                    l = ord(a[p])
                    n = ord(b[p])
            e += c[(l ^ n) % k]
        try:
            if self.Flat == 0:
                print e
            else:
                return e
        except NameError:
            pass


if __name__ == '__main__':
    Login()
    print "输入help获取帮助"
    while True:
        cmd = raw_input('console >>>')
        if cmd == '':
            pass
        elif cmd == 'exit' or cmd == 'quit':
            Log_out()
            break
        elif cmd == 'help':
            print help_text
            continue
        elif re.search('download', cmd):
            if cmd != 'download':
                dType = cmd.split(' ')[1]
                if dType == 'log':
                    DownloadL()
                elif dType == 'config':
                    Download_conf()
                else:
                    pass
        elif cmd == 'block':
            Show_block()
        elif cmd == 'delete log':
            Delete_log()
        elif cmd == 'set':
            Select_class()
        elif cmd == 'relogin':
            try:
                Log_out()
                Login()
            except NameError:
                print "请先登录"
                Login()
        elif re.match('passwd', cmd):
            try:
                Encrypt(cmd.split(' ')[1], 0).encrypt_passwd()
            except IndexError:
                pass
        elif re.match('systeminfo', cmd):
            systeminfo()
        else:
            try:
                Json_Post_Data(cmd)
            except NameError as ER:
                print ER
