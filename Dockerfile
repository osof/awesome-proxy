FROM python:3.7.4

LABEL version = "1.0"
LABEL description = "一款基于ADSL的高可用、高性能、高匿名代理池！"

ENV TZ "Asia/Shanghai"

WORKDIR /root


RUN apt update && apt install -y apt-utils redis &&\
    apt-get clean && rm -rf /var/lib/apt/lists/*


ADD . /root/awesome-proxy

RUN pip install -r /root/awesome-proxy/config/requirements.txt -i https://pypi.doubanio.com/simple


# 修改配置文件    port 未配置
RUN sed -i "s/bind 127.0.0.1 ::1/bind 0.0.0.0/g" /etc/redis/redis.conf &&\
    sed -i "s/protected-mode yes/protected-mode no/g" /etc/redis/redis.conf &&\
    redis_passwd=`egrep -r "REDIS_PASSWORD" /root/awesome-proxy/config/api_config.py |awk {'print $3'}` &&\
    if [ $redis_passwd = "''" ] ;then echo 'Redis密码为空！';else `sed -i "s/# requirepass foobared/requirepass ${redis_passwd}/g" /etc/redis/redis.conf`;fi &&\
    api_port=`egrep -r "API_PORT" /root/awesome-proxy/config/api_config.py |awk {'print $3'}` &&\
    sed -i "s/\(-b 0.0.0.0:\)[0-9]*/\1${api_port}/" /root/awesome-proxy/config/supervisor.conf


# 目前EXPOSE端口还无法实现动态更改
EXPOSE 6379 9001 8080

# 最后的/bin/bash不能省略，其他都是后台进程，没有活跃在前台的进程容器会被终止。
CMD /etc/init.d/redis-server start && supervisord -c /root/awesome-proxy/config/supervisor.conf && /bin/bash
