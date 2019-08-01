#!/usr/bin/env python3
# -*-coding:utf-8-*-
# @Version: Python 3
# API接口服务(每次启动程序都执行本脚本，一直执行)


import os
import sys

# 获取当前文件的上级目录(项目根目录)
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(ROOT_DIR)

from flask import Flask
from flask import jsonify
from flask import request
from config.api_config import *
from adslproxy.db import RedisClient

app = Flask(__name__)
redis_cli = RedisClient()

api_list = {
    'random': u'random get an proxy',
    'proxies': u'get all proxy from proxy pool',
    'delete': u'delete an unable adsl proxy, like: delete/adsl_name=adsl1',
    'counts': u'proxy counts',
    'names': u'all adsl client name',
    'all': u'all adsl client name and proxy'
}


@app.route('/')
def index():
    html = ''
    for key, values in api_list.items():
        html += f'<a href={key}>{values}</a><br><br>'
    return html, 200


@app.route('/random/')
def random():
    proxy = redis_cli.random()
    if proxy:
        return proxy, 200
    else:
        return 'redis no proxy', 400


@app.route('/proxies/')
def get_proxies():
    proxies = redis_cli.proxies()
    if proxies:
        return jsonify(proxies), 200
    else:
        return 'redis no proxy', 400


@app.route('/delete/', methods=['GET'])
def delete():
    adsl_client_name = request.args.get('adsl_name')
    if not adsl_client_name:
        return '请输入正确的 adsl name'
    result = redis_cli.remove(adsl_client_name)
    if result:
        return 'success', 200
    else:
        return 'delete error', 400


@app.route('/counts/')
def get_counts():
    count = redis_cli.count()
    if count:
        return jsonify(count), 200
    else:
        return 'no adsl client', 400


@app.route('/names/')
def get_names():
    names = redis_cli.names()
    if names:
        return jsonify(names), 200
    else:
        return 'no names', 400


@app.route('/all/')
def get_all():
    result = redis_cli.all()
    if result:
        return jsonify(result), 200
    else:
        return 'no adsl', 400


if __name__ == '__main__':
    # 启动接口
    # app.run(host=API_HOST, port=API_PORT, debug=True)
    # gunicorn方式启动
    os.system(f'gunicorn -w 4 -b {API_HOST}:{API_PORT} -k gevent api_server:app')