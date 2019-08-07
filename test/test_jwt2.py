#!/usr/bin/env python3
# -*-coding:utf-8-*-
# @Autuor : LeoLan  mail：842632422@qq.com
# @Version: Python 3
# Flask JWT 验证

import time
from adslproxy.db import RedisClient
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import SignatureExpired, BadSignature, BadData
from flask import Flask, jsonify, request, abort

app = Flask(__name__)

# 用于存储已经保存的账户信息
redis_cli = RedisClient()

#############################################################
secret_key = 'PMF9IAnk16KVbUel'
salt = 'jR9kK3KjYDN79t6s'
access_token_expires_in = 60 * 60 * 5
refresh_token_expires_in = 60 * 60 * 6


def genTokenSeq(user):
    """
    # 生成token
    :param user: 输入用户名
    :return: 两个token
    """
    access_token_gen = Serializer(secret_key=secret_key, salt=salt, expires_in=access_token_expires_in)
    refresh_token_gen = Serializer(secret_key=secret_key, salt=salt, expires_in=refresh_token_expires_in)
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
        "access_token_expire_in": access_token_expires_in,
        "refresh_token": str(refresh_token, 'utf-8'),
        "refresh_token_expire_in": refresh_token_expires_in,
    }
    return data


def validateToken(token):
    """
    # 解析token
    :param token: 输入toke
    :return: 解析结果
    """
    s = Serializer(secret_key=secret_key, salt=salt)
    try:
        data = s.loads(token)
    except SignatureExpired:
        return jsonify({'code': 401, 'message': 'toekn expired'})  # token过期
    except BadSignature as e:
        encoded_payload = e.payload
        if encoded_payload is not None:
            try:
                s.load_payload(encoded_payload)
            except BadData:
                return jsonify({'code': 401, 'message': 'token tampered'})  # token篡改
        return jsonify({'code': 401, 'message': 'badSignature of token'})  # 签名有误
    except Exception:
        return jsonify({'code': 401, 'message': 'wrong token with unknown reason'})  # 令牌错误

    if 'userid' not in data:
        return jsonify({'code': 401, 'message': 'illegal payload inside'})  # 非法载荷
    return jsonify({'code': 200, 'userid': data['userid'], 'message': f"user({data['userid']}) logged in by token."})


###############################################################
# API
@app.route('/login', methods=['POST'])
def login():
    """
    客户端发送json过来
    {
        "username":"admin",
        "password":"12345678"
    }
    """
    json_data = request.get_json()
    username = json_data.get('username')
    password = json_data.get('password')
    if username is None or password is None:
        abort(400)
    # 这里校验账户是否合法，我这里用来redis简单对比；关系型数据库需要自行修改。
    # 这里使用了redis做AB数据集切换（账户密码是定时从配置文件读取并更新的），redis方法是自己封装的。
    list_key = RedisClient(list_key='ab_set').get('a_or_b')
    if RedisClient(list_key=list_key).get(username) == password:
        return genTokenSeq(username)
    else:
        abort(400)


@app.route('/', methods=['POST'])
def index():
    """
    客户端发送json过来
    {
        "token":"token-str",
    }
    """
    json_data = request.get_json()
    print(json_data)
    token = ''
    if json_data:
        token = json_data.get('token')
    else:
        abort(400)
    if token:
        data = validateToken(token)
        return data, 200
    else:
        abort(400)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
