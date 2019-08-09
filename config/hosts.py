# adsl主机配置文件

"""
重要说明：
1、主机名、组名都是唯一的，不要重复，如：myadsl1、myadsl2
2、目前只支持root用户执行任务，所以username必须为root，否则可能初始化失败！
3、cmd是拨号程序的开始拨号和停止拨号命令；各家服务商有细微区别，需要手动填写，如不清楚请保留默认配置。。
"""

# ADSL主机列表
HOSTS_GROUP = {
    "group1": {  # 分组1
        "myadsl1": {
            "host": "127.0.0.1",
            "username": "root",
            "password": "12345678",
            "port": 22,
            "cmd": ('adsl-start', 'adsl-stop')  # 见说明
        },
    },
}
