#!/usr/bin/env python3
# -*-coding:utf-8-*-
# @Version: Python 3
# 执行初始化、拨号等任务


# TODO：拨号，服务器初始化


from config.hosts import *
from fabric import Connection
from adslproxy.db import RedisClient

redis_cli = RedisClient()


def check_host(ssh_cli):
    # redis_cli.get(nickname)
    s = ssh_cli.run('ps -ef |grep squid|wc -l')
    print(type(s), s)
    # ssh_cli.put('123.sh')
    # ssh_cli.run("./123.sh")
    return True


from fabric.group import Group, SerialGroup


def task_main():
    for _group in HOSTS_GROUP:
        host_list = HOSTS_GROUP.get(_group)
        for key, values in host_list.items():
            # print(key, values)
            ssh_cli = Connection(f"{values['username']}@{values['host']}", port=values['port'],
                                 connect_kwargs={"password": values['password']})
            with ssh_cli.cd('/root'):
                check_host(ssh_cli)


if __name__ == '__main__':
    task_main()
