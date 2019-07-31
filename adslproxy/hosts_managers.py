#!/usr/bin/env python3
# -*-coding:utf-8-*-
# @Version: Python 3
# 执行初始化、主机管理


# TODO：修改为多线程，拨号程序

import os
import re
import time
import paramiko
from config.hosts import *
from config.api_config import *
from adslproxy.db import RedisClient

redis_cli = RedisClient()


def pppoe(ssh_cli):
    # 拨号程序
    _stdin, _stdout, _stderr = ssh_cli.exec_command('adsl-stop && sleep 3 && adsl-start')
    time.sleep(5)
    # 获取代理IP(能请求成功说明代理IP有效)
    stdin, stdout, stderr = ssh_cli.exec_command('curl http://members.3322.org/dyndns/getip')
    proxy_ip = stdout.readlines()[0]
    return proxy_ip.strip()


def set_sh_config():
    # 修改squid.sh中的代理账户配置，便于执行
    with open('../script-sh/squid.sh', 'r', encoding='utf-8') as f:
        m = re.findall('(squid_proxy_.*?)=(.*?)\s', f.read())
        for key, values in dict(m).items():
            # print(key, values)
            print(f'{key}={values}')
            print(key[12:])
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


def task_main():
    # 主机管理(启动程序时会检查并配置所有主机)
    for _group in HOSTS_GROUP:
        host_list = HOSTS_GROUP.get(_group)
        for key, values in host_list.items():
            with paramiko.SSHClient() as ssh_cli:
                ssh_cli.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh_cli.connect(hostname=values['host'], username=values['username'],
                                password=values['password'],
                                port=values['port'])
                # 检查squid
                check_host(ssh_cli)
                # 开始拨号
                proxy_ip = pppoe(ssh_cli)
                # 存储到Redis
                redis_cli.set(key, f'{proxy_ip}:{PROXY_PORT}')


if __name__ == '__main__':
    task_main()
