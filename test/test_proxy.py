#!/usr/bin/env python3
# -*-coding:utf-8-*-
# @Version: Python 3
#

import os
from urllib import request

# 代理服务器账户
proxy_host = '114.115.166.201'
proxy_user = 'myproxy'
proxy_passwd = 'N2PYOnRDk5gKInqQ'
proxy_port = 3100

# 这是代理IP
proxy = {'http': f'http://{proxy_user}:{proxy_passwd}@{proxy_host}:{proxy_port}'}

url1 = 'http://members.3322.org/dyndns/getip'
url2 = 'http://test.heroflower.top/'
url3 = 'https://weixin.sogou.com/weixin?type=2&ie=utf8&s_from=hotnews&query=%E6%9C%80%E6%83%A8%E8%88%AA%E7%8F%AD'


def test_porxy():
    # 访问网址
    # 创建ProxyHandler
    proxy_support = request.ProxyHandler(proxy)
    # 创建Opener
    opener = request.build_opener(proxy_support)
    # 添加User Angent
    opener.addheaders = [('User-Agent',
                          'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36')]
    # 安装OPener
    request.install_opener(opener)
    # 使用自己安装好的Opener
    response = request.urlopen(url1, timeout=5)
    # 读取相应信息并解码
    html = response.read().decode("utf-8")
    # 打印信息
    print("代理IP为：", html)
    # 打印本机IP
    print('本机外网IP为：', os.popen('curl http://members.3322.org/dyndns/getip').read())


if __name__ == '__main__':
    test_porxy()

######################################

import socket
import struct
import random
import requests


def createHeader():
    ip = socket.inet_ntoa(struct.pack('>I', random.randint(1, 0xffffffff)))
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'User-Agent': 'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0',
        'CLIENT-IP': ip,
        'X-FORWARDED-FOR': ip
    }
    return headers


# if __name__ == '__main__':
#     headers = createHeader()
#     html = requests.get(url3, headers=headers, proxies=proxy)
#     print(html.text)
#     import re
#
#     sss = re.findall('clientIp = "(.*?)";', html.text)
#     print(sss)
