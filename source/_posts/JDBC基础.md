---
title: JDBC基础
date: 2017-09-12 15:22:24
tags: [Java,JDBC]
categories: Java
---


之前操作Mysql数据库都是使用客户端工具登录数据库，然后再客户端编写SQL语句，发送到数据库服务器执行，例如Mysql数据库带的mysql客户端工具，可以在命令行执行`mysql -uUSERNAME -pPASSWORD`来登录本机数据库

那么在Java程序代码中操作数据库，可以使用JDBC技术。

### 一，什么是JDBC

JDBC（Java DataBase Connectivity,java数据库连接）是一种用于执行SQL语句的Java API，可以为多种关系数据库提供统一访问，它由一组用Java语言编写的类和接口组成。直白讲就是使用Java代码发送SQL语句的技术。

<!--more-->

使用JDBC可以连接不同的数据库，只需要提供相应的驱动程序，驱动程序由数据库厂商提供，就是一堆实现了JDBC接口的类。

![](/img/JDBCintroduce.png)

这样做的好处：

- 开发者不需要关心数据库的驱动内部的原理，只需要维护Java部分的接口
- 数据库厂商如果修改了数据库的底层原理，也要提供对应的数据库驱动，但不影响Java程序部分


### 二，使用JDBC技术链接Mysql数据库服务器

连接数据库我们需要知道数据库的地址，端口号，正确的用户名和对应的密码

#### JDBC 核心API：

JDBC的核心接口和类位于Java标准库的`java.sql`和`javax.sql`中，常用的主要位于java.sql中

核心类或者接口介绍：

- Driver接口：表示Java驱动程序接口，数据库的驱动需要实现此接口
	- connect(url,properties)方法，可以连接url到指定的数据库
    

- Connection接口:表示与数据库的连接对象
	- createStatement():创建一个Statement对象
	- PreparedStatement(String sql):创建一个预编译的Statement对象
	- CallableStatement(String sql):创建CallableStatement对象
	
- DriverManager类：驱动管理类，用于管理所有的注册的驱动程序
	- registerDriver(Driver driver)：注册驱动程序
	- getConnection(url,user,password):返回一个对应的Connection对象

- Statement接口:用于执行静态 SQL 语句并返回它所生成结果的对象
	- executeUpdate(String sql)：用于执行静态的更新SQL语句
	- executeQuery(String sql):用于执行静态的查询SQL语句
	 

- PreparedStatement接口:Statement的子接口，表示预编译的 SQL 语句的对象
	- executeUpdate():用于执行预编译的更新SQL语句
	- executeQuery(): 用于执行预编译的查询SQL语句

- CallableStatement接口：Statement和PreparedStatement的子接口，调用储存过程的对象


#### JDBC 驱动的注册
在注册驱动之前，需要下载mysql数据库的驱动程序jar包添加到项目中
##### 第一种方式

```java

//1.创建数据库驱动对象
Driver driver = new com.mysql.jdbc.Driver();

Properties info = new Properties();
info.setProperty("user", "root");
info.setProperty("password", "root");

//2. 连接数据库
Connection connection = driver.connect(url, info);

``` 

##### 第二种方式(使用DriverManager（驱动管理）类来获取连接)
```java
//1.创建一个驱动对象
Driver driver = new com.mysql.jdbc.Driver();//这句代码中已经注册了驱动
// Driver driver2 = new com.orace.jdbc.Driver();

//2.注册驱动程序(可以注册多个)
DriverManager.registerDriver(driver);
// DriverManager.registerDriver(driver2);

//3. 获取连接对象
Connection connection = DriverManager.getConnection(url, user, password);
```

上面使用DriverManager来注册的方式实际会注册两次驱动

##### 第三种方式
 
```java
Class.forName("com.mysql.jdbc.Driver");

Connection connection = DriverManager.getConnection(url,user,password);

System.out.println(connection);
````

> 推荐使用第三种方式


下面用一个实例展示JDBC技术发送SQL语句的一般步骤

事先已经在本地mysql服务器上创建了一个mydb的数据库

```java
/*
 * 执行DML（数据库操纵语言）(insert update delete)
 * */
public class Demo2 {
	private String url="jdbc:mysql://localhost:3306/mydb";
	private String user="root";
	private String password="root";
	
	
	
	@Test
	public void testInsert(){
		Connection connection = null;
		Statement statement = null;
		try {
			Class.forName("com.mysql.jdbc.Driver");
			connection = DriverManager.getConnection(url,user,password);
		    statement = connection.createStatement();
			
			String sql = "insert into student(name,gender) values('云溪','女')";
			
			int count = statement.executeUpdate(sql);
			
			System.out.println("插入影响了"+count+"行");
		} catch (ClassNotFoundException e) {
			e.printStackTrace();
			throw new RuntimeException(e);
		} catch (SQLException e) {
			e.printStackTrace();
			throw new RuntimeException(e);
		}finally {
			if(statement!=null){
				try {
					statement.close();
				} catch (SQLException e) {
					e.printStackTrace();
					throw new RuntimeException(e);
				}
			}
			if(connection!=null){
				try {
					connection.close();
				} catch (SQLException e) {
					e.printStackTrace();
					throw new RuntimeException(e);
				}
			}
		}
		
		
	}
```
 

##### 可以看出JDBC操作数据库的一般步骤：

1. 注册驱动（只做一次）
2. 建立连接（Connection）
3. 创建执行SQL的语句（Statement）
4. 执行语句
5. 处理执行结果(ResultSet)
6. 释放资源
