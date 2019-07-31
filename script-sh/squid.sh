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
    yum install squid httpd-tools curl -y
    # 修改配置
    conf_path=/etc/squid
    basic_auth=/usr/lib64/squid
    echo "auth_param basic program ${basic_auth}/basic_ncsa_auth /etc/squid/passwords" >> ${conf_path}/squid.conf
    echo 'auth_param basic realm proxy' >> ${conf_path}/squid.conf
    echo 'acl authenticated proxy_auth REQUIRED' >> ${conf_path}/squid.conf
    echo 'http_access allow authenticated' >> ${conf_path}/squid.conf   # 允许所有认证通过的客户端
    sed -i "s/http_port 3128/http_port ${proxy_port}/g" ${conf_path}/squid.conf
    sed -i "s/http_access deny all/#http_access deny all/g" ${conf_path}/squid.conf
    # 高匿设置
    echo 'request_header_access Via deny all' >> ${conf_path}/squid.conf
    echo 'request_header_access X-Forwarded-For deny all' >> ${conf_path}/squid.conf
    # 生成密钥
    htpasswd -bc  ${conf_path}/passwords ${proxy_user} ${proxy_passwd}
    chmod o+r ${conf_path}/passwords
    systemctl enable squid
    systemctl restart squid
}



apt_squid(){
	echo 'start install squid !'
    apt-get update -y && apt-get install squid apache2-utils curl -y
    # 修改配置
    if [ "${OS}" == 'Ubuntu' ]; then
        conf_path=/etc/squid3
        basic_auth=/usr/lib/squid3
        start_squid="sed -i '/By default this script does nothing/a\squid3' /etc/rc.local && pgrep squid3 |xargs kill -9 && squid3"
    elif [ "${OS}" == 'Debian' ]; then
        conf_path=/etc/squid
        basic_auth=/usr/lib/squid
        start_squid="service squid enable && service squid restart"
    fi
    echo "auth_param basic program ${basic_auth}/basic_ncsa_auth /etc/squid/passwords" >> ${conf_path}/squid.conf
    echo 'auth_param basic realm proxy' >> ${conf_path}/squid.conf
    echo 'acl authenticated proxy_auth REQUIRED' >> ${conf_path}/squid.conf
    echo 'http_access allow authenticated' >> ${conf_path}/squid.conf   # 允许所有认证通过的客户端
    sed -i "s/http_port 3128/http_port ${proxy_port}/g" ${conf_path}/squid.conf
    sed -i "s/http_access deny all/#http_access deny all/g" ${conf_path}/squid.conf
    # 高匿设置
    echo 'request_header_access Via deny all' >> ${conf_path}/squid.conf
    echo 'request_header_access X-Forwarded-For deny all' >> ${conf_path}/squid.conf
    # 生成密钥
    htpasswd -bc  ${conf_path}/passwords ${proxy_user} ${proxy_passwd}
    chmod o+r ${conf_path}/passwords
    ${start_squid}
}




# Get OS Type
if [ -e /etc/redhat-release ]; then
  OS=CentOS
  PM=yum
  init_sys
  yum_squid
elif [ -n "$(grep 'Amazon Linux' /etc/issue)" -o -n "$(grep 'Amazon Linux' /etc/os-release)" ]; then
  OS=CentOS
  PM=yum
  init_sys
  yum_squid
elif [ -n "$(grep 'bian' /etc/issue)" -o "$(lsb_release -is 2>/dev/null)" == "Debian" ]; then
  OS=Debian
  PM=apt
  init_sys
  apt_squid
elif [ -n "$(grep 'Deepin' /etc/issue)" -o "$(lsb_release -is 2>/dev/null)" == "Deepin" ]; then
  OS=Debian
  PM=apt
  init_sys
  apt_squid
elif [ -n "$(grep -w 'Kali' /etc/issue)" -o "$(lsb_release -is 2>/dev/null)" == "Kali" ]; then
  OS=Debian
  PM=apt
  init_sys
  apt_squid
elif [ -n "$(grep 'Ubuntu' /etc/issue)" -o "$(lsb_release -is 2>/dev/null)" == "Ubuntu" -o -n "$(grep 'Linux Mint' /etc/issue)" ]; then
  OS=Ubuntu
  PM=apt
  init_sys
  apt_squid
elif [ -n "$(grep 'elementary' /etc/issue)" -o "$(lsb_release -is 2>/dev/null)" == 'elementary' ]; then
  OS=Ubuntu
  PM=apt
  init_sys
  apt_squid
fi