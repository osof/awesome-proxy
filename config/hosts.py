# adsl主机配置文件

"""
说明：
目前只支持root用户执行任务，所以username必须为root，否则可能初始化失败！
cmd是拨号程序的开始拨号和停止拨号命令；各家服务商有细微区别，需要手动填写。
"""

# ADSL主机列表
HOSTS_GROUP = {
    "group1": {  # 分组1
        "ssh2": {
                    "host": "114.115.166.201",
                    "username": "root",
                    "password": "zzwul2018",
                    "port": 22,
                    "cmd": ('adsl-start', 'adsl-stop')
                 },
        "ssh3": {
                    "host": "114.115.166.202",
                    "username": "root",
                    "password": "zzwul2018",
                    "port": 22,
                    "cmd": ('adsl-start', 'adsl-stop')
                 },

    },
}
