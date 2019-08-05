# -*-coding:utf8-*-
# @Time   : 2019/8/4
# @Autuor : LeoLan  mail：842632422@qq.com
# @Version: Python 3
#

from adslproxy.api_server import SECRET_KEY
from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth
from flask import make_response, jsonify, g
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from werkzeug.security import generate_password_hash, check_password_hash

SQLALCHEMY_DATABASE_URI = "sqlite:////user_info.db"

# 安全配置
CSRF_ENABLED = True

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_httpauth import HTTPBasicAuth
from flask_cors import CORS
from flask import request, abort

app = Flask(__name__)
# flask的跨域解决
CORS(app, supports_credentials=True)
# 可以获取config.py的内容
db = SQLAlchemy(app)

# 创建Basic Auth类型验证对象
"""TOKEN令牌认证"""
auth = HTTPTokenAuth()
basicAuth = HTTPBasicAuth()


# 验证账号和非明文密码
@basicAuth.verify_password
def verify_password(username, password):
    for user in users:
        if user['username'] == username:
            if check_password_hash(user['password'], password):
                return True
    return False


# 对于非认证用户的错误处理
@basicAuth.error_handler
def unauthorized():
    return make_response(jsonify({'errmsg': 'Invalid user'}), 401)


def generate_auth_token(expiration=36000):
    serializer = Serializer(SECRET_KEY, expires_in=expiration)
    # 生成token写入到redis数据库，类型string
    user = 'D88'
    token = serializer.dumps({'username': user})
    return token


@auth.verify_token
def verify_token(token):
    g.user = None
    serializer = Serializer(SECRET_KEY)
    try:
        data = serializer.loads(token)
    except:
        return False
    if 'username' in data:
        g.user = data['username']
        return True
    return False


# 对于非认证用户的错误处理
@auth.error_handler
def unauthorized():
    return make_response(jsonify({'errmsg': 'Invalid token'}), 401)



app.run(debug=True)