FROM python:3.7.4

# 本文件由build_images.sh生成，若要修改，请修改源文件！

LABEL version = "1.0"
LABEL description = "一款基于ADSL的高可用、高性能、高匿名代理池！"

ENV TZ "Asia/Shanghai"

WORKDIR /root


RUN apt update && apt install -y apt-utils redis &&    apt-get clean && rm -rf /var/lib/apt/lists/*


# 修改Redis配置
RUN sed -i "s/bind 127.0.0.1 ::1/bind 0.0.0.0/g" /etc/redis/redis.conf &&    sed -i "s/port 6379/port 6390/g" /etc/redis/redis.conf &&    sed -i "s/protected-mode yes/protected-mode no/g" /etc/redis/redis.conf &&    sed -i 's/# requirepass foobared/requirepass '123456'/g' /etc/redis/redis.conf

# 注意顺序，此时添加的文件配置都已修改为最新。
ADD . /root/awesome-proxy

RUN pip install -r /root/awesome-proxy/config/requirements.txt -i https://pypi.doubanio.com/simple

# 目前EXPOSE端口还无法实现动态更改
EXPOSE 8080 6390 9001

# 最后的/bin/bash不能省略，其他都是后台进程，没有活跃在前台的进程容器会被终止。
CMD /etc/init.d/redis-server start && supervisord -c /root/awesome-proxy/config/supervisor.conf && /bin/bash

