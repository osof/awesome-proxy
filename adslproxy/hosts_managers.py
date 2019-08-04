#!/usr/bin/env python3
# -*-coding:utf-8-*-
# @Version: Python 3
# 执行初始化、主机管理(每次启动程序都执行本脚本，一次性执行)


import os
import re
import time
import json
import threading
import paramiko
from retrying import retry
from config.hosts import *
from config.api_config import *
from adslproxy.db import RedisClient
from adslproxy.api_server import WORK_DIR

SCRIPT_DIR = os.path.join(WORK_DIR, 'script-sh')
SQUID_SH = os.path.join(SCRIPT_DIR, 'squid.sh')


@retry(stop_max_attempt_number=5)
def get_proxy_ip(ssh_cli):
    time.sleep(5)  # 拨号后要好几秒后才能分配到IP
    # 获取代理IP(能请求成功说明代理IP有效)，注意stdout只有第一次输出是有效的，再次获取是空的。
    stdin, stdout, stderr = ssh_cli.exec_command('curl http://members.3322.org/dyndns/getip')
    proxy_ip = stdout.readlines()  # 要获取stdout的内容不能先用if判断（第二次读取内容为空），而是先赋值
    if proxy_ip:
        proxy_ip = proxy_ip[0].strip()
        return proxy_ip
    else:
        raise Exception('获取不到IP，尝试重新获取')


@retry(stop_max_attempt_number=5)
def pppoe(ssh_cli, cmd):
    # 拨号程序
    print('重新拨号中...')
    stdin, stdout, stderr = ssh_cli.exec_command(f'{cmd[0]} && sleep 3 && {cmd[1]}')
    if stderr.readlines():
        raise Exception('拨号出现问题！')
    else:
        return get_proxy_ip(ssh_cli)


def set_sh_config():
    # 修改squid.sh中的代理账户配置，便于执行
    with open(SQUID_SH, 'r', encoding='utf-8') as f:
        m = re.findall('(squid_proxy_.*?)=(.*?)\s', f.read())
        for key, values in dict(m).items():
            # print(key, values)
            if key[12:] == "user":
                os.system(f'sed -i "s/{key}={values}/{key}={PROXY_USER}/g" {SQUID_SH}')
            elif key[12:] == "passwd":
                os.system(f'sed -i "s/{key}={values}/{key}={PROXY_PASSWORD}/g" {SQUID_SH}')
            elif key[12:] == "port":
                os.system(f'sed -i "s/{key}={values}/{key}={PROXY_PORT}/g" {SQUID_SH}')
    return True


def clean_sys(ssh_cli):
    # 清理系统为重装做准备
    # TODO：重装的包括adsl软件，未完成！
    try:
        _stdin, _stdout, _stderr = ssh_cli.exec_command('/root/squid.sh uninstall')
        if _stderr.readlines():
            raise Exception('/root/squid.sh脚本不存在！')
    except Exception:
        # 脚本不存在会报异常，上传后再执行
        with ssh_cli.open_sftp() as sftp:
            set_sh_config()  # 上传文件前要更新脚本的配置信息
            sftp.put(SQUID_SH, '/root/squid.sh')
        ssh_cli.exec_command('chmod +x /root/squid.sh && /root/squid.sh uninstall')


def check_host(ssh_cli):
    # exec_command执行命令，正常执行stdout有数据返回；异常时是空列表。stderr可以输出错误信息；同理，正常执行错误信息为空列表。
    # 检查主机是否有安装squid，并安装好
    stdin, stdout, stderr = ssh_cli.exec_command('squid -v|grep Version')
    if stdout.readlines():
        try:
            print("重启squid ！")
            # squid是正常的，重启防假死、程序已崩溃
            _stdin, _stdout, _stderr = ssh_cli.exec_command('/root/squid.sh restart')
            if _stderr.readlines():
                raise Exception('/root/squid.sh脚本不存在！')
        except Exception:
            # 脚本不存在
            with ssh_cli.open_sftp() as sftp:
                set_sh_config()  # 上传文件前要更新脚本的配置信息
                sftp.put(SQUID_SH, '/root/squid.sh')
            ssh_cli.exec_command('chmod +x /root/squid.sh && /root/squid.sh restart')
    else:
        # 系统中没有安装squid，尝试安装。
        print('安装squid！')
        try:
            _stdin, _stdout, _stderr = ssh_cli.exec_command('/root/squid.sh install')
            if _stderr.readlines():
                raise Exception('/root/squid.sh脚本不存在！')
        except Exception:
            # 脚本不存在，上传后再执行
            with ssh_cli.open_sftp() as sftp:
                set_sh_config()  # 上传文件前要更新脚本的配置信息
                sftp.put(SQUID_SH, '/root/squid.sh')
            c_stdin, c_stdout, c_stderr = ssh_cli.exec_command('chmod +x /root/squid.sh && /root/squid.sh install')
            # print(c_stdout.readlines())


def run_task(key, values):
    # print(threading.currentThread().getName())
    print('初始化主机：', key)
    with paramiko.SSHClient() as ssh_cli:
        ssh_cli.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            ssh_cli.connect(hostname=values['host'], username=values['username'],
                            password=values['password'],
                            port=values['port'])
        except paramiko.ssh_exception.NoValidConnectionsError as e:
            logger.error(f'主机：{key}，配置有问题，请手动修复并重启程序! {e}')
            values['problem'] = 'init_error'
            RedisClient(list_key='badhosts').set(key, json.dumps(values))
            return False
        # 检查squid
        check_host(ssh_cli)
        # 开始拨号
        proxy_ip = pppoe(ssh_cli, values['cmd'])
        # 存储到Redis
        RedisClient(list_key='adslproxy').set(key, f'{proxy_ip}:{PROXY_PORT}')
        RedisClient(list_key='goodhosts').set(key, json.dumps(values))



def hosts_init():
    # 清空Redis中的数据
    RedisClient(list_key='adslproxy').delete()
    RedisClient(list_key='goodhosts').delete()
    RedisClient(list_key='badhosts').delete()
    # 一启动先拨号一次号，保存所有主机的代理IP
    # 主机管理(启动程序时会检查并配置所有主机)
    thread_list = []
    for _group in HOSTS_GROUP:
        host_list = HOSTS_GROUP.get(_group)
        for key, values in host_list.items():
            # run_task(key, values)
            t = threading.Thread(target=run_task, args=(key, values))
            thread_list.append(t)
    # 开始执行任务
    for t in thread_list:
        t.start()

    for t in thread_list:
        # 阻塞线程，等待子线程执行完毕。
        t.join()


if __name__ == '__main__':
    # 启动时只执行一次
    hosts_init()
