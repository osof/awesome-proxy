import requests
from json import JSONDecodeError


def get_data_from_post(url, data):
    """

    :param url: api
    :param data: dict
    :return: dict
    """
    response = requests.post(url, json=data, timeout=10)
    if response.status_code == 200:
        response_text = response.json()
        return response_text
    else:
        try:
            print(response.json())
            return None
        except JSONDecodeError:
            raise TypeError(f'json 解析错误，可能 {url} 不是 api 列表中的 url')


test_url = 'http://www.baidu.com'
host_url = 'http://192.168.2.21:8080'

# 获取 token
user_info = {
    "username": "admin",
    "password": "12345678",
}
token_url = f'{host_url}/api/v1/login'
token_dict = get_data_from_post(token_url, user_info)
token = token_dict.get('access_token')

# 向接口提交 token，验证权限，获取的数据类似{'http': proxy_url, 'https': proxy_url}
data = {'token': token}
random_proxy_url = f'{host_url}/api/v1/random'
random_proxy = get_data_from_post(random_proxy_url, data)

resp = requests.get(url=test_url, proxies=random_proxy, timeout=10)
if resp.status_code == 200:
    print(resp.text)
