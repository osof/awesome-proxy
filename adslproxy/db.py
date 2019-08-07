#!/usr/bin/env python3
# -*-coding:utf-8-*-
# @Version: Python 3
# 数据库函数

import redis
import random
from config.api_config import *


class RedisClient(object):
    def __init__(self, host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD, list_key='adslproxy'):
        """
        初始化Redis连接proxy_key=PROXY_KEY
        :param host: Redis 地址
        :param port: Redis 端口
        :param password: Redis 密码
        :param proxy_key: Redis 哈希表名
        """
        self.db = redis.StrictRedis(host=host, port=port, password=password, decode_responses=True)
        self.list_key = list_key

    def set(self, name, proxy):
        """
        设置代理
        :param name: 主机名称
        :param proxy: 代理
        :return: 设置结果
        """
        return self.db.hset(self.list_key, name, proxy)

    def get(self, name):
        """
        获取代理
        :param name: 主机名称
        :return: 代理
        """
        return self.db.hget(self.list_key, name)

    def count(self):
        """
        获取代理总数
        :return: 代理总数
        """
        return self.db.hlen(self.list_key)

    def remove(self, name):
        """
        删除代理
        :param name: 主机名称
        :return: 删除结果
        """
        return self.db.hdel(self.list_key, name)

    def delete(self):
        """
        删除代理池
        :return: None
        """
        return self.db.delete(self.list_key)

    def names(self):
        """
        获取主机名称列表
        :return: 获取主机名称列表
        """
        return self.db.hkeys(self.list_key)

    def proxies(self):
        """
        获取代理列表
        :return: 代理列表
        """
        return self.db.hvals(self.list_key)

    def random(self):
        """
        随机获取代理
        :return:
        """
        proxies = self.proxies()
        if proxies:
            return random.choice(proxies)

    def all(self):
        """
        获取字典
        :return:
        """
        return self.db.hgetall(self.list_key)

    def random_info(self):
        """
        随机获取代理的详细信息
        :return:
        """
        get_name = self.names()
        if get_name:
            name = random.choice(get_name)
            proxy = self.get(name)
            return [name, proxy]
        # 测试返回
        # return ['', '']
