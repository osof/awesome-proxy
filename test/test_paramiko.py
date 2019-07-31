# -*-coding:utf8-*-
# @Time   : 2019/7/29
# @Autuor : LeoLan  mail：842632422@qq.com
# @Version: Python 3
#


import paramiko
from config.hosts import *

"""
参考资料：
https://zhuanlan.zhihu.com/p/25031447
https://blog.csdn.net/a_gorilla/article/details/82151541

https://www.fabfile.org/installing.html
"""


def depoly_monitor(host_info):
    with paramiko.SSHClient() as client:
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        #print(host_info['password'])
        client.connect(hostname=host_info['host'], username=host_info['username'], password=host_info['password'],
                       port=host_info['port'])

        # stdin, stdout, stderr = client.exec_command('ls -l')
        # print(stdout.readlines())

        # with client.open_sftp() as sftp:
        #     sftp.put('123.sh', '123.sh')
        #     sftp.chmod('123.sh', 0o755)

        stdin, stdout, stderr = client.exec_command('curl http://members.3322.org/dyndns/getip')
        print(stdout.readlines())


def main():
    for i in HOSTS_GROUP['group1'].values():
        print(type(i), i)
        depoly_monitor(i)


if __name__ == '__main__':
    main()
