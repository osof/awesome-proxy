#!/usr/bin/env python3
# -*-coding:utf-8-*-
# @Version: Python 3
# 执行初始化、拨号等任务


# TODO：拨号，服务器初始化

import os
from config.hosts import *
from fabric import Connection
from adslproxy.db import RedisClient

redis_cli = RedisClient()


def check_host(ssh_cli):
    # redis_cli.get(nickname)
    try:
        ssh_cli.run('squid -v|grep Version')
        # squid是正常的，重启防假死、程序已崩溃
        ssh_cli.run('/usr/sbin/service squid restart')
        print('重启成功')
    except Exception:
        # 系统中没有安装squid
        ssh_cli.put('../script-sh/squid.sh') # 覆盖目标文件
        ssh_cli.run('chmod +x squid.sh && ./squid.sh')







def task_main():
    for _group in HOSTS_GROUP:
        host_list = HOSTS_GROUP.get(_group)
        for key, values in host_list.items():
            # print(key, values)
            ssh_cli = Connection(f"{values['username']}@{values['host']}", port=values['port'],
                                 connect_kwargs={"password": values['password']})
            with ssh_cli.cd('/root'):
                check_host(ssh_cli)
                # 获取外网地址
                proxy_ip = ssh_cli.run('curl http://members.3322.org/dyndns/getip')
                print(proxy_ip)



# from fabric.group import Group, SerialGroup
# def task2():
#     task_list = []
#     for _group in HOSTS_GROUP:
#         host_list = HOSTS_GROUP.get(_group)
#         for key, values in host_list.items():
#             # print(key, values)
#             key = Connection(f"{values['username']}@{values['host']}", port=values['port'],
#                                  connect_kwargs={"password": values['password']})
#             task_list.append(key)
#     print("task_list", task_list)
#     group = SerialGroup(task_list)
#     results = group.run("pwd")
#     print(results)



if __name__ == '__main__':
    task_main()
    # task2()
    # import sys
    # os.system('cat ../script-sh/squid.sh')
    # print(f'{os.getcwd()}/../script-sh')