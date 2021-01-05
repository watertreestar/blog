---
title: MyBatis入门
date: 2018-07-12 15:22:24
tags: [Java,MyBatis]
categories: 框架
---

#### 1. MyBatis 简介

- MyBatis是一个优秀的**持久层框架**，它对jdbc的操作数据库的过程进行封装，使开发者只需要关注 SQL 本身，而不需要花费精力去处理例如注册驱动、创建connection、创建statement、手动设置参数、结果集检索等jdbc繁杂的过程代码。
- Mybatis通过xml或注解的方式将要执行的各种statement（statement、preparedStatemnt、CallableStatement）配置起来，并通过java对象和statement中的sql进行映射生成最终执行的sql语句，最后由mybatis框架执行sql并将结果映射成java对象并返回

<!--more-->

#### 2. MyBatis架构

 ![](/img/MyBatis架构.png)

##### MyBatis配置

- SqlMapConfig.xml，此文件作为mybatis的全局配置文件，配置了mybatis的运行环境等信息、
- mapper.xml文件即sql映射文件，文件中配置了操作数据库的sql语句。此文件需要在SqlMapConfig.xml中加载

##### SqlSessionFactory

 通过mybatis环境等配置信息构造SqlSessionFactory即会话工厂

##### SqlSession

由会话工厂创建sqlSession即会话，操作数据库需要通过sqlSession进行。

##### Executor

mybatis底层自定义了Executor执行器接口操作数据库，Executor接口有两个实现，一个是基本执行器、一个是缓存执行器。

##### Mapped Statement

Mapped Statement也是mybatis一个底层封装对象，它包装了mybatis配置信息及sql映射信息等。mapper.xml文件中一个sql对应一个Mapped Statement对象，sql的id即是Mapped statement的id

Mapped Statement对sql执行输入参数进行定义，包括HashMap、基本类型、pojo，Executor通过Mapped Statement在执行sql前将输入的java对象映射至sql中，输入参数映射就是jdbc编程中对preparedStatement设置参数

Mapped Statement对sql执行输出结果进行定义，包括HashMap、基本类型、pojo，Executor通过Mapped Statement在执行sql后将输出结果映射至java对象中，输出结果映射过程相当于jdbc编程中对结果的解析处理过程。



#### 3. MyBatis框架搭建

1. 导包

   ```xml
   <dependency>
         <groupId>org.mybatis</groupId>
         <artifactId>mybatis</artifactId>
         <version>3.2.7</version>
       </dependency>
       <!-- https://mvnrepository.com/artifact/mysql/mysql-connector-java -->
       <dependency>
         <groupId>mysql</groupId>
         <artifactId>mysql-connector-java</artifactId>
         <version>5.1.8</version>
       </dependency>
       <dependency>
         <groupId>commons-logging</groupId>
         <artifactId>commons-logging</artifactId>
         <version>1.1.1</version>
       </dependency>
       <dependency>
         <groupId>log4j</groupId>
         <artifactId>log4j</artifactId>
         <version>1.2.17</version>
       </dependency>
       <dependency>
         <groupId>org.apache.logging.log4j</groupId>
         <artifactId>log4j-api</artifactId>
         <version>2.10.0</version>
       </dependency>
       <!-- https://mvnrepository.com/artifact/org.apache.logging.log4j/log4j-core -->
       <dependency>
         <groupId>org.apache.logging.log4j</groupId>
         <artifactId>log4j-core</artifactId>
         <version>2.1</version>
       </dependency>
       <!-- https://mvnrepository.com/artifact/org.slf4j/slf4j-api -->
       <dependency>
         <groupId>org.slf4j</groupId>
         <artifactId>slf4j-api</artifactId>
         <version>1.7.6</version>
       </dependency>
       <!-- https://mvnrepository.com/artifact/org.slf4j/slf4j-log4j12 -->
       <dependency>
         <groupId>org.slf4j</groupId>
         <artifactId>slf4j-log4j12</artifactId>
         <version>1.7.6</version>
         <scope>test</scope>
       </dependency>
       <!-- https://mvnrepository.com/artifact/cglib/cglib -->
       <dependency>
         <groupId>cglib</groupId>
         <artifactId>cglib</artifactId>
         <version>3.1</version>
       </dependency>
       <!-- https://mvnrepository.com/artifact/org.javassist/javassist -->
       <dependency>
         <groupId>org.javassist</groupId>
         <artifactId>javassist</artifactId>
         <version>3.18.2-GA</version>
       </dependency>
       <!-- https://mvnrepository.com/artifact/org.ow2.asm/asm -->
       <dependency>
         <groupId>org.ow2.asm</groupId>
         <artifactId>asm</artifactId>
         <version>5.0.3</version>
       </dependency>
   ```

   ​

