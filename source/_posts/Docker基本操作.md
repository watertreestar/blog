---
title: Docker基本操作
date: 2019-1-27 13:41:23
tag: docker,容器
categories: docker
---

# Docker的基本操作

## Docker镜像

### Docker获取镜像

从 Docker 镜像仓库获取镜像的命令是 `docker pull`。其命令格式为 

```shell
docker pull [选项] [Docker Registry 地址[:端口号]/]仓库名[:标签]
```

<!--more-->

- Docker 镜像仓库地址：地址的格式一般是 `<域名/IP>[:端口号]`。默认地址是 Docker Hub。

- 仓库名：如之前所说，这里的仓库名是两段式名称，即 `<用户名>/<软件名>`。对于 Docker Hub，如果不给出用户名，则默认为 `library`，也就是官方镜像。

  比如

````shell
$ docker pull ubuntu:16.04
16.04: Pulling from library/ubuntu
bf5d46315322: Pull complete
9f13e0ac480c: Pull complete
e8988b5b3097: Pull complete
40af181810e7: Pull complete
e6f7c7e5c03e: Pull complete
Digest: sha256:147913621d9cdea08853f6ba9116c2e27a3ceffecf3b492983ae97c3d643fbbe
Status: Downloaded newer image for ubuntu:16.04
````

### Docker运行镜像

有了镜像之后，可以在此基础上启动并运行，运行后的镜像称为容器

```shell
$ docker run -it --rm ubuntu:16.04 bash

root@e7009c6ce357:/# cat /etc/os-release
NAME="Ubuntu"
VERSION="16.04.4 LTS, Trusty Tahr"
ID=ubuntu
ID_LIKE=debian
PRETTY_NAME="Ubuntu 16.04.4 LTS"
VERSION_ID="16.04"
HOME_URL="http://www.ubuntu.com/"
SUPPORT_URL="http://help.ubuntu.com/"
BUG_REPORT_URL="http://bugs.launchpad.net/ubuntu/"
```

`docker run` 就是运行容器的命令，我们这里简要的说明一下上面用到的参数。

- `-it`：这是两个参数，一个是 `-i`：交互式操作，一个是 `-t` 终端。我们这里打算进入 `bash` 执行一些命令并查看返回结果，因此我们需要交互式终端。
- `--rm`：这个参数是说容器退出后随之将其删除。默认情况下，为了排障需求，退出的容器并不会立即删除，除非手动 `docker rm`。我们这里只是随便执行个命令，看看结果，不需要排障和保留结果，因此使用 `--rm` 可以避免浪费空间。
- `ubuntu:16.04`：这是指用 `ubuntu:16.04` 镜像为基础来启动容器。
- `bash`：放在镜像名后的是**命令**，这里我们希望有个交互式 Shell，因此用的是 `bash`。
- 最后可以通过`exit`命令来退出容器



###  Docker列出镜像

```shell
[root@localhost ~]# docker image ls
REPOSITORY          TAG                 IMAGE ID            CREATED             SIZE
tomcat              latest              7ee26c09afb3        3 days ago          462MB
ubuntu              16.04               7e87e2b3bf7a        4 days ago          117MB
hello-world         latest              fce289e99eb9        3 weeks ago         1.84kB

```

列表包含了 `仓库名`、`标签`、`镜像 ID`、`创建时间` 以及 `所占用的空间` 

**镜像 ID** 则是镜像的唯一标识，一个镜像可以对应多个**标签** 



### 镜像体积问题

