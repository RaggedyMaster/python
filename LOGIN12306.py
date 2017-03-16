#!/bin/env python
# -*- coding=utf-8 -*-
import ssl
import sys
import urllib2
import random
import httplib
import json
from cookielib import LWPCookieJar
import urllib
import re
import getpass

reload(sys)
sys.setdefaultencoding('UTF8')
cookiejar = LWPCookieJar()
cookiesuppor = urllib2.HTTPCookieProcessor(cookiejar)
opener = urllib2.build_opener(cookiesuppor, urllib2.HTTPHandler)
urllib2.install_opener(opener)
ssl._create_default_https_context = ssl._create_unverified_context
codeimg = 'https://kyfw.12306.cn/otn/passcodeNew/getPassCodeNew?module=login&rand=sjrand&%s' % random.random()

baner = """
##################################
    12306登录脚本,作者Mr RJL
    python版本:2.7,适用于linux
    验证码输入方式:
    输入问题对应的图片序号,1-8;
    多个以','分隔.如:1,2,3
##################################
"""
def get(url):
    try:
        request = urllib2.Request(url=url)
        # req.add_header('User-Agent', 'Mozilla/5.0 (X11; Fedora; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0')
        request.add_header("Content-Type", "application/x-www-form-urlencoded; charset=utf-8")
        request.add_header('X-Requested-With', 'xmlHttpRequest')
        request.add_header('User-Agent',
                           'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.154 Safari/537.36')
        request.add_header('Referer', 'https://kyfw.12306.cn/otn/login/init')
        request.add_header('Accept', '*/*')
        result = urllib2.urlopen(request).read()
        assert isinstance(result, object)
        return result
    except httplib.error as e:
        print e
        pass
    except urllib2.URLError as e:
        print e
        pass
    except urllib2.HTTPBasicAuthHandler, urllib2.HTTPError:
        print 'error'
        pass


def Post(url, data):
    try:
        request = urllib2.Request(url=url, data=urllib.urlencode(data))
        # req.add_header('User-Agent', 'Mozilla/5.0 (X11; Fedora; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0')
        # request = urllib2.Request(ajax_url, urllib.urlencode(dc))
        request.add_header("Content-Type", "application/x-www-form-urlencoded; charset=utf-8")
        request.add_header('X-Requested-With', 'xmlHttpRequest')
        request.add_header('User-Agent',
                           'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.154 Safari/537.36')
        request.add_header('Referer', 'https://kyfw.12306.cn/otn/login/init')
        request.add_header('Accept', '*/*')
        # request.add_header('Accept-Encoding', 'gzip, deflate')
        result = urllib2.urlopen(request).read()
        return result
    except httplib.error as e:
        return e
    except urllib2.URLError as e:
        return e
    except urllib2.HTTPBasicAuthHandler, urllib2.HTTPError:
        return 'error'


def cookietp():
    stoidinput("获取Cookie")
    Url = "https://kyfw.12306.cn/otn/login/init"
    get(Url)
    for index, c in enumerate(cookiejar):
        stoidinput(c)


def getImg():
    stoidinput("下载验证码...")
    result = get(codeimg)
    try:
        if open('/tmp/tkcode', 'wb').write(result) :
            import os
            os.system("oeg /tmp/tkcode &")
        else:
            return False
    except OSError as e:
        print e
        pass


def stoidinput(text):
    """
    正常信息输出
    :param text:
    :return:
    """
    print "\033[34m[*]\033[0m %s " % text


def errorinput(text):
    """
    错误信息输出
    :param text:
    :return:
    """
    print "\033[32m[!]\033[0m %s " % text
    return False


def codexy():
    """
    获取验证码
    :return: str
    """

    Ofset = raw_input("[*] 请输入验证码: ")
    select = Ofset.split(',')
    global randCode
    post = []
    offsetsX = 0  # 选择的答案的left值,通过浏览器点击8个小图的中点得到的,这样基本没问题
    offsetsY = 0  # 选择的答案的top值
    for ofset in select:
        if ofset == '1':
            offsetsY = 46
            offsetsX = 42
        elif ofset == '2':
            offsetsY = 46
            offsetsX = 105
        elif ofset == '3':
            offsetsY = 45
            offsetsX = 184
        elif ofset == '4':
            offsetsY = 48
            offsetsX = 256
        elif ofset == '5':
            offsetsY = 36
            offsetsX = 117
        elif ofset == '6':
            offsetsY = 112
            offsetsX = 115
        elif ofset == '7':
            offsetsY = 114
            offsetsX = 181
        elif ofset == '8':
            offsetsY = 111
            offsetsX = 252
        else:
            pass
        post.append(offsetsX)
        post.append(offsetsY)
    randCode = str(post).replace(']', '').replace('[', '').replace("'", '').replace(' ', '')


def login(user, passwd):
    randurl = 'https://kyfw.12306.cn/otn/passcodeNew/checkRandCodeAnsyn'
    logurl = 'https://kyfw.12306.cn/otn/login/loginAysnSuggest'
    surl = 'https://kyfw.12306.cn/otn/login/userLogin'
    geturl = 'https://kyfw.12306.cn/otn/index/initMy12306'
    randdata = {
        "randCode": randCode,
        "rand": "sjrand"
    }
    logdata = {
        "loginUserDTO.user_name": user,
        "userDTO.password": passwd,
        "randCode": randCode
    }
    ldata = {
        "_json_att": None
    }
    fresult = json.loads(Post(randurl, randdata), encoding='utf8')
    checkcode = fresult['data']['msg']
    if checkcode == 'FALSE':
        errorinput("验证码有误,请重试")
    else:
        stoidinput("验证码通过,开始登录..")
        try:
            tresult = json.loads(Post(logurl, logdata), encoding='utf8')
            if tresult['data'].__len__() == 0:
                errorinput("登录失败: %s" % tresult['messages'][0])
            else:

                stoidinput("登录成功")
                sult = Post(surl, ldata)
                getUserinfo()
        except ValueError as e:
            errorinput(e)


def getUserinfo():
    """
    登录成功后,显示用户名
    :return:
    """
    url = 'https://kyfw.12306.cn/otn/modifyUser/initQueryUserInfo'
    data = dict(_json_att=None)
    result = Post(url, data)
    userinfo = result
    name = r'<input name="userDTO.loginUserDTO.user_name" style="display:none;" type="text" value="(\S+)" />'
    try:
        stoidinput("欢迎 %s 登录" % re.search(name, result).group(1))
    except AttributeError:
        pass


def main():
    user = raw_input("[+] 用户名(用户名/邮箱/手机): ")
    passwd = getpass.getpass("[+] 密码: ")
    if user == '' or passwd == '':
        errorinput("用户名或密码不能为空!")
    else:
        cookietp()
        getImg()
        codexy()
        login(user, passwd)
def logout():
    url = 'https://kyfw.12306.cn/otn/login/loginOut'
    result = get(url)
    if result:
        stoidinput("已退出")
    else:
        errorinput("退出失败")

if __name__ == "__main__":
    print baner
    main()
    logout()
