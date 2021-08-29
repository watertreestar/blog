---
title: Maven依赖，去哪儿找你呢？
tags: [Maven,工程化]
date: 2021-08-29 16:11:37
permalink: where-is-maven-dep
categories: Maven
---

<img src="https://cdn.jsdelivr.net/gh/watertreestar/CDN@master/picimage-20210829143616546.png" alt="" style="width:100%" />


# 1. 前言

`maven`是作为`Javer`日常开发中必不可少的工具，但是很多人对于它的使用也只是仅限于的几个功能。

前几天在使用一个依赖总是说找不到该依赖，但是在中央仓库中的确存在该构建。这个问题让我很困惑，突然发现对于maven这个优秀构建工具的使用也只是浮于表面。痛定思痛，于是就有了这篇简短的总结。

> 对于maven依赖顺序的搜索，网上众说纷纭，那么真相到底是怎么样的呢？

<!-- more -->


# 2. 准备

根据我们的开发经验，使用maven可以配置多个仓库，先来看看我们最熟悉的一个。

打开我们的settings.xml文件,一开始是一个最纯洁的配置文件：

![image-20210826221331089](https://cdn.jsdelivr.net/gh/watertreestar/CDN@master/picimage-20210826221331089.png)

可以看到，只是配置了一个镜像地址和一个本地仓库的路径，这也是我们第一次使用maven时大多数教程中会提到的一点-修改mirror为国内的一个地址。

现在我们创建一个maven的工程，然后看看它的依赖查找顺序是怎样的？

我创建了一个`mvn-dep`文件夹，在这里面创建项目所需要的文件，为了简单，我就使用maven cli来搭建一个简单的项目，使用的命令如下：

```shell
mvn archetype:generate -DarchetypeGroupId=org.apache.maven.archetypes -DarchetypeArtifactId=maven-archetype-webapp  -DinteractiveMode=true -DgroupId=com.watertreestar -DartifactId=mvn-dep -Dversion=1.0 -Dpackage=com.watertreestar
```

创建好以后我们的项目结构如下：

<img align="left" height="300" src="https://cdn.jsdelivr.net/gh/watertreestar/CDN@master/picimage-20210826222721918.png">

接下来看一下不同的配置下依赖查找的路径



# 3. 依赖查找探索

使用上一步创建的项目，并在上面的基础settings.xml配置文件上做修改，观察依赖查找的优先级。

在操作之前，我们在项目的pom.xml中已经包含了一个依赖就是fastjson

```xml
 <dependency>
   <groupId>com.alibaba</groupId>
   <artifactId>fastjson</artifactId>
   <version>1.2.78</version>
</dependency>
```


我们先确保本地仓库中该版本的junit不存在,使用`rm`命令来删除它:

`rm -rf  ~/.m2/repository/com/alibaba/fastjson`



## 3.1 不修改的情况

我们使用上面的setings.xml文件，不做任何修改,执行`mvn compile`命令,输出如下：

![image-20210829143616546](https://cdn.jsdelivr.net/gh/watertreestar/CDN@master/picimage-20210829143616546.png)

可以看出，maven是从我们配置的central镜像-阿里云镜像中拉取依赖



## 3.2 没有配置中央仓库镜像

现在我们把settings文件中的mirror配置删除,就成了一个光秃秃的配置：

```xml
<?xml version="1.0" encoding="UTF-8"?>
<settings xmlns="http://maven.apache.org/SETTINGS/1.0.0"
          xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
          xsi:schemaLocation="http://maven.apache.org/SETTINGS/1.0.0 http://maven.apache.org/xsd/settings-1.0.0.xsd">

    <pluginGroups></pluginGroups>

    <proxies></proxies>
    
    <localRepository>/Users/young/.m2/repository</localRepository>

</settings>
```



这种情况下，依赖会从哪儿获取呢

![image-20210829143812267](https://cdn.jsdelivr.net/gh/watertreestar/CDN@master/picimage-20210829143812267.png)

可以看到，是从默认的中央仓库中查找和下载依赖。

根据上面的结果可以看到优先级：

> 特定仓库reporitory的镜像mirror > settings中配置的仓库repository 



## 3.3 项目配置仓库repository

1. 现在我们把仓库的配置还原到最初的状态，如下：

```xml
<?xml version="1.0" encoding="UTF-8"?>
<settings xmlns="http://maven.apache.org/SETTINGS/1.0.0"
   xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://maven.apache.org/SETTINGS/1.0.0 http://maven.apache.org/xsd/settings-1.0.0.xsd">

   <pluginGroups></pluginGroups>

   <proxies></proxies>

   <localRepository>/Users/young/.m2/repository</localRepository>

   <mirrors>
      <mirror>
         <id>settings-mirror</id>
         <url>https://maven.aliyun.com/repository/public</url>
         <mirrorOf>central</mirrorOf>
      </mirror>
   </mirrors>
</settings>

```



2. 然后在第二节中创建的项目pom.xml文件中添加一个repository配置,我们使用了一个sonatype的maven仓库

   当前的`项目pom.xml配置`如下:

```xml
<dependencies>
   <dependency>
     <groupId>com.alibaba</groupId>
     <artifactId>fastjson</artifactId>
     <version>1.2.78</version>
  </dependency>
</dependencies>

<repositories>
  <repository>
    <id>pom_repository</id>
    <name>sonatype</name>
    <url>https://repository.sonatype.org/content/groups/public/</url>
    <releases>
      <enabled>true</enabled>
    </releases>
    <snapshots>
      <enabled>true</enabled>
    </snapshots>
  </repository>
</repositories>
```

执行`mvn compile`命令，输出如下：

![](https://cdn.jsdelivr.net/gh/watertreestar/CDN@master/picpicimage-20210829151337364.png)

可以看出依赖从项目pom.xml配置的pom-repository仓库中查找并下载。



## 3.4 配置全局profile中的repository

在maven配置文件settings.xml中增加profile配置

![image-20210826235027569](https://cdn.jsdelivr.net/gh/watertreestar/CDN@master/picimage-20210826235027569.png)

使用`maven compile -Psettings-profile`

![image-20210829151813952](https://cdn.jsdelivr.net/gh/watertreestar/CDN@master/picimage-20210829151813952.png)

可以看出，依赖从settings.xml中我们配置settings-profile的repository中下载的

> settings_profile_repository > pom_repositories



## 3.5 配置项目profile的repository

### 3.5.1 激活pom中的profile和setting中的profile

全局settings.xml中的配置不见，在pom.xml中增加profile配置：

```xml
<profiles>
  <profile>
    <id>pom-profile</id>
    <repositories>
      <repository>
        <id>pom-profile-repository</id>
        <name>maven2</name>
        <url>https://repo.maven.apache.org/maven2/</url>
        <releases>
          <enabled>true</enabled>
        </releases>
        <snapshots>
          <enabled>true</enabled>
        </snapshots>
      </repository>
    </repositories>
  </profile>
</profiles>
```

删除本地仓库的fastjson依赖，然后执行`mvn compile -Psettings-profile,pom-profile`

输出：

![image-20210829153530950](https://cdn.jsdelivr.net/gh/watertreestar/CDN@master/picimage-20210829153530950.png)

我们同时激活了settings-profile和pom-profile,但是最终依赖的下载是从settings-profile中配置的仓库下载的。

> settings-profile > pom-profile



### 3.5.2 只是激活pom中的profile

假如只是激活pom中的profile,也就是使用`mvn compile -Ppom-profile`,输出结果如下：

![image-20210829153952948](https://cdn.jsdelivr.net/gh/watertreestar/CDN@master/picimage-20210829153952948.png)

可以看出，最终依赖的下载是从pom中配置的profile-repository中下载的

> pom-profile-repository > pom-repository



## 3.6 local repository

由于之前的步骤中我们已经下载jar到了local仓库，为了测试最后一步，我们就不用在执行`rm -rf ~/.m2/repository/com/alibaba/fastjson`来删除本地的依赖了。

我这里使用了` mvn compile -Ppom-profile`来做测试，输出的结果如下：

![image-20210829154538769](https://cdn.jsdelivr.net/gh/watertreestar/CDN@master/picimage-20210829154538769.png)

可以看到，没有从任何远程仓库中下载依赖

> local > 所有远程仓库



# 4. 总结

从上面一系列的验证中可以总结出依赖查找的优先级：

>  local-repo > settings-profile-repository > pom-profile-repository > pom-repository >  central

理解maven查找的优先级，可以帮助我们在工作和学习中解决一些依赖找不到的错误。



最后，推荐几个可以使用的maven仓库：

- https://repo.maven.apache.org/maven2/
- https://repo1.maven.org/maven2/
- https://maven.aliyun.com/repository/public



