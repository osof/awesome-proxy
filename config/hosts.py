# adsl主机配置文件

# 暂定格式

# ADSL主机列表
# HOSTS_LIST111 = [
#     {
#         "name": 'my_adsl1',
#         "host": '123.456.678.789',
#         "port": 22,
#         "username": 'root',
#         "password": '123456',
#         'switch_time': 60
#     },
#     {
#         "name": 'my-adsl2',
#         "host": '123.456.678.789',
#         "port": 22,
#         "username": 'root',
#         "password": '123456',
#         'switch_time': 60
#     }
# ]

HOSTS_GROUP = {
    "group1": {  # 分组1
        "ssh2": {"host": "127.0.0.1", "username": "root", "password": "lanlan", "port": 44, "switch_time": 60},
        "ssh3": {"host": "127.0.0.1", "username": "root", "password": "lanlan", "port": 55, "switch_time": 60},
        "ssh4": {"host": "127.0.0.1", "username": "root", "password": "lanlan", "port": 66, "switch_time": 60},
    },
}

# for i in HOSTS_LIST['group3'].values():
#     print(type(i), i)