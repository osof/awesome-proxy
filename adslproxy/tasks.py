#!/usr/bin/env python3
# -*-coding:utf-8-*-
# @Version: Python 3
# 定时任务、拨号(每次启动程序都执行本脚本，一直执行)


import paramiko
import threading
from config.hosts import *
from config.api_config import *
from adslproxy.hosts_managers import pppoe, task_main
from adslproxy.db import RedisClient

redis_cli = RedisClient()


def adsl_switch_ip():
    # 开始拨号（从拨号到IP可用有一定时间间隔，不要用异步，防止短时间内无IP可用）
    for _group in HOSTS_GROUP:
        host_list = HOSTS_GROUP.get(_group)
        for key, values in host_list.items():
            with paramiko.SSHClient() as ssh_cli:
                ssh_cli.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh_cli.connect(hostname=values['host'], username=values['username'],
                                password=values['password'],
                                port=values['port'])
                proxy_ip = pppoe(ssh_cli)
                # 存储到Redis
                redis_cli.set(key, f'{proxy_ip}:{PROXY_PORT}')
    # 间隔ADSL_SWITCH_TIME 时间再次执行
    timer = threading.Timer(ADSL_SWITCH_TIME, adsl_switch_ip)
    timer.start()


def adsl_main():
    # hosts_manages启动时会初始化主机，并把代理写入Redis，此处接着执行定时任务即可。
    timer = threading.Timer(ADSL_SWITCH_TIME, adsl_switch_ip)
    timer.start()


if __name__ == "__main__":
    # task_main启动时会初始化主机，并把代理写入Redis，此处接着执行定时任务即可。
    task_main()
    # 开始定时拨号任务
    adsl_main()
