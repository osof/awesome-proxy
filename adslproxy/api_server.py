#!/usr/bin/env python3
# -*-coding:utf-8-*-
# @Version: Python 3
# API接口服务(每次启动程序都执行本脚本，一直执行)


import os
import sys

# 无效果
# import pathlib
# ROOT_DIR = pathlib.Path.cwd().parent
# sys.path.append(ROOT_DIR)
# sys.path.append(ROOT_DIR / 'adslproxy')
# sys.path.append(ROOT_DIR / 'config')

# 获取当前文件的上级目录(项目根目录)
WORK_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(WORK_DIR)
sys.path.append(os.path.join(WORK_DIR, 'adslproxy'))
sys.path.append(os.path.join(WORK_DIR, 'config'))

import time
import wrapt
from adslproxy.db import RedisClient
from config.api_config import *
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import SignatureExpired, BadSignature, BadData
from flask import Flask, jsonify, request, abort, url_for

app = Flask(__name__)
redis_cli = RedisClient(list_key='adslproxy')


#############################################################


def genTokenSeq(user):
    """
    # 生成token
    :param user: 输入用户名
    :return: 两个token
    """
    access_token_gen = Serializer(secret_key=SECRET_KEY, salt=SALT, expires_in=ACCESS_TOKEN_EXPIRES)
    refresh_token_gen = Serializer(secret_key=SECRET_KEY, salt=SALT, expires_in=REFRESH_TOKEN_EXPIRES)
    timestamp = time.time()
    access_token = access_token_gen.dumps({
        "userid": user,
        "iat": timestamp
    })
    refresh_token = refresh_token_gen.dumps({
        "userid": user,
        "iat": timestamp
    })

    data = {
        "access_token": str(access_token, 'utf-8'),
        "access_token_expire_in": ACCESS_TOKEN_EXPIRES,
        "refresh_token": str(refresh_token, 'utf-8'),
        "refresh_token_expire_in": REFRESH_TOKEN_EXPIRES,
    }
    return data


def validateToken(token):
    """
    # 解析token
    :param token: 输入toke
    :return: 解析结果
    """
    s = Serializer(secret_key=SECRET_KEY, salt=SALT)
    try:
        data = s.loads(token)
    except SignatureExpired:
        return {'code': 401, 'message': 'toekn expired'}  # token过期
    except BadSignature as e:
        encoded_payload = e.payload
        if encoded_payload is not None:
            try:
                s.load_payload(encoded_payload)
            except BadData:
                return {'code': 401, 'message': 'token tampered'}  # token篡改
        return {'code': 401, 'message': 'badSignature of token'}  # 签名有误
    except Exception:
        return {'code': 401, 'message': 'wrong token with unknown reason'}  # 令牌错误
    if 'userid' not in data:
        return {'code': 401, 'message': 'illegal payload inside'}  # 非法载荷
    return {'code': 200, 'userid': data['userid'], 'message': f"user({data['userid']}) logged in by token."}


def helper_proxy(proxy):
    proxyMeta = f"http://{PROXY_USER}:{PROXY_PASSWORD}@{proxy}"
    proxy = {
        "http": proxyMeta,
        "https": proxyMeta,
    }
    return proxy


# def check_login(flag=""):
#     """
#     校验token的装饰器
#     """
#     def check(func):
#         def _check_login(*args, **kwargs):
#             json_data = request.get_json()
#             token = json_data.get('token')
#             data = validateToken(token)
#             if data['code'] == 200:
#                 return func()
#             else:
#                 return jsonify({"status": "403", 'error': 'Unauthorized access'})
#         return _check_login
#     return check


def check_login2(flag=""):
    """
    校验token的装饰器2
    """

    @wrapt.decorator
    def check(wrapped, instance, args, kwargs):
        # 参数含义：
        #
        # - wrapped：被装饰的函数或类方法
        # - instance：
        #   - 如果被装饰者为普通类方法，该值为类实例
        #   - 如果被装饰者为 classmethod 类方法，该值为类
        #   - 如果被装饰者为类/函数/静态方法，该值为 None
        # - args：调用时的位置参数（注意没有 * 符号）
        # - kwargs：调用时的关键字参数（注意没有 ** 符号）
        json_data = request.get_json()
        token = json_data.get('token')
        data = validateToken(token)
        if data['code'] == 200:
            return wrapped()
        else:
            return jsonify({"status": "403", 'error': 'Unauthorized access'})

    return check


