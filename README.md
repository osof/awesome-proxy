# awesome-proxy
一款基于ADSL拨号主机构建的高可用、高性能、高匿名代理池！

**一次构建，长久使用，免维护**

---
# 架构图
![image](https://github.com/osof/awesome-proxy/blob/master/%E6%A1%86%E6%9E%B6%E5%9B%BEv1.png)


---
# OS支持
|操作系统|是否支持|
|---|---|
|Mac|是|
|Linux|是(Redhat系、Debian系)|
|Windows|不完全支持（只支持能执行sh脚本的环境cygwin、linux子系统等）|


---
# 快速开始
```bash
# 说明
可以在本地环境跑容器或者IDE中执行；也可以在云服务器上运行。
在IDE中运行需要执行api_server.py和tasks.py两个文件

# 拉取代码
git clone https://github.com/osof/awesome-proxy.git
cd awesome-proxy && chmod +x build_images.sh

# 修改配置
cd config # 并修改配置
# api_config.py : 接口、数据库等配置，只需修改代理账户、IP切换时间
# hosts.py : 配置您购买的adsl拨号主机
# supervisor.conf 该文件一般不用修改，根据api_config.py中的配置会自动覆盖相关配置。

# 检查本地环境是否已安装docker，如果没有安装则会自动安装。
./build_images.sh check


# 构建镜像
./build_images.sh make_images [you_images_tag_name]


# 启动容器
# 端口映射有三个：redis端口（可选）、API服务（必须）、Supervisor管理端口（可选）
docker run -idt --name [my_adsl] --restart=always -p xxx:xxx [you_images_tag_name]

```

---
# 其他
还没想好！