#!/usr/bin/env python3
# -*-coding:utf-8-*-
# @Version: Python 3
# API接口服务(每次启动程序都执行本脚本，一直执行)

# TODO：账户校验、频率限制未完成
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

from flask import Flask
from flask import jsonify
from flask import request
from config.api_config import *
from adslproxy.db import RedisClient
from flask_httpauth import HTTPBasicAuth
from flask import Flask, abort, request, jsonify, g, url_for, make_response
from passlib.apps import custom_app_context as pwd_context
from flask_sqlalchemy import SQLAlchemy
from itsdangerous import (TimedJSONWebSignatureSerializer as Serializer, BadSignature, SignatureExpired)

app = Flask(__name__)
app.config.update(SQLALCHEMY_TRACK_MODIFICATIONS=False)
auth = HTTPBasicAuth()
db = SQLAlchemy(app)
redis_cli = RedisClient(list_key='adslproxy')


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), index=True)
    password_hash = db.Column(db.String(64))

    def hash_password(self, password):
        self.password_hash = pwd_context.encrypt(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)

    def generate_auth_token(self, expiration=600):
        s = Serializer(SECRET_KEY, expires_in=expiration)
        return s.dumps({'id': self.id})

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(SECRET_KEY)
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None    # valid token, but expired
        except BadSignature:
            return None    # invalid token
        user = User.query.get(data['id'])
        return user

@auth.verify_password
def verify_password(username_or_token, password):
    # first try to authenticate by token
    user = User.verify_auth_token(username_or_token)
    if not user:
        # try to authenticate with username/password
        user = User.query.filter_by(username=username_or_token).first()
        if not user or not user.verify_password(password):
            return False
    g.user = user
    return True


@app.route('/api/token')
@auth.login_required
def get_auth_token():
    token = g.user.generate_auth_token(600)
    return jsonify({'token': token.decode('ascii'), 'duration': 600})

@auth.error_handler
def unauthorized():
    return make_response(jsonify({'error': 'Unauthorized access'}), 403)


if __name__ == '__main__':
    if not os.path.exists('db.sqlite'):
        db.create_all()
    app.run(debug=True)

#
# ##########################################
# api_list = {
#     'random': u'random get an proxy',
#     'proxies': u'get all proxy from proxy pool',
#     'delete': u'delete an unable adsl proxy, like: delete/adsl_name=adsl1',
#     'counts': u'proxy counts',
#     'names': u'all ADSL client name',
#     'all': u'all ADSL client name and proxy'
# }
#
#
# @app.route('/')
# def index():
#     html = ''
#     for key, values in api_list.items():
#         html += f'<a href={key}>{values}</a><br><br>'
#     return html, 200
#
#
# @app.route('/random/')
# def random():
#     proxy = redis_cli.random()
#     if proxy:
#         return proxy, 200
#     else:
#         return 'redis no proxy', 400
#
#
# @app.route('/proxies/')
# def get_proxies():
#     proxies = redis_cli.proxies()
#     if proxies:
#         return jsonify(proxies), 200
#     else:
#         return 'redis no proxy', 400
#
#
# @app.route('/delete/', methods=['GET'])
# def delete():
#     adsl_client_name = request.args.get('adsl_name')
#     if not adsl_client_name:
#         return '请输入正确的 adsl name'
#     result = redis_cli.remove(adsl_client_name)
#     if result:
#         return 'success', 200
#     else:
#         return 'delete error', 400
#
#
# @app.route('/counts/')
# def get_counts():
#     count = redis_cli.count()
#     if count:
#         return jsonify(count), 200
#     else:
#         return 'no adsl client', 400
#
#
# @app.route('/names/')
# def get_names():
#     names = redis_cli.names()
#     if names:
#         return jsonify(names), 200
#     else:
#         return 'no names', 400
#
#
# @app.route('/all/')
# def get_all():
#     result = redis_cli.all()
#     if result:
#         return jsonify(result), 200
#     else:
#         return 'no adsl', 400
#
#
# if __name__ == '__main__':
#     # 启动接口
#     # app.run(host=API_HOST, port=API_PORT, debug=True)
#     # gunicorn方式启动
#     os.system(f'gunicorn -w 4 -b {API_HOST}:{API_PORT} -k gevent api_server:app')