2. 建立数据库表

   ```sql
   DROP TABLE IF EXISTS `user`;
   CREATE TABLE `user` (
   `id` int(11) NOT NULL AUTO_INCREMENT,
   `name` varchar(32) NOT NULL COMMENT '用户名称',
   `birthday` date DEFAULT NULL COMMENT '生日',
   `sex` char(1) DEFAULT NULL COMMENT '性别',
   `address` varchar(256) DEFAULT NULL COMMENT '地址',
   PRIMARY KEY (`id`)
   ) ENGINE=InnoDB AUTO_INCREMENT=27 DEFAULT CHARSET=utf8;

   ```



3. 创建User实体类，对应数据库中的user

   ```java
   private int id;
   private String username;// 用户姓名
   private String sex;// 性别
   private Date birthday;// 生日
   private String address;// 地址
   ```

4. 核心配置文件`sqlMapConfig.xml`(src目录下)

   ```xml
   <?xml version="1.0" encoding="UTF-8" ?>
   <!DOCTYPE configuration
   PUBLIC "-//mybatis.org//DTD Config 3.0//EN"
   "http://mybatis.org/dtd/mybatis-3-config.dtd">
   <configuration>
   <!-- 和spring整合后 environments配置将废除 -->
   <environments default="development">
       <environment id="development">
           <!-- 使用jdbc事务管理 -->
           <transactionManager type="JDBC" />
           <!-- 数据库连接池 -->
           <dataSource type="POOLED">
               <property name="driver" value="com.mysql.jdbc.Driver" />
               <property name="url"
                   value="jdbc:mysql://localhost:3306/spring?characterEncoding=utf-8" />
               <property name="username" value="root" />
               <property name="password" value="123456" />
           </dataSource>
       </environment>
   </environments>
   </configuration>
   ```

5. 日志文件

   ```properties

   log4j.rootLogger=DEBUG, stdout

   # Console output...

   log4j.appender.stdout=org.apache.log4j.ConsoleAppender
   log4j.appender.stdout.layout=org.apache.log4j.PatternLayout
   log4j.appender.stdout.layout.ConversionPattern=%5p [%t] - %m%n
   ```

6. mapper.xml文件

   ```xml
   <?xml version="1.0" encoding="UTF-8" ?>
   <!DOCTYPE mapper
   PUBLIC "-//mybatis.org//DTD Mapper 3.0//EN"
   "http://mybatis.org/dtd/mybatis-3-mapper.dtd">
   <!-- namespace：命名空间，用于隔离sql, 
   命名空间 user.findUserById
   -->
   <mapper namespace="user">
   <!-- 通过ID查询一个用户 
    id名字，namespace+id用来定位具体的sql   parameterType：参数类型   resultType：返回值，如果bean与数据库一一对应，则会自动映射   where id=#{v}，#{} 占位符，里面要写一个任意字符
   -->
   <select id="findUserById" parameterType="Integer" resultType="com.ali.pojo.User">
       select * from t_user where id=#{v}
   </select>
   </mapper>
   ```

   同时，在核心配置文件中配置

   ```xml
   <!-- mapper位置 -->
   <mappers>
       <mapper resource="../src/sqlMap/User.xml" />
   </mappers>
   ```

7. 测试

   ```java
   public class MybatisTest{

       @Test
       public void testMybatis() throws IOException {
           //加载核心文件
           String resource="sqlMapConfig.xml";
           InputStream resourceAsStream = Resources.getResourceAsStream(resource);
           //创建sqlSessionFactory
           SqlSessionFactory sqlSessionFactory=new SqlSessionFactoryBuilder().build(resourceAsStream);
           //创建sqlSession
           SqlSession session=sqlSessionFactory.openSession();
           //执行sql语句
           User user = session.selectOne("user.findUserById", 1);
           System.out.println(user);
       }
   ```

8. 根据名字模糊查询

   ```xml
   <!-- 根据名字模糊查询
           #{}  1.相当于？   =='' 会带单引号   2.里面的表示字符任意
           ${}     1.不带单引号    2.里面的字符必须为value
           resultType="com.pojo.User"  写的是list的泛型
        -->
   <select id="findUserByName" parameterType="String" resultType="com.ali.pojo.User">
       <!--  select * from t_user where name like '%${value}%'-->
       select * from t_user where name like "%"#{v}"%"
   </select>
   ```

   测试代码：`List<User> users = session.selectList("user.findUserByNames", "ba");`

9. 添加用户

   ```xml
   <insert id="insertUser" parameterType="com.bean.User">
           insert into t_user values(null,#{name},#{sex})
   </insert>
   ```

10. 添加用户返回id

    ```xml
    <insert id="insertUser" parameterType="com.ali.bean.User">
        
        <selectKey keyProperty="id" resultType="Integer" order="AFTER">
            select LAST_INSERT_ID()<!-- 这个是mysql提供的函数-->
        </selectKey>
        insert into t_user values(null,#{name},#{age})
    </insert>
    ```

    使用

    ```java
    User user=new User();
    user.setName("ali");
    user.setAge(24);
    int insert = openSession.insert("user.insertUser", user);
    openSession.commit();
    System.out.println(user.getId());
    ```

11. 更新用户

    ```xml
    <update id="updateUser" parameterType="com.bean.User">
        update t_user set name=#{name} where id=#{id}
    </update>
    ```

