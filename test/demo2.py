import requests

# 获取Token（返回的token 默认5小时有效）
# 代理池地址（Docker部署的服务器）
api_url = 'http://192.168.2.21:8080'


def get_token():
    # 获取Token（返回的token 默认5小时有效）
    url = f'{api_url}/api/v1/login'
    # 修改为自己的账户信息
    user_info = {"username": "admin", "password": "12345678"}
    token = requests.post(url=url, json=user_info).json().get('access_token')
    if token:
        return {"token": token}
    return None


if __name__ == '__main__':
    token = get_token()  # token是长时间有效的，获取一次就好。
    if token:
        # 获取一个随机代理
        random_proxy = requests.post(url=f'{api_url}/api/v1/random', json=get_token()).json()
        if 'http' in random_proxy.keys():
            # 代理正常返回
            resp = requests.get(url='https://www.baidu.com', proxies=random_proxy, timeout=10)
            print(resp.text)
