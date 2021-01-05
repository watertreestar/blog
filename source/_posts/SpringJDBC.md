---
title: Spring JDBC入门
date: 2018-07-7 10:20:11
tags: [Java,Spring]
categories: 框架
---

#### 1. Spring JDBC 模板

Spring 是EE的一站式开发框架，对持久层同样提供了支持：ORM模块和`JDBC模板`

Spring 提供了很多模板简化了开发

- spring中提供了一个可以操作数据库的对象，对象封装了jdbc技术。
- 与DBUtils中QueryRunner非常相似



<!--more-->

#### 2. JDBC模板的使用

#####　基本使用方法



1. 创建数据库

   ```mysql
   mysql> show create table account;

   | Table   | Create Table| account | 
   CREATE TABLE `account` (
     `id` int(11) NOT NULL AUTO_INCREMENT,
     `name` char(10) DEFAULT NULL,
     `money` double DEFAULT NULL,
     PRIMARY KEY (`id`)
   ) ENGINE=InnoDB DEFAULT CHARSET=utf8
   ```

2. ```java
   public class JDBCTemplateTest {
   	@Test
   	public void testadd(){
   		// 创建连接池
   		DriverManagerDataSource dataSource = new DriverManagerDataSource();
   		dataSource.setDriverClassName("com.mysql.jdbc.Driver");
   		dataSource.setUrl("jdbc:mysql://localhost:3306/spring");
   		dataSource.setUsername("cyp");
   		dataSource.setPassword("cyp");
   		
   		// 创建JDBC 模板
   		JdbcTemplate jdbcTemplate = new JdbcTemplate(dataSource);
   		jdbcTemplate.update("insert into account values(null,?,?)", "陈亚平",2000);
   		
   	}
   	
   }
   ```

3. ```mysql
   mysql> select *from account;
   +----+-----------+-------+
   | id | name      | money |
   +----+-----------+-------+
   |  1 | 陈亚平    |  2000 |
   +----+-----------+-------+
   1 row in set (0.00 sec)
   ```

#####　整合Spring（spring管理dataSource和JdbcTemplate）

1. Spring 配置文件配置

   ```xml
   <bean name="dataSource" class="org.springframework.jdbc.datasource.DriverManagerDataSource">
   			<property name="driverClassName" value="com.mysql.jdbc.Driver"></property>
   			<property name="url" value="jdbc:mysql://localhost:3306/spring"></property>
   			<property name="username" value="cyp"></property>
   			<property name="password" value="cyp"></property>
   </bean>
   <bean name="jdbcTemplate" class="org.springframework.jdbc.core.JdbcTemplate">
       <property name="dataSource" ref="dataSource"></property>
   </bean>
   ```

2. 测试类

   ```java

   @RunWith(SpringJUnit4ClassRunner.class)
   @ContextConfiguration("classpath:applicationContext.xml")
   public class JDBCTemplateTestWithSpring {
   	@Resource(name="jdbcTemplate")
   	private JdbcTemplate jdbcTemplate;
   	
   	@Test
   	public void test1(){
   		jdbcTemplate.update("insert into account values(null,?,?)", "王红琳",2000);
   	}
   }

   ```

   ​

##### c3p0 连接池的使用

1. 导入包

   `c3p0.jar`

2. Spring中配置连接池

   ```xml
   <bean name="dataSource" class="com.mchange.v2.c3p0.ComboPooledDataSource">
   			<property name="driverClass" value="com.mysql.jdbc.Driver"></property>
   			<property name="jdbcUrl" value="jdbc:mysql://localhost:3306/spring"></property>
   			<property name="user" value="cyp"></property>
   			<property name="password" value="cyp"></property>
   		</bean>
   ```

3. 显示结果

   ![](/img/Spring中使用c3p0连接池启动信息.png)



##### 使用属性文件配置连接池

1. 创建属性文件jdbc.properteis

   ```properties
   jdbc.driver=com.mysql.jdbc.Driver
   jdbc.url=jdbc:mysql://localhost:3306/spring
   jdbc.user=cyp
   jdbc.password=cyp
   ```

2. 配置文件中配置属性文件

   ``` xml
   <!-- 配置属性文件 -->
   <!-- 第一种方式：配置一个bean  ,较少使用 -->
   <bean class="org.springframework.beans.factory.config.PropertyPlaceholderConfigurer">
       <property name="location" value="classpath:jdbc.properteis"/>		
    </bean> 
   <!-- 第二种方式  使用context 标签-->
   <context:property-placeholder location="classpath:jdbc.properteis"/><!-- 配置属性文件 -->

   ```

