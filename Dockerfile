



#下载基本镜像
#安装基本软件，redis
#安装req
#修改配置
#启动服务器
#暴露端口

# Supervisor

# 1、启动Flask
# 2、执行主机管理程序，正常工作
# 3、启动定时任务，定时adsl拨号


# gunicorn -w 4 -b 0.0.0.0:80 -k gevent api_server:app


FROM python:3.7.4