如果仔细观察，会注意到，这里标识的所占用空间和在 Docker Hub 上看到的镜像大小不同。比如，`ubuntu:16.04` 镜像大小，在这里是 `127 MB`，但是在 [Docker Hub](https://hub.docker.com/r/library/ubuntu/tags/) 显示的却是 `50 MB`。这是因为 Docker Hub 中显示的体积是压缩后的体积。在镜像下载和上传过程中镜像是保持着压缩状态的，因此 Docker Hub 所显示的大小是网络传输中更关心的流量大小。而 `docker image ls` 显示的是镜像下载到本地后，展开的大小，准确说，是展开后的各层所占空间的总和，因为镜像到本地后，查看空间的时候，更关心的是本地磁盘空间占用的大小。

另外一个需要注意的问题是，`docker image ls` 列表中的镜像体积总和并非是所有镜像实际硬盘消耗。由于 Docker 镜像是多层存储结构，并且可以继承、复用，因此不同镜像可能会因为使用相同的基础镜像，从而拥有共同的层。由于 Docker 使用 Union FS，相同的层只需要保存一份即可，因此实际镜像硬盘占用空间很可能要比这个列表镜像大小的总和要小的多

### 中间层镜像

为了节省空间，Docker会复用中间层镜像，而`docker image ls`只是显示了顶层镜像

如果希望显示包括中间层镜像在内的所有镜像的话，需要加 `-a` 参数。 

```shell
docker image ls -a
```

###  部分镜像查看

`docker image ls `会列出所有的顶层镜像，如果只想查看特定镜像，可以使用

```shell
$ docker image ls tomcat
REPOSITORY          TAG                 IMAGE ID            CREATED             SIZE
tomcat              latest              7ee26c09afb3        3 days ago          462MB
```

还可以同时指定仓库和标签

```shell
$ docker image ls ubuntu:16.04
REPOSITORY          TAG                 IMAGE ID            CREATED             SIZE
ubuntu              16.04               7e87e2b3bf7a        4 days ago          117MB

```



### Docker删除镜像

如果要删除本地的镜像，可以使用 `docker image rm` 命令，其格式为： 

````shell
$ docker image rm 镜像1 [镜像2]
````

其中，`<镜像>` 可以是 `镜像短 ID`、`镜像长 ID`、`镜像名` 或者 `镜像摘要`。 

我们可以用镜像的完整 ID，也称为 `长 ID`，来删除镜像。使用脚本的时候可能会用长 ID，但是人工输入就太累了，所以更多的时候是用 `短 ID` 来删除镜像。`docker image ls` 默认列出的就已经是短 ID 了，一般取前3个字符以上，只要足够区分于别的镜像就可以了 

例如：

```shell
[root@localhost ~]# docker image ls
REPOSITORY          TAG                 IMAGE ID            CREATED             SIZE
tomcat              latest              7ee26c09afb3        3 days ago          462MB
mysql               latest              71b5c7e10f9b        4 days ago          477MB
ubuntu              16.04               7e87e2b3bf7a        4 days ago          117MB
hello-world         latest              fce289e99eb9        3 weeks ago         1.84kB
[root@localhost ~]# docker image rm 71b
Untagged: mysql:latest
Untagged: mysql@sha256:048c2c616866c47c8a9fb604548d32ce842be292b56fba3d90fc07e0e143dac4
Deleted: sha256:71b5c7e10f9b20f4bd37c348872899cac828b1d2edad269fc8b93c9d43682241
Deleted: sha256:93b8c1c00d372509c6888231cb726e7b86967094de7ea52c937d15dd91950d0b
Deleted: sha256:3837955eb61ec7c85d40ab07652700261d7bc2697f286473c8e06a685b72bd04
Deleted: sha256:713ebd3c1007d105b495aea56622c280401fb7d546c446602b44c82db3f46426
Deleted: sha256:cef5d1285d28d5f7cb4628be7583a817c97bdd7b15973e4238f8104558586ff5
Deleted: sha256:f7aba53d045dded400e53bd3a206deebb0b238973528667d0b67a5acba7f0dd8
Deleted: sha256:f7812c287bf837a8305e90fcda2f64780d6c78a08e29c344d8f88450b0c6f6c6
Deleted: sha256:1ed10bc6753b7d6f1ef93f35f78c3ac288c703f4448b2af124f6aa1d8d0749fa
Deleted: sha256:9e7275e8e159891e30790fb7fef26fb0bffbf93fb4ca9ec7c2188419e1bca50c
Deleted: sha256:427ea12731646e109552c62208c34b89d7addadf83c7607a644325860ede8a70
Deleted: sha256:2006fea1cac1ad9982a33fee5fc6776dc7c5c6aabe7f7a1842125c55566c9ce6
Deleted: sha256:8e47708381224afca65fe791945667cc382aabe00c805f679a7136751aa6c3ad
Deleted: sha256:3c816b4ead84066ec2cadec2b943993aaacc3fe35fcd77ada3d09dc4f3937313

```

我们只用了ID的前3位就可以删除一个镜像

### Docker commit

注意： `docker commit` 命令除了学习之外，还有一些特殊的应用场合，比如被入侵后保存现场等。但是，不要使用 `docker commit` 定制镜像，定制镜像应该使用 `Dockerfile` 来完成 

镜像是容器的基础，每次执行 `docker run` 的时候都会指定哪个镜像作为容器运行的基础。在之前的例子中，我们所使用的都是来自于 Docker Hub 的镜像。直接使用这些镜像是可以满足一定的需求，而当这些镜像无法直接满足需求时，我们就需要定制这些镜像。接下来的几节就将讲解如何定制镜像 

现在让我们以定制一个 Web 服务器为例子，来讲解镜像是如何构建的 

#### pull nginx

```
[root@localhost ~]# docker pull nginx
Using default tag: latest
latest: Pulling from library/nginx
5e6ec7f28fb7: Pull complete 
ab804f9bbcbe: Pull complete 
052b395f16bc: Pull complete 
Digest: sha256:56bcd35e8433343dbae0484ed5b740843dd8bff9479400990f251c13bbb94763
Status: Downloaded newer image for nginx:latest

```

#### 启动容器

```
docker run --name webserver -d -p 80:80 nginx
```

这条命令会用 `nginx` 镜像启动一个容器，命名为 `webserver`，并且映射了 80 端口，这样我们可以用浏览器去访问这个 `nginx` 服务器。 

如果我们想对这个容器做修改，可以进入容器内

```
$ docker exec -it webserver bash
```

进入容器后，可以对文件做修改

```shell
root@3b9702b9719e:/# whereis nginx
nginx: /usr/sbin/nginx /usr/lib/nginx /etc/nginx /usr/share/nginx
root@3b9702b9719e:/# cd /usr/share/nginx
root@3b9702b9719e:/usr/share/nginx# ls
html
root@3b9702b9719e:/usr/share/nginx# echo '<h1>hello,ranger,this is nginx contianer on docker<h1>' > html
bash: html: Is a directory
root@3b9702b9719e:/usr/share/nginx# echo '<h1>hello,ranger,this is nginx contianer on docker<h1>' > html/index.html
root@3b9702b9719e:/usr/share/nginx# 
```

重新访问就可以看到改变后的页面

改变了容器中的文件，可以查看这些改动

```shell
root@3b9702b9719e:/# whereis nginx
nginx: /usr/sbin/nginx /usr/lib/nginx /etc/nginx /usr/share/nginx
root@3b9702b9719e:/# cd /usr/share/nginx
root@3b9702b9719e:/usr/share/nginx# ls
html
root@3b9702b9719e:/usr/share/nginx# echo '<h1>hello,ranger,this is nginx contianer on docker<h1>' > html
bash: html: Is a directory
root@3b9702b9719e:/usr/share/nginx# echo '<h1>hello,ranger,this is nginx contianer on docker<h1>' > html/index.html
root@3b9702b9719e:/usr/share/nginx# 
```

加入我们现在想把这些改动保存成一个新的镜像，以后使用，就可以使用`docker commit`

`docker commit` 的语法格式为：

```shell
docker commit [选项] <容器ID或容器名> [<仓库名>[:<标签>]]
```

现在查看有哪些镜像

```shell
[root@localhost ~]# docker image ls
REPOSITORY          TAG                 IMAGE ID            CREATED              SIZE
nginx               v2                  ac471dbf7f1f        About a minute ago   109MB
tomcat              latest              7ee26c09afb3        3 days ago           462MB
nginx               latest              42b4762643dc        4 days ago           109MB
ubuntu              16.04               7e87e2b3bf7a        4 days ago           117MB
hello-world         latest              fce289e99eb9        3 weeks ago          1.84kB

```



## Docker容器

### Docker容器启动

启动容器有两种方式，一种是基于镜像新建一个容器并启动，另外一个是将在终止状态（`stopped`）的容器重新启动。

因为 Docker 的容器实在太轻量级了，很多时候用户都是随时删除和新创建容器

### 查看容器

查看正在运行的容器

```shel
docker container ls
```

使用以下命令查看所有容器

```shell
docker container ls -a
```



### 新建并启动Docker

所需要的命令主要为 `docker run`。

例如，下面的命令输出一个 “Hello World”，之后终止容器。

```
$ docker run ubuntu:14.04 /bin/echo 'Hello world'
Hello world
```

这跟在本地直接执行 `/bin/echo 'hello world'` 几乎感觉不出任何区别。

下面的命令则启动一个 bash 终端，允许用户进行交互。

```
$ docker run -t -i ubuntu:14.04 /bin/bash
root@af8bae53bdd3:/#
```

其中，`-t` 选项让Docker分配一个伪终端（pseudo-tty）并绑定到容器的标准输入上， `-i` 则让容器的标准输入保持打开。

在交互模式下，用户可以通过所创建的终端来输入命令，例如

```
root@af8bae53bdd3:/# pwd
/
root@af8bae53bdd3:/# ls
bin boot dev etc home lib lib64 media mnt opt proc root run sbin srv sys tmp usr var
```

当利用 `docker run` 来创建容器时，Docker 在后台运行的标准操作包括：

- 检查本地是否存在指定的镜像，不存在就从公有仓库下载
- 利用镜像创建并启动一个容器
- 分配一个文件系统，并在只读的镜像层外面挂载一层可读写层
- 从宿主主机配置的网桥接口中桥接一个虚拟接口到容器中去
- 从地址池配置一个 ip 地址给容器
- 执行用户指定的应用程序
- 执行完毕后容器被终止

### 启动已经终止的容器

可以利用 `docker container start` 命令，直接将一个已经终止的容器启动运行。 





### 查看容器日志

使用`docker container logs 容器`

```shell
[root@localhost ~]# docker container logs 3b9
192.168.25.1 - - [27/Jan/2019:06:26:01 +0000] "GET / HTTP/1.1" 200 612 "-" "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.67 Safari/537.36" "-"
2019/01/27 06:26:03 [error] 6#6: *1 open() "/usr/share/nginx/html/favicon.ico" failed (2: No such file or directory), client: 192.168.25.1, server: localhost, request: "GET /favicon.ico HTTP/1.1", host: "192.168.25.136", referrer: "http://192.168.25.136/"
192.168.25.1 - - [27/Jan/2019:06:26:03 +0000] "GET /favicon.ico HTTP/1.1" 404 555 "http://192.168.25.136/" "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.67 Safari/537.36" "-"
192.168.25.1 - - [27/Jan/2019:06:29:54 +0000] "GET / HTTP/1.1" 200 55 "-" "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.67 Safari/537.36" "-"

```



### 终止容器

先查看正在运行的容器

```shell
[root@localhost ~]# docker container ls
CONTAINER ID        IMAGE               COMMAND                  CREATED             STATUS              PORTS                NAMES
3b9702b9719e        nginx               "nginx -g 'daemon of…"   38 minutes ago      Up 29 minutes       0.0.0.0:80->80/tcp   webserver
32e475d34375        tomcat              "catalina.sh run"        About an hour ago   Up 7 seconds        8080/tcp             compassionate_bardeen
[root@localhost ~]# 

```

可以使用 `docker container stop` 来终止一个运行中的容器。

此外，当 Docker 容器中指定的应用终结时，容器也自动终止。

例如对于上一章节中只启动了一个终端的容器，用户通过 `exit` 命令或 `Ctrl+d` 来退出终端时，所创建的容器立刻终止。

处于终止状态的容器，可以通过 `docker container start` 命令来重新启动。 

### Docker进入容器

在使用 `-d` 参数时，容器启动后会进入后台 

某些时候需要进入容器进行操作，包括使用 `docker attach` 命令或 `docker exec` 命令，推荐大家使用 `docker exec` 命令 

#### attach命令

`docker attach` 是 Docker 自带的命令。下面示例如何使用该命令 

```shell
[root@localhost ~]# docker attach 32e
^C27-Jan-2019 06:58:42.095 INFO [Thread-5] org.apache.coyote.AbstractProtocol.pause Pausing ProtocolHandler ["http-nio-8080"]
27-Jan-2019 06:58:42.306 INFO [Thread-5] org.apache.coyote.AbstractProtocol.pause Pausing ProtocolHandler ["ajp-nio-8009"]
27-Jan-2019 06:58:42.318 INFO [Thread-5] org.apache.catalina.core.StandardService.stopInternal Stopping service [Catalina]
27-Jan-2019 06:58:42.496 INFO [Thread-5] org.apache.coyote.AbstractProtocol.stop Stopping ProtocolHandler ["http-nio-8080"]
27-Jan-2019 06:58:42.499 INFO [Thread-5] org.apache.coyote.AbstractProtocol.stop Stopping ProtocolHandler ["ajp-nio-8009"]
27-Jan-2019 06:58:42.504 INFO [Thread-5] org.apache.coyote.AbstractProtocol.destroy Destroying ProtocolHandler ["http-nio-8080"]
27-Jan-2019 06:58:42.505 INFO [Thread-5] org.apache.coyote.AbstractProtocol.destroy Destroying ProtocolHandler ["ajp-nio-8009"]

```

进入容器后并停止了`tomcat`,`tomcat` 停止后，这个容器也就执行完了



#### exec命令

 i -t 参数

`docker exec` 后边可以跟多个参数，这里主要说明 `-i` `-t` 参数。

只用 `-i` 参数时，由于没有分配伪终端，界面没有我们熟悉的 Linux 命令提示符，但命令执行结果仍然可以返回。

当 `-i` `-t` 参数一起使用时，则可以看到我们熟悉的 Linux 命令提示符

```shell
[root@localhost ~]# docker run -dit ubuntu
4afc7ff447ac61e14242df8c2f8a26d8c54b8bee822dbfa2cd5340084b7e8e74
[root@localhost ~]# docker container ls
CONTAINER ID        IMAGE               COMMAND                  CREATED             STATUS              PORTS                NAMES
4afc7ff447ac        ubuntu              "/bin/bash"              21 seconds ago      Up 15 seconds                            blissful_wiles
3b9702b9719e        nginx               "nginx -g 'daemon of…"   About an hour ago   Up 37 minutes       0.0.0.0:80->80/tcp   webserver
32e475d34375        tomcat              "catalina.sh run"        About an hour ago   Up 3 minutes        8080/tcp             compassionate_bardeen
[root@localhost ~]# docker exec -i 4a bash
ls
bin
boot
dev
etc
home
lib
lib64
media
mnt
opt
proc
root
run
sbin
srv
sys


```

```shell
[root@localhost ~]# docker exec -i 4a bash
ls
bin
boot
dev
etc
home
lib
lib64
media
mnt
opt
proc
root
run
sbin
srv
sys

```

如果使用`docker attach 4a`进入容器后，再使用 exit退出容器，将会导致容器的终止



但是，使用`docker exec -it 4a bash`

如果从这个 stdin 中 exit，不会导致容器的停止。这就是为什么推荐大家使用 `docker exec` 的原因 



### 　导入导出容器

如果要导出本地某个容器，可以使用 `docker export` 命令 

```shell
[root@localhost ~]# docker container ls
CONTAINER ID        IMAGE               COMMAND                  CREATED             STATUS              PORTS                NAMES
3b9702b9719e        nginx               "nginx -g 'daemon of…"   About an hour ago   Up 45 minutes       0.0.0.0:80->80/tcp   webserver
32e475d34375        tomcat              "catalina.sh run"        2 hours ago         Up 11 minutes       8080/tcp             compassionate_bardeen
[root@localhost ~]# docker export 3b nginx.tar
"docker export" requires exactly 1 argument.
See 'docker export --help'.

Usage:  docker export [OPTIONS] CONTAINER

Export a container's filesystem as a tar archive
[root@localhost ~]# docker export 3b >  nginx.tar
[root@localhost ~]# ls
anaconda-ks.cfg  Git检出代码工作脚本  nginx.tar  original-ks.cfg

```

可以把导出的镜像在导入为镜像

可以使用 `docker import` 从容器快照文件中再导入为镜像 

### Docker删除容器

可以使用 `docker container rm` 来删除一个处于终止状态的容器。例如 

```shell
[root@localhost ~]# docker container ls -a
CONTAINER ID        IMAGE               COMMAND                  CREATED             STATUS                            PORTS                NAMES
c507aac48152        ubuntu              "/bin/bash"              35 minutes ago      Exited (0) 35 minutes ago                              flamboyant_lovelace
77a1908342b8        ubuntu              "bash"                   38 minutes ago      Exited (127) 37 minutes ago                            ecstatic_pike
3b9702b9719e        nginx               "nginx -g 'daemon of…"   About an hour ago   Up About an hour                  0.0.0.0:80->80/tcp   webserver
3c1ee95ddbfd        hello-world         "/hello"                 2 hours ago         Exited (0) 2 hours ago                                 confident_borg
32e475d34375        tomcat              "catalina.sh run"        2 hours ago         Exited (143) About a minute ago                        compassionate_bardeen
0955cc000279        tomcat              "-it"                    2 hours ago         Created                           8080/tcp             cocky_tesla
cd725259b2b3        hello-world         "/hello"                 2 hours ago         Exited (0) 2 hours ago                                 reverent_knuth
[root@localhost ~]# docker container rm c5
c5
[root@localhost ~]# docker container rm 77a  3c 32e 09 cd
77a
3c
32e
09
cd
[root@localhost ~]# docker container ls -a
CONTAINER ID        IMAGE               COMMAND                  CREATED             STATUS              PORTS                NAMES
3b9702b9719e        nginx               "nginx -g 'daemon of…"   About an hour ago   Up About an hour    0.0.0.0:80->80/tcp   webserver
[root@localhost ~]# 
```

###  清楚所有终止的容器

用 `docker container ls -a` 命令可以查看所有已经创建的包括终止状态的容器，如果数量太多要一个个删除可能会很麻烦，用下面的命令可以清理掉所有处于终止状态的容器。

```
$ docker container prune
```

> 以上就是docker的基本操作，以后还会涉及到高级的部分

> 大部分参考自什么是[Docker](http://www.funtl.com/zh/docs-docker/),在自己机器上验证了操作

