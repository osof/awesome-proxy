#!/usr/bin/env python3
# -*-coding:utf-8-*-
# @Autuor : LeoLan  mail：842632422@qq.com
# @Version: Python 3
#

import time
from config.api_config import USER, SECRET_KEY
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import SignatureExpired, BadSignature, BadData

from flask_login import LoginManager, UserMixin
from flask import Flask, jsonify, request, abort
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY

SQLALCHEMY_DATABASE_URI = "sqlite:////user_info.db"

login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'login'
login_manager.init_app(app)


db = SQLAlchemy(app)


class Users(UserMixin, db.Model):
    # 定义数据库结构
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))

    @staticmethod
    def init_user():
        # 先删除所有表
        db.drop_all()
        # 创建表
        db.create_all()
        # 写入用户账户信息
        print('创建用户')
        for group in USER:
            for user_info in USER[group].values():
                _user = Users()
                _user.user_id = time.time()
                _user.username = user_info['username']
                _user.password = user_info['password']
                db.session.add(_user)
                db.session.commit()

    @property
    def password(self):
        raise AttributeError('password is not readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)




#############################################################
secret_key = 'hardtoguess'
salt = 'hardtoguess'
access_token_expires_in = 1800
refresh_token_expires_in = 86400


def genTokenSeq(user):
    # 生成token
    u = Users.query.filter_by(username=user).first()
    if u:
        userid = u.id
    else:
        return {'code': 422, 'message': '用户不存在'}
    access_token_gen = Serializer(secret_key=secret_key, salt=salt, expires_in=access_token_expires_in)
    refresh_token_gen = Serializer(secret_key=secret_key, salt=salt, expires_in=refresh_token_expires_in)
    timtstamp = time.time()
    access_token = access_token_gen.dumps({
        "userid": userid,
        "iat": timtstamp
    })
    refresh_token = refresh_token_gen.dumps({
        "userid": userid,
        "iat": timtstamp
    })

    data = {
        "access_token": str(access_token, 'utf-8'),
        "access_token_expire_in": access_token_expires_in,
        "refresh_token": str(refresh_token, 'utf-8'),
        "refresh_token_expire_in": refresh_token_expires_in,
    }
    return data


def validateToken(token):
    # 解析token
    s = Serializer(secret_key=secret_key, salt=salt)
    try:
        data = s.loads(token)
    except SignatureExpired:
        msg = 'toekn expired'
        return {'code': 401, 'error_code': 'auth_01', 'message': msg}
    except BadSignature as e:
        encoded_payload = e.payload
        if encoded_payload is not None:
            try:
                s.load_payload(encoded_payload)
            except BadData:
                msg = 'token tampered'
                return {'code': 401, 'error_code': 'auth_02', 'message': msg}
        msg = 'badSignature of token'
        return {'code': 401, 'error_code': 'auth_03', 'message': msg}
    except:
        msg = 'wrong token with unknown reason'
        return {'code': 401, 'error_code': 'auth_04', 'message': msg}

    if 'userid' not in data:
        msg = 'illegal payload inside'
        return {'code': 401, 'error_code': 'auth_05', 'message': msg}
    msg = 'user(' + str(data['userid']) + ') logged in by token.'
    userId = data['userid']
    return {'code': 200, 'error_code': 'auth_00', 'message': msg, 'userid': userId}



###############################################################
# API


@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))


@app.route('/login', methods=['POST'])
def login():
    json_data = request.get_json()
    print('&&&&&&&&&&&&&&&&&&&', json_data)
    username = json_data.get('username')
    password = json_data.get('password')
    if username is None or password is None:
        abort(400)  # missing arguments
    if Users.query.filter_by(username=username).first() is not None:
        abort(400)  # existing user

    print('开始查询用户')
    user = Users.query.filter_by(username=username).first()
    print('查询到用户信息', user)
    return genTokenSeq(user)



@app.route('/', methods=['POST'])
def index():
    json_data = request.get_json()
    print(json_data)
    token = ''
    if json_data:
        token = json_data.get('token')
        print("获取到的token", token)
    else:
        abort(400)
    if token:
        data = validateToken(token)
        return data, 200
    else:
        abort(400)


if __name__ == '__main__':
    Users.init_user()
    #app.run(host='0.0.0.0', port=5000, debug=True)