@app.route('/api/v1/login', methods=['POST'])
def login():
    """
    客户端发送json过来
    {
        "username":"admin",
        "password":"12345678"
    }
    """
    if request.headers['Content-Type'] != 'application/json':
        return jsonify({"status": "400", 'error': '请使用 Json 格式传递用户名和密码'}), 500
    json_data = request.get_json()
    username = json_data.get('username')
    password = json_data.get('password')
    if username is None or password is None:
        abort(400)
    # 这里校验账户是否合法，我这里用来redis简单对比；关系型数据库需要自行修改。
    # 这里使用了redis做AB数据集切换（账户密码是定时从配置文件读取并更新的），redis方法是自己封装的。
    list_key = RedisClient(list_key='ab_set').get('a_or_b')
    if RedisClient(list_key=list_key).get(username) == password:
        token = genTokenSeq(username)
        return jsonify(token)
    else:
        return jsonify({"status": "500", 'error': '请传递配置文件中正确的用户名和密码'}), 500
        # abort(400)


# 说明：url后面没有加“/”,用了装饰器之后函数名会被替换，用endpoint来区分。
@app.route('/', methods=['GET'], endpoint='index')
def index():
    # 查看API列表
    api_url = {}
    for api in app.url_map._rules_by_endpoint.keys():
        if api != 'static':
            api_url[api] = url_for(api, _external=True)
    return jsonify(api_url)


@app.route('/api/v1/random', methods=['POST'], endpoint='random')
@check_login2()
def random():
    # 随机获取一个代理的值
    proxy = redis_cli.random()
    if proxy:
        proxy = helper_proxy(proxy)
        return jsonify(proxy), 200
    else:
        return jsonify({"status": "500", 'error': 'No proxy available'}), 500


@app.route('/api/v1/proxies', methods=['POST'], endpoint='proxies')
@check_login2()
def get_proxies():
    # 获取一个随机代理的详细信息
    proxy_name = ''
    proxies = {}
    json_data = request.get_json()
    if json_data:
        proxy_name = json_data.get('proxy_name')
    if proxy_name:
        proxy = redis_cli.get(proxy_name)
        if proxy:
            proxies['status'] = "200"
            proxies['name'] = proxy_name
            proxies['proxy'] = helper_proxy(proxy)
            return jsonify(proxies), 200
    else:
        return jsonify({"status": "500", 'error': '找不到代理！'}), 500


@app.route('/api/v1/all', methods=['POST'], endpoint='all')
@check_login2()
def get_all():
    # 获取所有代理
    result = redis_cli.all()
    if result:
        proxy_list = [{'http': helper_proxy(values)} for values in result.values()]
        return jsonify({"data": proxy_list}), 200
    else:
        return jsonify({"status": "500", 'error': 'No proxy available'}), 500


@app.route('/api/v1/counts', methods=['POST'], endpoint='counts')
@check_login2()
def get_counts():
    count = redis_cli.count()
    return jsonify({"status": "200", "counts": count}), 200


@app.route('/api/v1/names', methods=['POST'], endpoint='names')
@check_login2()
def get_names():
    names = redis_cli.names()
    if names:
        return jsonify({"data": names}), 200
    else:
        return jsonify({"status": "500", 'error': 'No proxy available'}), 500


@app.route('/api/v1/delete', methods=['POST'], endpoint='delete')
@check_login2()
def delete():
    proxy_name = ''
    json_data = request.get_json()
    if json_data:
        proxy_name = json_data.get('proxy_name')
    if not proxy_name:
        return jsonify({"status": "500", 'delete': '请输入代理机器名称'}), 400
    try:
        result = redis_cli.remove(proxy_name)
    except Exception:
        return jsonify({"status": "500", 'delete': '删除失败，该代理不存在！'}), 400
    if result:
        return jsonify({"status": "200", 'delete': 'Success'}), 200
    else:
        return jsonify({"status": "500", 'delete': 'Fail'}), 400


if __name__ == '__main__':
    # 启动接口
    app.run(host=API_HOST, port=API_PORT, debug=False)
    # gunicorn方式启动
    # os.system(f'gunicorn -w 4 -b {API_HOST}:{API_PORT} -k gevent api_server:app')
