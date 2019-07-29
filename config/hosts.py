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

HOSTS_LIST = {
    "group1": {  # 分组1
        "my_adsl1": {"host": "192.168.1.1", "username": "11", "password": "aa", "port": 22, "switch_time": 60},
        "my_adsl2": {"host": "192.168.1.2", "username": "22", "password": "bb", "port": 22, "switch_time": 60},
        "my_adsl3": {"host": "192.168.1.3", "username": "33", "password": "cc", "port": 22, "switch_time": 60},
    },

    "group2": {  # 分组2
        "my_adsla": {"host": "192.168.1.5", "username": "11", "password": "aa", "port": 22, "switch_time": 60},
        "my_adslb": {"host": "192.168.1.6", "username": "22", "password": "bb", "port": 22, "switch_time": 60},
        "my_adslc": {"host": "192.168.1.7", "username": "33", "password": "cc", "port": 22, "switch_time": 60},
    },

    "group3": {
        "xx_adsl": {"host": "114.115.166.201", "username": "root", "password": "Admin@kylinstudio", "port": 22, "switch_time": 60},
    }
}

# for i in HOSTS_LIST['group3'].values():
#     print(type(i), i)