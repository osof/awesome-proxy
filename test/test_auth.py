# -*-coding:utf8-*-
# @Time   : 2019/8/4
# @Autuor : LeoLan  mail：842632422@qq.com
# @Version: Python 3
#


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
db = SQLAlchemy(app)
auth = HTTPBasicAuth()


db.create_all() #创建表




class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), index=True)
    password = db.Column(db.String(128))

    # 密码加密
    def hash_password(self, password):
        self.password = custom_app_context.encrypt(password)

    # 密码解析
    def verify_password(self, password):
        return custom_app_context.verify(password, self.password)

    # 获取token，有效时间10min
    def generate_auth_token(self, expiration=600):
        s = Serializer(SECRET_KEY, expires_in=expiration)
        return s.dumps({'id': self.id})

    # 解析token，确认登录的用户身份
    @staticmethod
    def verify_auth_token(token):
        s = Serializer(SECRET_KEY)
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None  # valid   token, but expired
        except BadSignature:
            return None  # invalid token
        user = User.query.get(data['id'])
        return user





@app.route('/api/register', methods=['POST'])
def new_user():
    # 注册用户
    json_data = request.get_json()
    print(json_data)
    username = json_data['username']
    password = json_data['password']
    if username is None or password is None:
        abort(400)  # missing arguments
    if User.query.filter_by(username=username).first() is not None:
        abort(400)  # existing user
    user = User(username=username)
    user.hash_password(password)
    db.session.add(user)
    db.session.commit()
    return jsonify({'username': user.username})


@app.route('/api/login', methods=['POST'])
#@auth.login_required
def get_auth_token():
    json_data = request.get_json()
    print(json_data)
    username = json_data['username']
    password = json_data['password']
    print(username, password, '@@@@@@@@@@@@@@@')
    obj = User.query.filter_by(username=username).first()
    if not obj:
        return jsonify(201, '', '未找到该用户')
    if obj.verify_password(password):
        token = g.user.generate_auth_token()
        token = str(token, encoding='utf8')
        return jsonify(200, {'token': token}, '登录成功')
    else:
        return jsonify(201, '', '密码错误')


@auth.verify_password
def verify_password(username_or_token, password):
    # 需要json传过来
    if request.path == "/api/login":
        username_and_password = request.get_json()
        print('###############', username_and_password)
        if username_and_password.get('username') is not None:
            username_or_token = username_and_password['username']
        if username_and_password.get('password') is not None:
            password = username_and_password['password']

        user = User.query.filter_by(username=username_or_token).first()
        if not user or not user.verify_password(password):
            return False
    else:
        # 传过来的是token
        user = User.verify_auth_token(username_or_token)
        if not user:
            return False
    g.user = user
    return True





# @app.route('/api/test', methods=['GET', 'POST'])
# def test():
#     b = request.get_json()
#     print(b)
#     return "test"


app.run(debug=True)

