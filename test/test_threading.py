#!/usr/bin/env python3
# -*-coding:utf-8-*-
# @Version: Python 3
#

import time
import threading


# https://www.cnblogs.com/cnkai/p/7504980.html

def run():
    time.sleep(2)
    print('当前线程的名字是： ', threading.current_thread().name)
    time.sleep(3)
    t = threading.Thread(target=run)
    t.start()



def task():
    # time.sleep(1)
    print('任务二')
    # time.sleep(2)


if __name__ == '__main__':
    start_time = time.time()

    print('这是主线程：', threading.current_thread().name)
    thread_list = []
    for i in range(5):
        t = threading.Thread(target=run)
        thread_list.append(t)

    for t in thread_list:
        t.start()

    for t in thread_list:
        t.join()

    print('主线程结束！', threading.current_thread().name)
    print('一共用时：', time.time() - start_time)
