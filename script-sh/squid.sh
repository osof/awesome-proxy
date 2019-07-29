#!/bin/bash
# squid安装脚本

# 代理服务器账户
proxy_user='myproxy'
proxy_passwd='N2PYOnRDk5gKInqQ'
proxy_port=3100



init_sys(){
    echo 'init system !'
    if [ "${PM}" == 'yum' ]; then
        # 关闭SELinux
        setenforce 0
        sed -i "s/^SELINUX=enforcing/SELINUX=disabled/g" /etc/sysconfig/selinux
        sed -i "s/^SELINUX=enforcing/SELINUX=disabled/g" /etc/selinux/config
        sed -i "s/^SELINUX=permissive/SELINUX=disabled/g" /etc/sysconfig/selinux
        sed -i "s/^SELINUX=permissive/SELINUX=disabled/g" /etc/selinux/config
        # 开启包转发
        echo 1 > /proc/sys/net/ipv4/ip_forward
        echo 'net.ipv4.ip_forward = 1' >> /etc/sysctl.conf
    fi
    if [ "${PM}" == 'apt' ]; then
        # 开启包转发
        echo 1 > /proc/sys/net/ipv4/ip_forward
        echo 'net.ipv4.ip_forward = 1' >> /etc/sysctl.conf
    fi
}



yum_squid(){
    echo 'start install squid !'
    yum install squid httpd-tools -y
    # 修改配置
    echo 'auth_param basic program /usr/lib64/squid/basic_ncsa_auth /etc/squid/passwords' >> /etc/squid/squid.conf
    echo 'auth_param basic realm proxy' >> /etc/squid/squid.conf
    echo 'acl authenticated proxy_auth REQUIRED' >> /etc/squid/squid.conf
    echo 'http_access allow authenticated' >> /etc/squid/squid.conf   # 允许所有认证通过的客户端
    sed -i "s/http_port 3128/http_port ${proxy_port}/g" /etc/squid/squid.conf
    sed -i "s/http_access deny all/#http_access deny all/g" /etc/squid/squid.conf
    # 高匿设置
    echo 'request_header_access Via deny all' >> /etc/squid/squid.conf
    echo 'request_header_access X-Forwarded-For deny all' >> /etc/squid/squid.conf
    # 生成密钥
    htpasswd -bc  /etc/squid/passwords ${proxy_user} ${proxy_passwd}
    chmod o+r /etc/squid/passwords
    systemctl enable squid
    systemctl restart squid
}



apt_squid(){
	echo 'start install squid !'
    apt-get update -y && apt-get install squid apache2-utils -y
    # 修改配置
    echo 'auth_param basic program /usr/lib/squid/basic_ncsa_auth /etc/squid/passwords' >> /etc/squid/squid.conf
    echo 'auth_param basic realm proxy' >> /etc/squid/squid.conf
    echo 'acl authenticated proxy_auth REQUIRED' >> /etc/squid/squid.conf
    echo 'http_access allow authenticated' >> /etc/squid/squid.conf   # 允许所有认证通过的客户端
    sed -i "s/http_port 3128/http_port ${proxy_port}/g" /etc/squid/squid.conf
    sed -i "s/http_access deny all/#http_access deny all/g" /etc/squid/squid.conf
    # 高匿设置
    echo 'request_header_access Via deny all' >> /etc/squid/squid.conf
    echo 'request_header_access X-Forwarded-For deny all' >> /etc/squid/squid.conf
    # 生成密钥
    htpasswd -bc  /etc/squid/passwords ${proxy_user} ${proxy_passwd}
    chmod o+r /etc/squid/passwords
    service squid enable
    service squid restart
}




# 系统判断
if [ -e "/usr/bin/yum" ]; then
  PM=yum
  init_sys
  yum_squid
fi
if [ -e "/usr/bin/apt-get" ]; then
  PM=apt
  init_sys
  apt_squid
fi

