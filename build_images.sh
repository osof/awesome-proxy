#!/usr/bin/env bash

# 构建Docker镜像

# 安装Docker
check_docker(){
    if [ `docker -v|cut -d" " -f1` == 'Docker' ];then
        echo "本地已安装了Docker！"
    else
        echo "现在为您安装Docker！"
        curl -fsSL https://get.docker.com -o get-docker.sh && sh get-docker.sh
    fi
}


create_dockerfile(){
    api_port=`egrep -r "API_PORT" config/api_config.py |awk {'print $3'}`

    # Redis Config
    redis_port=`egrep -r "REDIS_PORT" config/api_config.py |awk {'print $3'}`

    redis_passwd=`egrep -r "REDIS_PASSWORD" config/api_config.py |awk {'print $3'}`

    if [ $redis_passwd != "''" ] ;then
        set_redis_passwd="sed -i 's/# requirepass foobared/requirepass ${redis_passwd}/g' /etc/redis/redis.conf"
    else
        set_redis_passwd="echo "
    fi
    # Supervisor config
    # 下面这句sed是匹配地址并替换端口，在Mac上会报错。
    sed -i "s/\(-b 0.0.0.0:\)[0-9]*/\1${api_port}/" config/supervisor.conf

    supervisor_username=`egrep -r "supervisor_username" config/api_config.py |awk {'print $3'}`
    supervisor_password=`egrep -r "supervisor_password" config/api_config.py |awk {'print $3'}`
    supervisor_port=`egrep -r "supervisor_port" config/api_config.py |awk {'print $3'}`
    sed -i "s/`egrep -r 'username' config/supervisor.conf |head -n1`/username=${supervisor_username}/g" config/supervisor.conf
    sed -i "s/`egrep -r 'password' config/supervisor.conf |head -n1`/password=${supervisor_password}/g" config/supervisor.conf

    sed -i "s/`grep 'port=' config/supervisor.conf`/port=:${supervisor_port}/g" config/supervisor.conf
    sed -i "s/\(serverurl=http:\/\/0.0.0.0:\)[0-9]*/\1${supervisor_port}/" config/supervisor.conf

    # 生成Dockerfile（直接编写Dockerfile在Mac上无法使用sed操作文件）
    cat > Dockerfile <<EOF
FROM python:3.7.4

# 本文件由build_images.sh生成，若要修改，请修改源文件！

LABEL version = "1.0"
LABEL description = "一款基于ADSL的高可用、高性能、高匿名代理池！"

ENV TZ "Asia/Shanghai"

WORKDIR /root


RUN apt update && apt install -y apt-utils redis &&\
    apt-get clean && rm -rf /var/lib/apt/lists/*


# 修改Redis配置
RUN sed -i "s/bind 127.0.0.1 ::1/bind 0.0.0.0/g" /etc/redis/redis.conf &&\
    sed -i "s/port 6379/port ${redis_port}/g" /etc/redis/redis.conf &&\
    sed -i "s/protected-mode yes/protected-mode no/g" /etc/redis/redis.conf &&\
    ${set_redis_passwd}

# 注意顺序，此时添加的文件配置都已修改为最新。
ADD . /root/awesome-proxy

RUN pip install -r /root/awesome-proxy/config/requirements.txt -i https://pypi.doubanio.com/simple

# 目前EXPOSE端口还无法实现动态更改
EXPOSE ${api_port} ${redis_port} 9001

# 最后的/bin/bash不能省略，其他都是后台进程，没有活跃在前台的进程容器会被终止。
CMD /etc/init.d/redis-server start && supervisord -c /root/awesome-proxy/config/supervisor.conf && /bin/bash

EOF
}

# super 账户密码问题


make_docker_images(){
    # 修改各种配置
    create_dockerfile
    # 打包镜像
    docker build -t ${1} -f ./Dockerfile .
    # 打包完成删除Dockerfile
    #rm -f ./Dockerfile
}


case "${1}" in
  check)
    check_docker
    ;;
  make_images)
    if [ "${2}" = "" ] ;then
        echo "第二个参数是镜像标签名称，必须填写！请使用: $0 make_images tag_name"
    else
        # 第二个参数传入方法作为make_docker_images的第一个参数
        make_docker_images ${2}
    fi
    ;;
  *)
    echo "请使用 $0 [ check | make_images tag_name ] 执行脚本！"
    ;;
esac


