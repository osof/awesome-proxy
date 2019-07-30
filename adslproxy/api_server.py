#!/usr/bin/env python3
# -*-coding:utf-8-*-
# @Version: Python 3
# API接口服务

# TODO：这里用Flask写接口服务
# coding=utf-8
import sys
from flask import Flask
from flask import jsonify
from flask import request

sys.path.append('../')

from config.api_config import *
from adslproxy.db import RedisClient

app = Flask(__name__)
rd = RedisClient()

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
        html += f'<span>{key}: <a href={key}>{values}</a></span><br><br>'
    return html, 200


@app.route('/random/')
def random():
    proxy = rd.random()
    if proxy:
        return proxy, 200
    else:
        return 'redis no proxy', 400


@app.route('/proxies/')
def get_proxies():
    proxies = rd.proxies()
    if proxies:
        return jsonify(proxies), 200
    else:
        return 'redis no proxy', 400


@app.route('/delete/', methods=['GET'])
def delete():
    adsl_client_name = request.args.get('adsl_name')
    if not adsl_client_name:
        return '请输入正确的 adsl name'
    result = rd.remove(adsl_client_name)
    if result:
        return 'success', 200
    else:
        return 'delete error', 400


@app.route('/counts/')
def get_counts():
    count = rd.count()
    if count:
        return jsonify(count), 200
    else:
        return 'no adsl client', 400


@app.route('/names/')
def get_names():
    names = rd.names()
    if names:
        return jsonify(names), 200
    else:
        return 'no names', 400


@app.route('/all/')
def get_all():
    result = rd.all()
    if result:
        return jsonify(result), 200
    else:
        return 'no adsl', 400


def run():
    app.run(host=API_HOST, port=API_PORT, debug=True)


if __name__ == '__main__':
    run()

