#!/usr/bin/env python3
# -*-coding:utf-8-*-
# @Version: Python 3
# API配置文件


# 代理服务器统一账户
PROXY_USER = 'myproxy'
PROXY_PASSWORD = 'N2PYOnRDk5gKInqQ'
PROXY_PORT = 3100

# Redis Config
REDIS_HOST = '114.115.166.201'
REDIS_PORT = 6390
REDIS_PASSWORD = ''
PROXY_KEY = 'adslproxy'

# API Config
API_HOST = '127.0.0.1'
API_PORT = '5001'
"""
整体设计：
1、IP_INVALID_TIME： IP不能用废，本程序配置一个IP可以使用多久，之后必须更换IP，有利于多人使用IP但不被封；
高并发业务可以把时间设低一点，根据业务场景设定。
否则拒绝新的请求（可能根据用户的IP来定在squid中设置）

2、ADSL_SWITCH_TIME： 考虑到adsl主机并不是很多，避免网站检测到相同IP，一定时间后刷新ADSL代理池的所有IP。
高并发业务可以把时间设低一点，不建议低于120秒（adsl主机拨号间隔限死）
"""
# IP 失效时间（秒），不会从Redis中删除，只是换一个新IP
IP_INVALID_TIME = 60
# ADSL切换IP的时间（秒），同时更新Redis（注意：每次拨号时大约要8秒左右新IP才可用，服务商限制！）
ADSL_SWITCH_TIME = 3600 * 3

