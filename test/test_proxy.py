#!/usr/bin/env python3
# -*-coding:utf-8-*-
# @Autuor : LeoLan  mail：842632422@qq.com
# @Version: Python 3
#

import os
from urllib import request

# 代理服务器账户
proxy_host = '127.0.0.1'
proxy_user = 'myproxy'
proxy_passwd = 'N2PYOnRDk5gKInqQ'
proxy_port = 3100


def test_porxy():
    # 访问网址
    url = 'http://members.3322.org/dyndns/getip'
    # 这是代理IP
    proxy = {'http': f'http://{proxy_user}:{proxy_passwd}@{proxy_host}:{proxy_port}'}
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
    response = request.urlopen(url, timeout=5)
    # 读取相应信息并解码
    html = response.read().decode("utf-8")
    # 打印信息
    print("代理IP为：", html)
    # 打印本机IP
    print('本机外网IP为：', os.popen('curl http://members.3322.org/dyndns/getip').read())


if __name__ == '__main__':
    test_porxy()
