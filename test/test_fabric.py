#!/usr/bin/env python3
# -*-coding:utf-8-*-
# @Autuor : LeoLan  mail：842632422@qq.com
# @Version: Python 3
#

from fabric import Connection

def main():
    c = Connection("root@127.0.0.1", port=44, connect_kwargs={"password": "lanlan"})

    with c.cd('/root'):
        c.put('123.sh')
        c.run("./123.sh")


# fabric.colors.blue(text, bold=False)
# fabric.colors.cyan(text, bold=False)
# fabric.colors.green(text, bold=False)
# fabric.colors.magenta(text, bold=False)
# fabric.colors.red(text, bold=False)
# fabric.colors.white(text, bold=False)
# fabric.colors.yellow(text, bold=False)


if __name__ == '__main__':
    main()
