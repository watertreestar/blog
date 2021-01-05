---
title: Centos上Docker的安装
date: 2019-1-27 12:56:30
tag: [docker,容器]
---



## Centos上Docker的安装

### 系统要求

> Docker CE 支持 64 位版本 CentOS 7，并且要求内核版本不低于 3.10。 CentOS 7 满足最低内核的要求，但由于内核版本比较低，部分功能（如 `overlay2` 存储层驱动）无法使用，并且部分功能可能不太稳定 

我的系统版本

```shell
[root@localhost ~]# uname -a
Linux localhost.localdomain 3.10.0-514.10.2.el7.x86_64 #1 SMP Fri Mar 3 00:04:05 UTC 2017 x86_64 x86_64 x86_64 GNU/Linux

```

<!--more-->

### 卸载旧版本

旧版本的 Docker 称为 `docker` 或者 `docker-engine`，使用以下命令卸载旧版本 

```shell
$ sudo yum remove docker \
                  docker-client \
                  docker-client-latest \
                  docker-common \
                  docker-latest \
                  docker-latest-logrotate \
                  docker-logrotate \
                  docker-selinux \
                  docker-engine-selinux \
                  docker-engine
```

### 使用yum安装依赖包

```shell
$ sudo yum install -y yum-utils \
           device-mapper-persistent-data \
           lvm2
```

### 添加Docker软件源

```shell
$ sudo yum-config-manager \
    --add-repo \
    https://mirrors.ustc.edu.cn/docker-ce/linux/centos/docker-ce.repo


# 官方源
# $ sudo yum-config-manager \
#     --add-repo \
#     https://download.docker.com/linux/centos/docker-ce.repo    
```

### 安装Docker CE

```shell
$ sudo yum makecache fast
$ sudo yum install docker-ce
```

以上方式是使用`yum`来安装，还可以使用官方提供的自动化脚本来安装

```shell
$ curl -fsSL get.docker.com -o get-docker.sh
$ sudo sh get-docker.sh --mirror Aliyun   # 执行后，docker-ce将安装到系统
```

###  启动Docker-ce

```shell
$ sudo systemctl enable docker  # 开机启动
$ sudo systemctl start docker   # 启动docker-ce服务
```

默认情况下，`docker` 命令会使用 [Unix socket](https://en.wikipedia.org/wiki/Unix_domain_socket) 与 `Docker` 引擎通讯。只有`root`用户和`docker`组的用户才能够有权限。所以可以把非`root`用户加入到`docker`用户组中

```shell
sudo groupadd docker   # 创建docker用户组
sudo usermod -aG docker $USER   # 当前用户加入docker组 
```

### 测试

重新登录后测试`docker`服务是否可以使用

我们现在使用`docker run hello-world`命令来启动一个容器，如果`hello-world`镜像在本地不存在，docker会自动到仓库去`pull`

运行此命令后，会输出如下日志

```shell
[root@localhost ~]# docker run hello-world
Unable to find image 'hello-world:latest' locally
latest: Pulling from library/hello-world
1b930d010525: Pull complete 
Digest: sha256:2557e3c07ed1e38f26e389462d03ed943586f744621577a99efb77324b0fe535
Status: Downloaded newer image for hello-world:latest

Hello from Docker!
This message shows that your installation appears to be working correctly.

To generate this message, Docker took the following steps:
 1. The Docker client contacted the Docker daemon.
 2. The Docker daemon pulled the "hello-world" image from the Docker Hub.
    (amd64)
 3. The Docker daemon created a new container from that image which runs the
    executable that produces the output you are currently reading.
 4. The Docker daemon streamed that output to the Docker client, which sent it
    to your terminal.

To try something more ambitious, you can run an Ubuntu container with:
 $ docker run -it ubuntu bash

Share images, automate workflows, and more with a free Docker ID:
 https://hub.docker.com/

For more examples and ideas, visit:
 https://docs.docker.com/get-started/
```

##  镜像加速

由于国外的镜像拉取会比较慢，推荐使用国内的镜像源

```shell
$ vi /etc/docker/daemon.json  # 修改此文件
# 添加如下
{
        "registry-mirrors": ["http://hub-mirror.c.163.com"]
}

$ systemctl restart docker # 重启docker服务
```

