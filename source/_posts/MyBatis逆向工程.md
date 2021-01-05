---
title: MyBatis逆向工程
date: 2018-08-05 20:49:57
tags: [Java,MyBatis]
categories: 框架
---

####  什么是逆向工程

MyBatis的一个主要的特点就是需要程序员自己编写sql，那么如果表太多的话，难免会很麻烦，所以mybatis官方提供了一个逆向工程，可以针对单表自动生成mybatis执行所需要的代码（包括mapper.xml、mapper.java、pojo）。一般在开发中，常用的逆向工程方式是通过数据库的表生成代码

<!--more-->

#### 使用逆向工程生成代码

##### 1. 新建一个工程

使用Maven新建一个Java工程引入相应的包

```xml
<dependencies>
  	<dependency>
  		<groupId>org.mybatis.generator</groupId>
  		<artifactId>mybatis-generator-core</artifactId>
  		<version>1.3.5</version>
  	</dependency>
  	<dependency>
  		<groupId>mysql</groupId>
  		<artifactId>mysql-connector-java</artifactId>
  		<version>5.1.40</version>
  	</dependency>
  	<dependency>
  		<groupId>org.mybatis</groupId>
  		<artifactId>mybatis</artifactId>
  		<version>3.4.1</version>
  	</dependency>
  </dependencies>
```



##### 2. 建立逆向工程配置文件

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE generatorConfiguration
  PUBLIC "-//mybatis.org//DTD MyBatis Generator Configuration 1.0//EN"
  "http://mybatis.org/dtd/mybatis-generator-config_1_0.dtd">
 
<generatorConfiguration>

        <!-- 有Example查询条件内容 -->
       	<context id="testTables" targetRuntime="MyBatis3"> 
        <commentGenerator>
            <!-- 是否去除自动生成的注释 true：是 ： false:否 -->
            <property name="suppressAllComments" value="true" />
        </commentGenerator>
 
        <!--数据库连接的信息：驱动类、连接地址、用户名、密码 (自己修改)-->
        <jdbcConnection
            driverClass="com.mysql.jdbc.Driver"
            connectionURL="jdbc:mysql://localhost:3306/mydb"
            userId="cyp"
            password="cyp">
        </jdbcConnection>
 
        <!-- 默认false，把JDBC DECIMAL 和 NUMERIC 类型解析为 Integer，为 true时把JDBC DECIMAL
            和 NUMERIC 类型解析为java.math.BigDecimal -->
        <javaTypeResolver>
            <property name="forceBigDecimals" value="false" />
        </javaTypeResolver>
 
        <!-- targetProject:生成Entity类的路径 -->
        <javaModelGenerator targetProject="./src/main/java"
            targetPackage="pojo">
            <!-- enableSubPackages:是否让schema作为包的后缀 -->
            <property name="enableSubPackages" value="false" />
            <!-- 从数据库返回的值被清理前后的空格 -->
            <property name="trimStrings" value="true" />
        </javaModelGenerator>
 
        <!-- targetProject:XXXMapper.xml映射文件生成的路径 -->
        <sqlMapGenerator targetProject="./src/main/resources"
            targetPackage="mapper">
            <!-- enableSubPackages:是否让schema作为包的后缀 -->
            <property name="enableSubPackages" value="false" />
        </sqlMapGenerator>
 
        <!-- targetPackage：Mapper接口生成的位置 -->
        <javaClientGenerator type="XMLMAPPER"
            targetProject="./src/main/java" targetPackage="dao">
            <!-- enableSubPackages:是否让schema作为包的后缀 -->
            <property name="enableSubPackages" value="false" />
        </javaClientGenerator>
 
        <!-- 数据库表名字和我们的entity类对应的映射指定(需自己修改) -->
        <table tableName="user" domainObjectName="User" />
        <table tableName="student" domainObjectName="Student" />
        <table tableName="account" domainObjectName="Account" />
 
        <!-- 有些表的字段需要指定java类型 <table schema="" tableName=""> <columnOverride column=""
            javaType="" /> </table> -->
    </context>
</generatorConfiguration>
```

配置文件中各个标签的作用已经在配置文件中注释

配置文件中POJO，mapper接口，mapper文件的包创建好



##### 3. 新建工具类，用来加载配置文件和生成代码

```java
package util;
import java.io.File;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;

import org.mybatis.generator.api.MyBatisGenerator;
import org.mybatis.generator.config.Configuration;
import org.mybatis.generator.config.xml.ConfigurationParser;
import org.mybatis.generator.exception.XMLParserException;
import org.mybatis.generator.internal.DefaultShellCallback;

/**
 * 加载逆向生成配置文件，逆向生成代码
 * @author WaterTree
 *
 */
public class MybatisGeneratorUtil {
	public static void generator() throws Exception, XMLParserException{
		List<String> warnings = new ArrayList<String>();
		
		// 指定逆向工程配置文件
		File configurationFile = new File("generatorConfig.xml");
		ConfigurationParser cp = new ConfigurationParser(warnings);
		
		Configuration configuration = cp.parseConfiguration(configurationFile);
		DefaultShellCallback callback = new DefaultShellCallback(true);
		
		MyBatisGenerator myBatisGenerator = new MyBatisGenerator(configuration, callback, warnings);
		
		myBatisGenerator.generate(null);
	}
}

```



##### 4. 新建类包含mian方法调用工具类

```java
package util;
import java.io.File;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;

import org.mybatis.generator.api.MyBatisGenerator;
import org.mybatis.generator.config.Configuration;
import org.mybatis.generator.config.xml.ConfigurationParser;
import org.mybatis.generator.exception.XMLParserException;
import org.mybatis.generator.internal.DefaultShellCallback;

/**
 * 加载逆向生成配置文件，逆向生成代码
 * @author WaterTree
 *
 */
public class MybatisGeneratorUtil {
	public static void generator() throws Exception, XMLParserException{
		List<String> warnings = new ArrayList<String>();
		
		// 指定逆向工程配置文件
		File configurationFile = new File("generatorConfig.xml");
		ConfigurationParser cp = new ConfigurationParser(warnings);
		
		Configuration configuration = cp.parseConfiguration(configurationFile);
		DefaultShellCallback callback = new DefaultShellCallback(true);
		
		MyBatisGenerator myBatisGenerator = new MyBatisGenerator(configuration, callback, warnings);
		
		myBatisGenerator.generate(null);
	}
}

```

##### 5. 运行后项目的结构

![](/img/mybatis逆行工程项目结构.png)





#### 逆向工具生成的Example类

自定义查询条件的java类

```java
public class StudentExample {
    /*
		排序方式  字段 + 空格 + asc（desc）	
	*/
    protected String orderByClause;
	
    /*
    	是否去重
    */
    protected boolean distinct;
	
    /*
    	查询条件   eg->   name = 'tom'
    */
    protected List<Criteria> oredCriteria;

    public StudentExample() {
        oredCriteria = new ArrayList<Criteria>();
    }

    public void setOrderByClause(String orderByClause) {
        this.orderByClause = orderByClause;
    }

    public String getOrderByClause() {
        return orderByClause;
    }

    public void setDistinct(boolean distinct) {
        this.distinct = distinct;
    }

    public boolean isDistinct() {
        return distinct;
    }

    public List<Criteria> getOredCriteria() {
        return oredCriteria;
    }

    public void or(Criteria criteria) {
        oredCriteria.add(criteria);
    }
```

