import requests
from json import JSONDecodeError

test_url = 'http://www.baidu.com'
host_url = 'http://192.168.2.21:8080'


def get_data_from_post(url, data):
    response = requests.post(url, json=data, timeout=10)
    if response.status_code == 200:
        response_json = resp.json()
        return response_json
    else:
        try:
            print(response.json())
            return None
        except JSONDecodeError:
            raise TypeError(f'json 解析错误，可能 {url} 不是 api 列表中的 url')


# 测试 /
resp = requests.get(host_url)
index = resp.json()
print('index:', index, end='\n\n')

# 测试 /api/v1/login
user_info = {
    "username": "admin",
    "password": "12345678",
}
token_url = f'{host_url}/api/v1/login'
resp_json = get_data_from_post(token_url, user_info)
token = resp_json.get('access_token')
print('token:', token, end='\n\n')

# 测试 /api/v1/random
data = {'token': token}
random_proxy_url = f'{host_url}/api/v1/random'
random_proxy = get_data_from_post(random_proxy_url, data)
print('random_proxy:', random_proxy, end='\n\n')

# 测试 /api/v1/proxies
proxies_data = data.update(proxy_name='myadsl1')
name_proxy_url = f'{host_url}/api/v1/proxies'
name_proxy = get_data_from_post(name_proxy_url, data)
print('name_proxy:', name_proxy, end='\n\n')

# 测试 /api/v1/names
client_names_url = f'{host_url}/api/v1/names'
client_names = get_data_from_post(client_names_url, data)
print('client_names:', client_names, end='\n\n')

# 测试 /api/v1/all
all_proxies_url = f'{host_url}/api/v1/all'
all_proxies = get_data_from_post(all_proxies_url, data)
print('all_proxies:', all_proxies, end='\n\n')

# 测试 /api/v1/delete
delete_data = data.update(proxy_name='myadsl1')
del_proxy_url = f'{host_url}/api/v1/delete'
del_proxy = get_data_from_post(del_proxy_url, data)
print('del_proxy:', del_proxy, end='\n\n')

# proxy = all_proxies['']
#     resp = requests.get(url=test_url, proxies=random_proxy, timeout=10)
#     print(resp.text)
