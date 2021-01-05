---
title: mysql数据库的安装和卸载
date: 2017-09-10 15:05:40
tags: [MySQL,数据库]
categories: 数据库
---


## 一、mysql数据库的安装

这里我们使用mysql压缩包安装，也有使用安装程序安装的，那样比较简单，这里就不说明

+ 首先，去mysql的官网下载mysql数据库压缩包，下载完成之后，解压压缩包到自己想要安装的目录，解压过后的目录结构如下如所示
	![](/img/mysql_dir.png)

+ 在上图所示的目录下，创建```my.ini```配置文件来配置mysql
,配置文件添加如下内容：

![](/img/my.ini.jpg)


<!--more-->

> 下面粘贴实例方便复制

		[mysqld]
		
		port = 3306
		character_set_server = utf8
		
		basedir = F:\DataBase\mysql-5.7.19-winx64
		datadir = F:\DataBase\mysql-5.7.19-winx64\data
		
		sql_mode = NO_ENGINE_SUBSTITUTION,STRICT_TRANS_TABLES


​		
		[client]
		
		default-character-set = utf8



+ 在数据库```bin```目录下按住shift键鼠标右击打开命令行，使用命令```mysqld --initialize```初始化数据库，然后就会在数据库目录中多出一个```data```文件夹

+ 依然在```bin```目录下使用命令```mysqld -install```安装数据库服务，如果出现错误```Install/Remove of the Service Denied!```，表明没有安装权限，需要以管理员身份运行命令行即可解决问题，如图：
![](/img/mysql-install.png)

> 黑色部分是管理员身份打开的命令行
> 

+ 接下来启动mysql服务，在以管理员身份运行的命令行中运行`net start mysql`来启动服务

至此，`mysql数据库`已经安装成功并能够启动mysql数据库服务

## 二、mysql数据库的登录


当我尝试用`root`用户来登录数据库时，使用了`root`密码，但是密码不正确，提示`Access denied for user 'root'@'localhost' (using password: YES)`权限拒绝错误，遇到这种情况，可以采用如下方式来修改

1. 停止mysql服务，在win10下可以在`任务管理器`的服务中找到mysql服务然后停止，在win7下可以在计算机管理-服务 
中找到Mysql服务然后停止，上述方法都可以用`管理员命令行中运行net stop mysql`的方法代替

2. 依然在管理员命令行中运行`mysqld --skip-grant-tables`来跳过密码验证登录数据库，运行这个命令后此命令行会被阻塞而不能再键入，所以请重新运行一个命令行
	![](/img/mysqld--skip-grant-tables.png)

3. 在新的命令行中使用`mysql -uroot`登录，此时不需要密码就能成功登录数据库

	![](/img/mysqllogin.png)


4. 登录进去之后现在更改root用户的密码
	1. 使用`use mysql;`命令切换到mysql数据库
	2. 使用update语句修改user表中root用户的密码：`update user set authentication_string=password('root') where user='root'; `来修改root用户的密码，我这里把密码也设置为root，如果需要请自行修改
		> 注意：此数据库版本是`5.7`，网上资源说如果是`5.5`请使用`update user set password=password('root') where user='root';` 语句来代替上面的语句
	3. `flush privileges;`刷新权限
	4. `quit;`退出

5. 使用我们更改过后的登录数据库
	1. 关闭刚刚我们运行`mysqld --skip-grant-tables`的命令行窗口
	2. 使用命令`net start mysql`开启mysql服务(也可以通过其它方式启动),如果提示无法启动服务，请到任务管理器中结束`mysqld`进程后再启动服务，这样应该没问题了
	3. 运行`mysql -uroot -p`命令，之后输入密码(我的密码是root),登录
	
	![](/img/mysqlloginwithpwd.png)
6. 在操作时可能会遇到错误`You must reset your password using ALTER USER statement before executing this statement.`提示，这时可以使用`alter user 'root'@'localhost' identified by 'YOURPASSWORD';`或者`set password for 'root'@'localhost'=password('YOURPASSWORD');`,如果没有出现错误，就表明修改成功

到这里，就可以使用root用户和用户对应的密码来登录数据库执行操作


> 由于在整个执行命令的过程中没有把数据库安装目录的`bin`目录加入环境变量中，所以所有的关于mysql数据库的命令都必须在bin目录下执行，否则会提示`不是内部或外部命令，也不是可运行的程序
或批处理文件`。为了方便，可以自行把bin目录加入到环境变量中

## 三、mysql数据库的卸载

1. 命令行使用`mysqld --remove`来卸载服务，如果提示`Failed to remove the service because the service is running
Stop the service and try again`，请先停止mysql服务。如果提示`Service successfully removed.`则表面服务已经成功卸载，到计算机服务中查看已经不存在mysql服务。如果是使用安装程序安装的mysql，则还需要删除C盘中ProgramData的数据。


## 四、注意点

1. 如果没有安装数据库服务(即没有执行mysql的服务安装命令`mysqld --install`)就使用系统命令`net start mysql`会提示找不到mysql服务
2. 在没有安装mysql服务的情况下想要登录mysql需要先运行`mysqld`来启动mysql服务器，否则会出现` Can't connect to MySQL server on 'localhost' (10061)`的错误
3. 使用net start mysql也就运行mysqld来启动服务器