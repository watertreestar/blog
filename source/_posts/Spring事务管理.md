---
title: Spring 事务管理
date: 2018-07-7 20:05:03
tags: [Java,Spring,事务]
categories: 框架
---

####  1. 事务基本概述

##### 事务的特性

逻辑上的一组操作-，组成这组事务的各个单元，要么全部成功，要么全部失败

事务的特性（ACID）

- 原子性：事务不可分割
- 一致性：事务执行前后数据完整性保证一致
- 隔离性：一个事务不能干扰其它事务
- 持久性：事务一旦成功，数据就持久化到数据库




<!--more-->


##### 不考虑隔离性（使用锁）引发的问题

事务的并发引发的问题

- 读问题
  - 脏读：一个事务读取另一个事务未提交的数据
  - 不可重复读：一个事务读取到另一个事务update的数据，导致两次读取的结果不一致
  - 虚读：一个事务读取到另一个事务insert或者delete的数据，导致两次读取的结果不一致
- 写问题：丢失更新

##### 不同的锁引发不同类型的事务（事务隔离级别）

1. 不支持事务
2. read_uncommitted   未提交读，**不能解决任何读问题**
3. read_committed     已提交读  ，不能读取未提交的事务，**能够解决脏读**
4. repeateable_read    可重复读  ，能够保证两次读取的数据是一致的，**能解决脏读和不可重复读**
5. serializable      可序列化  ，事务的最高级别，**可以解决脏读、不可重复读和虚读**



#### 2. Spring事务管理API

##### 1. 平台事务管理器`PlateformTransactionManager`

`PlateformTransactionManager`是一个接口

- DataSourceTransactionManager:使用JDBC管理事务
- HibernateTransactionManager:使用Hibernate管理事务

##### 2. 事务定义信息`TransactionDefinition`

- 事务定义：用于定义事务的相关信息：隔离级别，传播信息，超时信息，是否只读

##### 3. 事务状态`TransactionStatus`

用于记录事务在执行过程中，事务的状态的对象

##### 4. 关系

`事务管理器`更具`事务定义`来管理事务，在管理过程中产生`事务状态`



#### 3. Spring事务的传播行为

事务的传播行为主要用来解决业务层方法相互调用的问题

Spring提供了七中的事务传播行为

- 保证多个操作在同一个事务中

  - **PROPAGATION_REQUIRED**:默认值，如果A中有事务，则使用A中的事务，如果没有事务则创建一个事务

  - PROPAGATION_SUPPORTS   如果A中有事务，则使用A中的事务，如果没有则不使用事务

  - PROPAGATION_MANDATORY  如果A中有事务，则使用A中的事务，如果没有，则报异常

- 保证多个操作在不同事务中

  -  **PROPAGATION_REQUIRES_NEW**：默认值，如果A中有事务，将A中 的事务挂起，创建新的事务，只包含自身操作，如果A中没有事务，则创建新事务包含自身操作

  - PROPAGATION_NOT_SUPPORTE    如果A中有事务，将A的事务挂起，不使用事务

  - PROPAGATION_NEVER   如果A中有事务，报异常

  - ​

- 嵌套式事务

  - ​

#### 4. 编程式事务

##### 1. 配置平台事务管理器

```xml
<!-- 配置事务管理器 -->
<bean name="transactionManager" class="org.springframework.jdbc.datasource.DataSourceTransactionManager">
    <property name="dataSource" ref="dataSource"></property>
</bean>
```

##### 2. 配置事务模板

```xml
<!-- 配置事务管理模板，简化事务控制 -->
<bean name="transactionTemplate" class="org.springframework.transaction.support.TransactionTemplate">
    <property name="transactionManager" ref="transactionManager"></property>
</bean>
```

##### 3. 注入业务层

```xml
<!-- 配置AccountService -->
<bean name="accountService" class="com.ranger.spring.tx.service.impl.AccountServiceImpl">
    <property name="accountDao" ref="accountDao"></property>
    <property name="transactionTemplate" ref="transactionTemplate"></property>
</bean>
```

##### 4. 使用事务模板开启事务

```java
@Override
public void transfer(Integer from, Integer to, double money) {
    transactionTemplate.execute(new TransactionCallbackWithoutResult() {

        @Override
        protected void doInTransactionWithoutResult(TransactionStatus arg0) {

            accountDao.increaseMoney(to, money);

            // 开启 / 关闭 异常
            int i = 1/0;

            accountDao.decreaseMoney(from, money);
        }
    });
}
```



#### 5. 声明式事务管理（常用）通过配置实现  使用AOP

##### 1. XML配置使用声明式事务管理

>  不必再业务层添加事务管理代码

1. 导入AOP相关的包

   ![](/img/声明式事务导包的jar包.png)



2. 配置事务管理器

   ```xml
   <!-- 配置事务管理器 -->
   <bean name="transactionManager" class="org.springframework.jdbc.datasource.DataSourceTransactionManager">
       <property name="dataSource" ref="dataSource"></property>
   </bean>
   ```

3. 配置事务管理通知

   ```xml
   <!-- 配置通知（增强） -->
   <tx:advice id="txAdvice" transaction-manager="transactionManager" >
       <tx:attributes>
           <!-- <tx:method name="save*" propagation="REQUIRED" isolation="DEFAULT"/>
       <tx:method name="update*" propagation="REQUIRED" isolation="DEFAULT"/>
       <tx:method name="delete*" propagation="REQUIRED" isolation="DEFAULT"/>
       <tx:method name="find*" read-only="true"/> -->
           <tx:method name="*" propagation="REQUIRED"/>
       </tx:attributes>
   </tx:advice>
   ```

4. 织入

   ```xml
   <!-- 织入（完成对目标对象的代理） -->
   <aop:config>
       <aop:pointcut expression="execution(* com.ranger.spring.tx.service.impl.AccountServiceImpl.transfer(..))" id="transferPointCut"/>
       <aop:advisor advice-ref="txAdvice" pointcut-ref="transferPointCut"/>

   </aop:config>
   ```

   ​

##### 2. 注解使用声明式事务

> 只需配置相应bean 和开启注解，配置注解

1. 配置事务管理器

   ```xml
   <!-- 配置事务管理器 -->
   <bean name="transactionManager" class="org.springframework.jdbc.datasource.DataSourceTransactionManager">
       <property name="dataSource" ref="dataSource"></property>
   </bean>
   ```

   ​

2. 配置文件中开启事务注解、

   ```xml
   <!-- 开启事务注解 -->
   <tx:annotation-driven transaction-manager="transactionManager"/>
   ```

3. 类上配置注解

   ```java

   @Transactional(isolation=Isolation.DEFAULT)   
   public class AccountServiceImpl implements AccountService {
   	
   	private AccountDao accountDao;
   	
   	private TransactionTemplate transactionTemplate;
   	
   	public void setAccountDao(AccountDao accountDao) {
   		this.accountDao = accountDao;
   	}
   	
   	

   	public void setTransactionTemplate(TransactionTemplate transactionTemplate) {
   		this.transactionTemplate = transactionTemplate;
   	}
       
       @Override
   	public void transfer(Integer from, Integer to, double money) {

           accountDao.increaseMoney(to, money);

           // 开启 / 关闭 异常
           int i = 1/0;

           accountDao.decreaseMoney(from, money);

   	}

   }
   ```



   	



