# -*-coding:utf8-*-
# @Time   : 2019/8/4
# @Autuor : LeoLan  mail：842632422@qq.com
# @Version: Python 3
#

import time
import base64
import hmac
from passlib.apps import custom_app_context as pwd_context

SQLALCHEMY_DATABASE_URI = "sqlite:////user_info.db"

# 安全配置
CSRF_ENABLED = True

from config.api_config import *
from passlib.apps import custom_app_context
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, SignatureExpired, BadSignature
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_httpauth import HTTPBasicAuth
from flask_cors import CORS
from flask import jsonify, request, abort, g

app = Flask(__name__)
# flask的跨域解决
CORS(app, supports_credentials=True)
# 可以获取config.py的内容
db = SQLAlchemy(app)
auth = HTTPBasicAuth()


class User(db.Model):
    __tablename__ = 'users_info'
    username = db.Column(db.BigInteger, primary_key=True)  # 手机号
    password = db.Column(db.Text, nullable=False)

    def hash_password(self, password):  # 给密码加密方法
        self.password = pwd_context.encrypt(password)

    def verify_password(self, password):  # 验证密码方法
        return pwd_context.verify(password, self.password)


@app.route('/api/register', methods=['POST'])
def register():
    username = request.form.get('username')
    password = request.form.get('password')
    if username is None or password is None:
        abort(400)  # missing arguments
    if User.query.filter_by(username=username).first() is not None:
        abort(400)  # existing user
    user = User(username=username)
    user.hash_password(password)  # 调用密码加密方法
    db.session.add(user)
    db.session.commit()
    return 'success'


@app.route('/api/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    obj = User.query.filter_by(userName=username).first()
    if not obj:
        return jsonify(201, '', '未找到该用户')
    if obj.verify_password(password):
        token = generate_token(username)
        return jsonify(200, {'token': token}, '登录成功')
    else:
        return jsonify(201, '', '密码错误')


def generate_token(key, expire=3600):
    ts_str = str(time.time() + expire)
    ts_byte = ts_str.encode("utf-8")
    sha1_tshexstr = hmac.new(key.encode("utf-8"), ts_byte, 'sha1').hexdigest()
    token = ts_str + ':' + sha1_tshexstr
    b64_token = base64.urlsafe_b64encode(token.encode("utf-8"))
    return b64_token.decode("utf-8")


# 验证token 入参：用户id 和 token
def certify_token(key, token):
    token_str = base64.urlsafe_b64decode(token).decode('utf-8')
    token_list = token_str.split(':')
    if len(token_list) != 2:
        return False
    ts_str = token_list[0]
    if float(ts_str) < time.time():
        # token expired
        return False
    known_sha1_tsstr = token_list[1]
    sha1 = hmac.new(key.encode("utf-8"), ts_str.encode('utf-8'), 'sha1')
    calc_sha1_tsstr = sha1.hexdigest()
    if calc_sha1_tsstr != known_sha1_tsstr:
        # token certification failed
        return False
    # token certification success
    return True



app.run(debug=True)