3. 使用配置

   ​

   ```xml
   <!-- 使用c3p0 连接池-->
   <bean name="dataSource" class="com.mchange.v2.c3p0.ComboPooledDataSource">
       <property name="driverClass" value="${jdbc.driver}"></property>
       <property name="jdbcUrl" value="${jdbc.url}"></property>
       <property name="user" value="${jdbc.user}"></property>
       <property name="password" value="${jdbc.password}"></property>
   </bean>
   ```

####　3. 模板的 CRUD操作

1. 编写bean

   ```java
   public class Account {
   	private int id;
   	private String name;
   	private double money;
   	public int getId() {
   		return id;
   	}
   	public void setId(int id) {
   		this.id = id;
   	}
   	public String getName() {
   		return name;
   	}
   	public void setName(String name) {
   		this.name = name;
   	}
   	public double getMoney() {
   		return money;
   	}
   	public void setMoney(double money) {
   		this.money = money;
   	}
   	@Override
   	public String toString() {
   		return "Account [id=" + id + ", name=" + name + ", money=" + money + "]";
   	}
   	
   	
   }
   ```

2. 编写AccountDaoImpl实现类,实现基本操作

   ```java
   public class AccountDaoImpl implements AccountDao{
   	
   	private JdbcTemplate jdbcTemplate;

   	public void setJdbcTemplate(JdbcTemplate jdbcTemplate) {
   		this.jdbcTemplate = jdbcTemplate;
   	}

   	@Override
   	public void add(Account account) {
   		
   		String sql = "insert into account values(null,?,?)";
   		jdbcTemplate.update(sql, account.getName(),account.getMoney());
   	}

   	@Override
   	public void delete(Integer id) {
   		
   		String sql = "delete from account where id = ?";
   		jdbcTemplate.update(sql, id);
   	}

   	@Override
   	public void update(Account account) {
   		String sql = "update account set name=? ,money=? where id=?";
   		jdbcTemplate.update(sql, account.getName(),account.getMoney(),account.getId());
   		
   	}

   	@Override
   	public Account find(Integer id) {
   		String sql = "select * from account where id = ?";
   		return jdbcTemplate.queryForObject(sql, new RowMapper<Account>(){
   			@Override
   			public Account mapRow(ResultSet rs, int arg1) throws SQLException {
   				Account account = new Account();
   				account.setId(rs.getInt("id"));
   				account.setName(rs.getString("name"));
   				account.setMoney(rs.getDouble("money"));
   				return account;
   			}
   		}, id);
   		
   	}

   	@Override
   	public int getTotalCount() {
   		String sql="select count(*) from account";
           Integer count = jdbcTemplate.queryForObject(sql, Integer.class);
           return count;
   		
   	}

   }

   ```

3. 配置文件

   ```xml
   <context:property-placeholder location="classpath:jdbc.properteis"/>
   <!-- 使用c3p0 连接池-->
   <bean name="dataSource" class="com.mchange.v2.c3p0.ComboPooledDataSource">
       <property name="driverClass" value="${jdbc.driver}"></property>
       <property name="jdbcUrl" value="${jdbc.url}"></property>
       <property name="user" value="${jdbc.user}"></property>
       <property name="password" value="${jdbc.password}"></property>
   </bean>

   <!-- 配置JdbcTemplate -->
   <bean name="jdbcTemplate" class="org.springframework.jdbc.core.JdbcTemplate">
       <property name="dataSource" ref="dataSource"></property>
   </bean>

   <!-- 配置UserDao -->
   <bean name="accountDao" class="com.ranger.spring.jdbc.dao.impl.AccountDaoImpl">
       <property name="jdbcTemplate" ref="jdbcTemplate"></property>
   </bean>
   ```

4. 编写测试类和测试方法

   ```java
   @RunWith(SpringJUnit4ClassRunner.class)
   @ContextConfiguration("classpath:applicationContext.xml")
   public class AccountDaoTest {
   	@Resource(name="accountDao")
   	private AccountDao accountDao;
   	@Test
   	public void add(){
   		Account account = new Account();
   		account.setName("小风");
   		account.setMoney(2000);
   		accountDao.add(account);
   	} 
   	
   	@Test
   	public void delete(){
   		
   		accountDao.delete(2);
   	} 
   	
   	@Test
   	public void update(){
   		Account account = new Account();
   		account.setId(4);
   		account.setName("小王");
   		account.setMoney(2000);
   		accountDao.update(account);
   	}
   	
   	@Test
   	public void find(){
   		
   		Account account = accountDao.find(1);
   		System.out.println(account);
   	}
   	
   	@Test
   	public void getTotal(){
   		
   		int count = accountDao.getTotalCount();
   		System.out.println(count);
   	}
   }

   ```



