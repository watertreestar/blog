---
title: MyBatis动态SQL和缓存
date: 2018-08-05 20:26:50
tags: [Java,MyBatis]
categories: 框架
---

#### 1.  什么是动态SQL

静态SQL：静态SQL语句在程序运行前SQL语句必须是确定的，SQL语句中涉及的表的字段名必须是存在的，静态SQL的编译是在程序运行前的。

动态SQL：动态SQL语句是在程序运行是被创建和执行的。

<!--more-->

#### 2. MyBatis中的动态SQL

为什么需要动态SQL?有时候需要根据实际传入的参数来动态的拼接SQL语句。

对于一些复杂的查询，我们可能会指定多个查询条件，但是这些条件可能存在也可能不存在,此时就需要根据用户指定的条件动态生成SQL语句。如果不使用持久层框架我们可能需要自己拼装SQL语句



MyBatis中用于实现动态SQL的元素主要有： 

- if 
- choose / when / otherwise 
- trim 
- where 
- set 


- foreach



#### 3. if标签



#### 4. choose标签



#### 5. trim标签



#### 6. set标签



#### 7. foreach标签

动态SQL的另一个常用的操作是需要对一个集合进行遍历，通常在构建in条件语句的时候

foreach标签还可以用于批量保存数据

```xml
<insert id="addEmps">
INSERT INTO tbl_employee(user_name,gender,email,d_id) VALUES
<foreach collection="emps" item="emp" separator=",">
(#{emp.userName},#{emp.gender},#{emp.email},#{emp.depart.id})
</foreach>
</insert>
```

```java
@Test
public void testGetEmployee(){
EmployeeMapper mapper = openSession.getMapper(EmployeeMapper.class);
List<Employee> emps = new ArrayList<Employee>();
emps.add(new Employee(0, 1, "allen", "allen@163.com", new Department(1)));
emps.add(new Employee(0, 0, "tom", "tom@163.com", new Department(2)));
emps.add(new Employee(0, 1, "mux", "mux@163.com", new Department(1)));
mapper.addEmps(emps);
}
```



#### 

#### 8. MyBatis缓存机制

MyBatis 包含一个非常强大的查询缓存特性,它可以非常方便地配置和定制。缓存可以极大的提升查询效率。
MyBatis系统中默认定义了两级缓存：一级缓存和二级缓存。



##### 1>  一级缓存

SqlSession级别的缓存，默认是开启的，不能关闭。与数据库同一次会话期间查询到的数据放在本地缓存中

使用以下代码测试缓存一级缓存

```java
@Test
public void testGetEmployee(){
    EmployeeMapper mapper = openSession.getMapper(EmployeeMapper.class);

    Employee emp = mapper.getEmployeeById(2);
    System.out.println(emp);
    Employee emp2 = mapper.getEmployeeById(2);
    System.out.println(emp2);

    System.out.println(emp == emp2);
}
```

当然也有一级缓存失效的时候，此时就需要查询数据库

- SqlSession不同
- SqlSession相同，查询条件不一致
- SqlSession相同，查询条件一致，但在两次查询期间有增删改操作
- SqlSession相同，手动清楚了一级缓存



##### 2>   二级缓存

基于namespace级别的缓存:一个namespace对应一个二级缓存

二级缓存可以跨越SqlSession

##### 3>  二级缓存的使用

1. 在MyBatis全局配置文件中配置

   ```xml
   <setting name="cacheEnabled" value="true"/>
   ```

2. mapper配置文件中配置二级缓存

   ```xml
   <cache eviction="FIFO" flushInterval="60000" readOnly="false" size="1024" type=""></cache>
   <!--
   eviction=“FIFO”：缓存回收策略：
   LRU –最近最少使用的：移除最长时间不被使用的对象。
   FIFO –先进先出：按对象进入缓存的顺序来移除它们。
   SOFT –软引用：移除基于垃圾回收器状态和软引用规则的对象。
   WEAK –弱引用：更积极地移除基于垃圾收集器状态和弱引用规则的对象。
   默认的是LRU。
   flushInterval：缓存刷新间隔
   缓存多长时间清空一次，默认不清空，设置一个毫秒值。
   size：引用数目，正整数
   代表缓存最多可以存储多少个对象，太大容易导致内存溢出
   readOnly：是否只读，true/false   
   true：只读缓存；mybatis认为所有从缓存中获取数据的操作都是只读操作，不会修改数据。
   mybatis为了加快获取速度，直接就会将数据在缓存中的引用交给用户。不安全，速度快。
   false：非只读:mybatis觉得获取的数据可能会被修改。
   mybatis会利用序列化&反序列化的技术克隆一份。安全，速度慢。
   type:指定自定义缓存的全类名
   实现cache接口即可！
   -->
   ```

   ​