12. 删除用户

    ```xml
    <delete id="deleteUser" parameterType="com.bean.User">
            delete from t_user where id=#{id}
    </delete>
    ```

13. 结论

    - ```
      - #{}表示一个占位符号，通过#{}可以实现preparedStatement向占位符中设置值，自动进行java类型和jdbc类型转换。#{}可以有效防止sql注入。 #{}可以接收简单类型值或pojo属性值。 如果parameterType传输单个简单类型值，#{}括号中可以是value或其它名称。
      - ${}表示拼接sql串，通过${}可以将parameterType 传入的内容拼接在sql中且不进行jdbc类型转换， ${}可以接收简单类型值或pojo属性值，如果parameterType传输单个简单类型值，${} 括号中只能是value。
      ```

      - 单个简单类型  `#{}`可以写任意值或者`value`,如果是pojo，则要对应pojo中的属性值
      - 单个简单类型`${}`只能写value



#### Hibernate和MyBatis简单比较

- Mybatis和hibernate不同，它不完全是一个ORM框架，`因为MyBatis需要程序员自己编写Sql语句`。mybatis可以通过XML或注解方式灵活配置要运行的sql语句，并将java对象和sql语句映射生成最终执行的sql，最后将sql执行的结果再映射生成java对象。


- `Mybatis学习门槛低，简单易学，程序员直接编写原生态sql`，可严格控制sql执行性能，灵活度高，非常适合对关系数据模型要求不高的软件开发，例如互联网软件、企业运营类软件等，因为这类软件需求变化频繁，一但需求变化要求成果输出迅速。但是灵活的前提是mybatis无法做到数据库无关性，如果需要实现支持多种数据库的软件则需要自定义多套sql映射文件，工作量大。
- `Hibernate对象/关系映射能力强，数据库无关性好`，对于关系模型要求高的软件（例如需求固定的定制化软件）如果用hibernate开发可以节省很多代码，提高效率。但是Hibernate的学习门槛高，要精通门槛更高，而且怎么设计O/R映射，在性能和对象模型之间如何权衡，以及怎样用好Hibernate需要具有很强的经验和能力才行。



#### MyBatis开发方法

##### DAO开发方法

- dao层建立UserDao和UserDaoImpl

  ```java
  public class UserDaoImpl implements UserDao {

  //注入工厂
  private SqlSessionFactory sessionFactory;

  public UserDaoImpl(SqlSessionFactory sessionFactory) {
      this.sessionFactory = sessionFactory;
  }
  //通过用户ID查询一个用户
    @Override
  public User selectUserById(Integer id) {
      SqlSession openSession = sessionFactory.openSession();
      return openSession.selectOne("user.findUserById",id);
  }
  }
  ```

- 测试类

  ```java
  public class MybatisDaoTest {
  public SqlSessionFactory sqlSessionFactory;
  @Before
  public void before() throws IOException {
      String resource="sqlMapConfig.xml";
      InputStream in = Resources.getResourceAsStream(resource);
      sqlSessionFactory=new SqlSessionFactoryBuilder().build(in); 
  }
  @Test
  public void testDao() {
      UserDao userDao =new UserDaoImpl(sqlSessionFactory);
      User user = userDao.selectUserById(2);
      System.out.println(user);
  }
  }
  ```



##### Mapper动态代理开发

- 只写接口，实现类由mybatis生成

- 四个原则：Mapper接口开发需要遵循以下规范

  1、 Mapper.xml文件中的namespace与mapper接口的类路径相同。

  2、 Mapper接口方法名和Mapper.xml中定义的每个statement的id相同

  3、 Mapper接口方法的输入参数类型和mapper.xml中定义的每个sql 的parameterType的类型相同

  4、 Mapper接口方法的输出参数类型和mapper.xml中定义的每个sql的resultType的类型相同

- 示例

  - 接口

    ```java
    package com.ali.mapper;
    public interface MapperUser {
        //原则一：mapper.xml中的namespace要与mapper接口类路径相同
        //原则二：接口方法名与xml中id相同
        //原则三：接口的输入参数一致
        //原则四：接口方法返回类型一致
        public User findUserById(Integer id);
    }
    ```

  - mapper.xml文件

    ```xml
    <mapper namespace="com.mapper.MapperUser">
        <select id="findUserById" resultType="com.bean.User"
            parameterType="Integer">
            select * from t_user where id=#{v}
        </select>
    </mapper>
    ```

  - 测试类

    ```java
    public void fun1() throws IOException {
      String resource="sqlMapConfig.xml";
      InputStream in = Resources.getResourceAsStream(resource);
      SqlSessionFactory sqlSessionFactory=new SqlSessionFactoryBuilder().build(in);
      SqlSession sqlSession = sqlSessionFactory.openSession();
      //sqlSession生成实现类
      MapperUser userMapper = sqlSession.getMapper(MapperUser.class);
      User user = userMapper.findUserById(2);
      System.out.println(user);
    }
    ```

    ​

