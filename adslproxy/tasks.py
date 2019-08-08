#!/usr/bin/env python3
# -*-coding:utf-8-*-
# @Version: Python 3
# 定时任务、拨号(每次启动程序都执行本脚本，一直执行)


import os
import sys

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(ROOT_DIR)

import json
import paramiko
import threading
from config.hosts import *
from config.api_config import *
from adslproxy.hosts_managers import pppoe, hosts_init, clean_sys, check_host
from adslproxy.db import RedisClient


def solve_badhosts():
    # 处理问题主机，根据问题类型，重装软件或拨号。

    badhosts_info_dict = RedisClient(list_key='badhosts').all()
    if badhosts_info_dict:
        for key, v in badhosts_info_dict.items():
            values = v
            # 从配置文件读取（链接信息可能已被修正了）
            for _group in HOSTS_GROUP:
                if key in HOSTS_GROUP.get(_group).keys():
                    values = HOSTS_GROUP.get(_group)[key]

            with paramiko.SSHClient() as ssh_cli:
                ssh_cli.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                try:
                    ssh_cli.connect(hostname=values['host'], username=values['username'],
                                    password=values['password'],
                                    port=values['port'])
                except paramiko.ssh_exception.NoValidConnectionsError as e:
                    # init_error错误是ssh信息配置错误，只要修正了配置文件就能继续下去。
                    # 如果还是链接不上，还是init_error则更新信息。
                    logger.error(f'主机：{key}，配置有问题，请手动修复并重启程序! {e}')
                    values['problem'] = 'init_error'
                    RedisClient(list_key='badhosts').set(key, json.dumps(values))

            # 如果是adsl_error错误，则需要重新安装软件
            if values['problem'] == 'adsl_error':
                clean_sys(ssh_cli)
                check_host(ssh_cli)

            # 开始拨号
            try:
                proxy_ip = pppoe(ssh_cli, values['cmd'])
            except Exception:
                # 依然有问题，不做操作
                pass
            # 如果没问题，加入代理，从问题主机列表移除并添加到正常主机列表
            RedisClient(list_key='adslproxy').set(key, f'{proxy_ip}:{PROXY_PORT}')
            RedisClient(list_key='badhosts').remove(key)
            RedisClient(list_key='goodhosts').set(key, json.dumps(values))
    # 间隔300秒 时间再次执行
    threading.Timer(300, solve_badhosts).start()


def adsl_switch_ip():
    # 定时拨号的主机是从正常的主机中获取的。
    hosts_info_dict = RedisClient(list_key='goodhosts').all()
    # 开始拨号（从拨号到IP可用有一定时间间隔，不要用异步，防止短时间内无IP可用）
    for key, values in hosts_info_dict.items():
        with paramiko.SSHClient() as ssh_cli:
            ssh_cli.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            # 这里不用捕捉异常，在hosts_init()时即可判断时否异常
            ssh_cli.connect(hostname=values['host'], username=values['username'],
                            password=values['password'],
                            port=values['port'])
            try:
                proxy_ip = pppoe(ssh_cli, values['cmd'])
            except Exception:
                # 重新拨号得不到新IP，则移除旧IP，且从正常主机列表移除并加入问题主机列表
                logger.error(f'{key}:拨号失败了！')
                RedisClient(list_key='adslproxy').remove(key)
                RedisClient(list_key='goodhosts').remove(key)
                values['problem'] = 'adsl_error'
                RedisClient(list_key='badhosts').set(key, json.dumps(values))
            # 存储到Redis
            RedisClient(list_key='adslproxy').set(key, f'{proxy_ip}:{PROXY_PORT}')
    # 间隔ADSL_SWITCH_TIME 时间再次执行
    threading.Timer(ADSL_SWITCH_TIME, adsl_switch_ip).start()


def update_user_info():
    # 更新API用户信息(AB集切换)
    a_or_b = RedisClient(list_key='ab_set').get('a_or_b')
    if a_or_b == "userinfo_a":
        for group in USER:
            for user_info in USER[group].values():
                RedisClient(list_key='userinfo_b').set(user_info['username'], user_info['password'])
        RedisClient(list_key='ab_set').set('a_or_b', 'userinfo_b')
        RedisClient(list_key='userinfo_a').delete()
    elif a_or_b == "userinfo_b":
        for group in USER:
            for user_info in USER[group].values():
                RedisClient(list_key='userinfo_a').set(user_info['username'], user_info['password'])
        RedisClient(list_key='ab_set').set('a_or_b', 'userinfo_a')
        RedisClient(list_key='userinfo_b').delete()
    # 间隔60秒 时间再次执行
    threading.Timer(60, update_user_info).start()


def tasks_main():
    # hosts_manages启动时会初始化主机，并把代理写入Redis，此处接着执行定时任务即可。
    t2 = threading.Timer(ADSL_SWITCH_TIME, adsl_switch_ip)
    t2.start()
    # 立刻处理问题主机
    # print("处理问题主机！")
    t3 = threading.Timer(0, solve_badhosts)
    t3.start()


if __name__ == "__main__":
    # 清空Redis中的数据
    RedisClient(list_key='adslproxy').delete()
    RedisClient(list_key='goodhosts').delete()
    RedisClient(list_key='badhosts').delete()
    RedisClient(list_key='userinfo_a').delete()
    RedisClient(list_key='userinfo_b').delete()
    # 定时更新用户账户
    RedisClient(list_key='ab_set').set('a_or_b', 'userinfo_b')  # 启动初始化要设置一下，防止key不存在报错。
    t1 = threading.Timer(0, update_user_info)
    t1.start()
    # hosts_init启动时会初始化主机，并把代理写入Redis，此处接着执行定时任务即可。
    hosts_init()  # join线程阻塞（配置环境需要时间，只花最慢一台机器的时间）
    # 开始定时拨号任务，子线程开始等待，不影响下面执行
    tasks_main()
