---
title: maven-source-plugin
tags: [maven,maven-plugin]
date: 2021-07-24 21:16:45
categories: maven
description: '我们在IDEA中查看Maven包的代码时，右上角会有一个下载源码，这样我们就可以从仓库中获取到jar包对应的源码。

要获取源码，首先要在上传构建(项目)到仓库的时候同时上传source(源码)文件。

下面是Maven官网对于该插件的描述:'

---


# maven-source-plugin

> 源码在哪儿？

## 1. 介绍

我们在IDEA中查看Maven包的代码时，右上角会有一个下载源码，这样我们就可以从仓库中获取到jar包对应的源码。

要获取源码，首先要在上传构建(项目)到仓库的时候同时上传source(源码)文件。

下面是Maven官网对于该插件的描述:

> The Source Plugin creates a jar archive of the source files of the current project. The jar file is, by default, created in the project's target directory.

大致意思就是创建一个包含当前项目源码的jar压缩文件，默认情况下，这个jar压缩文件创建在target目录下


<!-- more -->

> 提示：从插件的 3.0.0 版开始，所有可以通过命令行使用的属性都基于以下架构 maven.source.* 命名



下面是该插件所包含的goal:

- [source:aggregate](http://maven.apache.org/plugins/maven-source-plugin/aggregate-mojo.html) aggregrates sources for all modules in an aggregator project.
- [source:jar](http://maven.apache.org/plugins/maven-source-plugin/jar-mojo.html) is used to bundle the main sources of the project into a jar archive.
- [source:test-jar](http://maven.apache.org/plugins/maven-source-plugin/test-jar-mojo.html) on the other hand, is used to bundle the test sources of the project into a jar archive.
- [source:jar-no-fork](http://maven.apache.org/plugins/maven-source-plugin/jar-no-fork-mojo.html) is similar to **jar** but does not fork the build lifecycle.
- [source:test-jar-no-fork](http://maven.apache.org/plugins/maven-source-plugin/test-jar-no-fork-mojo.html) is similar to **test-jar** but does not fork the build lifecycle.



maven中的`fork`是什么？

true 意味着它将创建（fork）一个新的` JVM `来运行编译器。这有点慢，但隔离更好。特别是可以指定一个不同于 Maven 启动的 JVM



## 2. 怎么使用

### 2.1 创建maven项目/模块

第一步当然是搭建一个maven的项目或者模块，这里就不用过多演示了，大家都会

### 2.2 pom中添加插件

```xml
<build>
  <plugins>
    <plugin>
      <groupId>org.apache.maven.plugins</groupId>
      <artifactId>maven-source-plugin</artifactId>
      <version>3.0.0</version>
      <!-- 绑定source插件到Maven的生命周期,并在生命周期后执行绑定的source的goal -->
      <executions>
        <execution>
          <!-- 绑定source插件到Maven的生命周期 -->
          <phase>compile</phase>
          <!--在生命周期后执行绑定的source插件的goals -->
          <goals>
            <goal>jar-no-fork</goal>
          </goals>
        </execution>
      </executions>
    </plugin>
  </plugins>
</build>
```

上面截取的一段定义就是配置maven-source-plugin插件，并绑定goal- `jar-no-fork`到default生命周期的compile phase,这样我们指定paase的执行就可以执行插件的goal

现在我们来试一下该插件，我们可以在terminal中切换到该项目下，然后执行`mvn compile`看效果:

![image-20210724183028418](https://cdn.jsdelivr.net/gh/watertreestar/CDN@master/picimage-20210724183028418.png)



假如我们没有绑定到生命周期的某一个phase而想要执行这个插件怎么做呢，就可以直接使用`goal而不是phase`来构建。

例如，我们把上面的exxcutions节点下所有的内容注释掉，然后在命令行执行mvn source:jar-no-fork也可以得到source打包后的文件

## 3. 使用建议

1. 如果在多项目的构建中，maven-source-plugin放在顶层的pom中是不会起作用的，需要放到具体的某一个项目中
2. 使用了该插件，在deploy到远程仓库后也会带上该项目的source文件


<hr />
