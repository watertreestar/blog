---
title: Spring AOP入门
date: 2018-07-5 21:44:43
tags: [Java,Spring]
categories: 框架
---

#### 1. AOP概述

在软件业，AOP为Aspect Oriented Programming的缩写，意为：[面向切面编程](https://baike.baidu.com/item/%E9%9D%A2%E5%90%91%E5%88%87%E9%9D%A2%E7%BC%96%E7%A8%8B)，通过[预编译](https://baike.baidu.com/item/%E9%A2%84%E7%BC%96%E8%AF%91)方式和运行期动态代理实现程序功能的统一维护的一种技术。AOP是[OOP](https://baike.baidu.com/item/OOP)的延续，是软件开发中的一个热点，也是[Spring](https://baike.baidu.com/item/Spring)框架中的一个重要内容，是[函数式编程](https://baike.baidu.com/item/%E5%87%BD%E6%95%B0%E5%BC%8F%E7%BC%96%E7%A8%8B)的一种衍生范型。利用AOP可以对业务逻辑的各个部分进行隔离，从而使得业务逻辑各部分之间的[耦合度](https://baike.baidu.com/item/%E8%80%A6%E5%90%88%E5%BA%A6)降低，提高程序的可重用性，同时提高了开发的效率。    --来自百度

<!--more-->



####  2. Spring中的AOP

- Spring能够为容器中管理的对象生成动态代理对象
- 以前我们要使用动态代理，我们需要自己调用下面的方法生成对象`Proxy.newProxyInstance(xx,xx,xx)` 生成代理对象，现在Spring能够帮我们生成代理对象

#### 3. Spring 中AOP实现原理

spring 的AOP 是使用动态代理实现的

两种动态代理方式：

1. JDK 提供的动态代理

   - 被代理对象必须要实现实现**接口**，才能产生代理对象。如果没有接口不能使用此动态代理技术。

2. cglib动态代理

   - 第三方代理技术，cglib代理，可以对任何类实现代理，代理的原理是对目标对象进行**继承**（生成子类）代理。如果目标对象被final修饰，该类无法被cglib代理。

     ```java
     // 使用cglib来动态代理
     public class CglibProxy {
     	private CustomerDao customerDao;
     	public CglibProxy(CustomerDao customerDao) {
     		this.customerDao = customerDao;
     	}
     	
     	public CustomerDao crateProxy(){
     		Enhancer enhancer = new Enhancer();
     		enhancer.setSuperclass(customerDao.getClass());
     		enhancer.setCallback(new MethodInterceptor() {
     			
     			@Override
     			public Object intercept(Object proxy, Method method, Object[] args, MethodProxy methodProxy) throws Throwable {
     				if("save".equals(method.getName())){
     					// 增强
     					System.out.println("权限验证");
     					return methodProxy.invokeSuper(proxy, args);
     				}
     				return methodProxy.invokeSuper(proxy, args);
     			}
     		});
     		// 返回代理的对象
     		return (CustomerDao)enhancer.create();
     	}
     }
     ```

     测试

     ```java
     @Test
     	public void test(){
     		CustomerDao customerDao = new CustomerDao();
     		CustomerDao proxyCustomer = new CglibProxy(customerDao).crateProxy();
     		proxyCustomer.save();
     		proxyCustomer.delete();
     		proxyCustomer.update();
     		proxyCustomer.find();
     	}
     ```

     输出

     ```
     权限验证
     CustomerDao.save()
     CustomerDao.delete()
     CustomerDao.update()
     CustomerDao.find()
     ```

#### 4. AOP 相关术语

- JoinPoint(连接点):在目标对象中，所有可以增强的方法。
- PointCut(切入点)：目标对象，已经增强的方法。
- Advice(通知/增强)：增强的代码
- Target(目标对象)：被代理对象
- WeAVing(织入):将通知应用到切入点的过程
- Proxy(代理)：将通知织入到目标对象之后，形成代理对象
- Aspect(切面)：多个切入点和多个通知的组合



#### 5. AOP开发入门（AspectJ  xml方式）

1. 导入开发包

   ![](/img/AOP相关包.png)

2. 引入配置文件

   ```xml
   <?xml version="1.0" encoding="UTF-8"?>
   <beans xmlns="http://www.springframework.org/schema/beans"
       xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
       xmlns:aop="http://www.springframework.org/schema/aop" xsi:schemaLocation="
           http://www.springframework.org/schema/beans http://www.springframework.org/schema/beans/spring-beans.xsd
           http://www.springframework.org/schema/aop http://www.springframework.org/schema/aop/spring-aop.xsd"> <!-- bean definitions here -->

   </beans>
   ```

3.  准备目标类

   ```java
   public class UserServiceImpl implements UserService {
   	@Override
   	public void save() {
   		System.out.println("UserServiceImpl.save()");
   	}
   	@Override
   	public void find() {
   		System.out.println("UserServiceImpl.find()");
   	}
   	@Override
   	public void update() {
   		System.out.println("UserServiceImpl.update()");
   	}
   	@Override
   	public void delete() {
   		System.out.println("UserServiceImpl.delete()");
   	}
   }
   ```

4. 配置文件中配置目标对象（bean）

   ```xml
   	<bean name="userService" class="com.ranger.apectjAOP.UserServiceImpl"></bean>
   ```

5. 配置文件中配置切面对象

   ```xml
   <!-- 切面对象配置 -->
   	<bean name="myAspectXML" class="com.ranger.apectjAOP.MyAspectXML"></bean>
   ```

6. 完成目标对象的代理

   ```xml
   <!-- 完成对目标对象的代理 -->
   	<aop:config>
   		<aop:pointcut expression="execution(* com.ranger.apectjAOP.UserServiceImpl.save(..))" id="pointcut1"/>
   		<aop:aspect ref="myAspectXML">
   			<aop:before method="checkPriv" pointcut-ref="pointcut1"/>
   		</aop:aspect>
   	</aop:config>
   ```

7. 测试

   ```java
   @Test
   	public void test1(){
   		ApplicationContext applicationContext = new ClassPathXmlApplicationContext("applicationContext.xml");
   		UserService userService = (UserService) applicationContext.getBean("userService");
   		userService.save();
   		
   	}

   输出：
       权限验证
       UserServiceImpl.save()

   ```



#### 6. 通知的类型

##### 1. 前置通知：目标方法执行前

```xml
<aop:before method="checkPriv" pointcut-ref="pointcut1"/>   <!-- application.xml中配置-->
```

切面类

```java

public class MyAspectXML {
	public void checkPriv(JoinPoint joinPoint){
		System.out.println("权限验证"+joinPoint);
	}
	
	public void afterReturning(Object result){
		System.out.println("日志记录........"+result);
	}
	
	
	// 环绕通知
	public Object around(ProceedingJoinPoint pjp) throws Throwable  {
        System.out.println("这是环绕通知之前的部分！");
        Object proceed = pjp.proceed(); 
        System.out.println("这是环绕通知之后的部分！");
        return proceed;    // 返回值
    }
	
	
	// 最终通知：出现异常也会调用
	public void after() {
        System.out.println("这是后置通知(出现异常也会调用)");
    }
	
	public void afterException() {
        System.out.println("异常出现了！");
    }
}

```

切入点的配置

```xml
<aop:config>
		<!-- 切入点 -->
		<aop:pointcut expression="execution(* com.ranger.apectjAOP.UserServiceImpl.save(..))" id="pointcut1"/>
		<aop:pointcut expression="execution(* com.ranger.apectjAOP.UserServiceImpl.delete(..))" id="pointcut2"/>
		<aop:pointcut expression="execution(* com.ranger.apectjAOP.UserServiceImpl.update(..))" id="pointcut3"/>
		<aop:pointcut expression="execution(* com.ranger.apectjAOP.UserServiceImpl.find(..))" id="pointcut4"/>
		
	</aop:config>
```



##### 2. 后置通知：目标方法执行后

```xml
<!--returning 属性设置连接点的返回值，这个返回值可以在通知中的方法参数中获取 -->
<aop:after-returning method="afterReturning" pointcut-ref="pointcut2" returning="result"/>
```



##### 3. 环绕通知：目标方法执行前执行后

```xml
<aop:around method="around" pointcut-ref="pointcut3" />
```



##### 4. 异常抛出通知：程序抛出异常时，进行的操作

```xml
<aop:after-throwing method="afterException" pointcut-ref="pointcut4"/>
```



##### 5. 最终通知：无论是否有异常，都会执行

```xml
<aop:after method="after" pointcut-ref="pointcut4"/>
```



##### 6. 引介通知

> 以上配置可以使用注解开发



#### 7. Spring切入点表达式

- 语法
  - 基于execution()函数完成
  - 格式：[访问修饰符] 返回值类型 包名.类名.方法名(参数)
  - 例如：
    - `public void com.ranger.spring.userDao.save(..)`
    - `* *.*.*Dao.save(..)`任意包下的以Dao结尾的save方法
    - `* com.ranger.spring.userDao+.save(..)`com.ranger.spring包下userDao类及其子类的save方法
    - `* com.ranger.spring..*.*(..)` com.ranger.spring包及其子包下的所有类的所用方法


#### 8. Spring 基于AspectJ的AOP注解开发

1. 配置文件中开启注解

   ![](/img/AOP注解开发配置.png)

2. 前置增强

   ![](/img/注解前置增强配置.png)

3. 切入点注解

   ![](/img/切入点配置.png)



#### 9. Spring 整合Junit

1. 导入依赖包

   ![](/img/Spring-test.png)

2. 在测试单元中加入注解

   ![](/img/SpringJunit测试注解配置.png)

