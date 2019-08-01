#!/usr/bin/env python3
# -*-coding:utf-8-*-
# @Version: Python 3
# 执行初始化、主机管理(每次启动程序都执行本脚本，一次性执行)


import os
import re
import time
import threading
import paramiko
from retrying import retry
from config.hosts import *
from config.api_config import *
from adslproxy.db import RedisClient

redis_cli = RedisClient()


@retry(stop_max_attempt_number=5)
def get_proxy_ip(ssh_cli):
    time.sleep(5)  # 拨号后要好几秒后才能分配到IP
    # 获取代理IP(能请求成功说明代理IP有效)，注意stdout只有第一次输出是有效的，再次获取是空的。
    stdin, stdout, stderr = ssh_cli.exec_command('curl http://members.3322.org/dyndns/getip')
    proxy_ip = stdout.readlines()
    if proxy_ip:
        proxy_ip = proxy_ip[0].strip()
        return proxy_ip
    else:
        raise Exception('获取不到IP，尝试重新获取')


@retry(stop_max_attempt_number=5)
def pppoe(ssh_cli):
    # 拨号程序
    try:
        _stdin, _stdout, _stderr = ssh_cli.exec_command('adsl-stop && sleep 3 && adsl-start')
    except Exception:
        raise Exception('ADSL 拨号超时，重试中！')
    return get_proxy_ip(ssh_cli)


def set_sh_config():
    # 修改squid.sh中的代理账户配置，便于执行
    with open('../script-sh/squid.sh', 'r', encoding='utf-8') as f:
        m = re.findall('(squid_proxy_.*?)=(.*?)\s', f.read())
        for key, values in dict(m).items():
            # print(key, values)
            if key[12:] == "user":
                os.system(f'sed -i "s/{key}={values}/{key}={PROXY_USER}/g" ../script-sh/squid.sh')
            elif key[12:] == "passwd":
                os.system(f'sed -i "s/{key}={values}/{key}={PROXY_PASSWORD}/g" ../script-sh/squid.sh')
            elif key[12:] == "port":
                os.system(f'sed -i "s/{key}={values}/{key}={PROXY_PORT}/g" ../script-sh/squid.sh')
    return True


def check_host(ssh_cli):
    # 检查主机是否有安装squid，并安装好
    try:
        ssh_cli.exec_command('squid -v|grep Version')
        try:
            # squid是正常的，重启防假死、程序已崩溃
            ssh_cli.exec_command('./squid.sh restart')
        except Exception:
            # 脚本不存在
            with ssh_cli.open_sftp() as sftp:
                set_sh_config()  # 上传文件前要更新脚本的配置信息
                sftp.put('../script-sh/squid.sh', 'squid.sh')
            ssh_cli.exec_command('chmod +x squid.sh && ./squid.sh restart')
    except Exception:
        # 系统中没有安装squid
        with ssh_cli.open_sftp() as sftp:
            set_sh_config()  # 上传文件前要更新脚本的配置信息
            sftp.put('../script-sh/squid.sh', 'squid.sh')
        ssh_cli.exec_command('chmod +x squid.sh && ./squid.sh install')


def run_task(key, values):
    print(threading.currentThread().getName())
    print('现在处理', key)
    with paramiko.SSHClient() as ssh_cli:
        ssh_cli.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_cli.connect(hostname=values['host'], username=values['username'],
                        password=values['password'],
                        port=values['port'])
        # 检查squid
        check_host(ssh_cli)
        # 开始拨号
        try:
            proxy_ip = pppoe(ssh_cli)
        except Exception:
            # TODO:存储到异常主机稍后处理
            # redis_cli.set(key, f'{proxy_ip}:{PROXY_PORT}')
            pass
        # 存储到Redis
        redis_cli.set(key, f'{proxy_ip}:{PROXY_PORT}')


def hosts_init():
    # 清空Redis中的代理
    redis_cli.delete()
    # 一启动先拨号一次号，保存所有主机的代理IP
    # 主机管理(启动程序时会检查并配置所有主机)
    for _group in HOSTS_GROUP:
        host_list = HOSTS_GROUP.get(_group)
        for key, values in host_list.items():
            # run_task(key, values)
            t = threading.Thread(target=run_task, args=(key, values))
            t.start()

        for t in host_list:
            # 阻塞线程，等待子线程执行完毕。
            t.join()


if __name__ == '__main__':
    hosts_init()
