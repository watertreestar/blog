---
title: SSM整合
date: 2018-07-15 18:30:54
tags: [Java,SpringMVC]
categories: 框架
---
####　１．SpringMVC入门示例

1. 导入包

   ![](/img/独立运行Jar包.png)

2. web.xml中配置SpringMVC 核心控制器

   <!--more-->

   ```xml
   <!-- 配置SpringMVC 核心控制器 -->
   <servlet>
       <servlet-name>springmvc</servlet-name>
       <servlet-class>org.springframework.web.servlet.DispatcherServlet</servlet-class>
       <init-param>
           <param-name>contextConfigLocation</param-name>
           <param-value>classpath:springmvc.xml</param-value>
       </init-param>
   </servlet>
   <servlet-mapping>
       <servlet-name>springmvc</servlet-name>  
       <url-pattern>/</url-pattern>
   </servlet-mapping>

   ```

   ​

3. 创建SpringMVC配置文件

   springmvc.xml

   ```xml
   <?xml version="1.0" encoding="UTF-8"?>
   <beans xmlns="http://www.springframework.org/schema/beans"
          xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
          xmlns:context="http://www.springframework.org/schema/context" 
          xmlns:aop="http://www.springframework.org/schema/aop" xsi:schemaLocation="
                                                                                    http://www.springframework.org/schema/beans http://www.springframework.org/schema/beans/spring-beans.xsd
                                                                                    http://www.springframework.org/schema/context http://www.springframework.org/schema/context/spring-context.xsd
                                                                                    http://www.springframework.org/schema/aop http://www.springframework.org/schema/aop/spring-aop.xsd"> <!-- bean definitions here -->
       
       <context:component-scan base-package="com.ranger.springMVC.helloSpringMVC">/context:component-scan

   </beans>

   ```

4. 编写Controller代码


   ```java
      @Controller
      public class HelloController {
          @RequestMapping("/hello")
          public ModelAndView hello(){
              System.out.println("HelloController.hello()");
              ModelAndView mav = new ModelAndView();
              mav.addObject("msg","hello ,　SpringMVC");
              mav.setViewName("/WEB-INF/jsp/hello.jsp");
              return mav;
          }
      }
   ```

   ​

   ​

   ​

   ​

5. 访问测试

   浏览器访问`localhost:8080/01-SpringMVC/hello`

   ![](/img/入门示例结果.png)

#### 2. 配置详解



1. Dispatcherservlet

　　DispatcherServlet是前置控制器，配置在web.xml文件中的。拦截匹配的请求，Servlet拦截匹配规则要自已定义，把拦截下来的请求，依据相应的规则分发到目标Controller来处理，是配置spring MVC的第一步。



2. 以上出现的注解

- @Controller 负责注册一个bean 到spring 上下文中
- @RequestMapping 注解为控制器指定可以处理哪些 URL 请求



####  3. SpringMVC执行流程图（结构图）

![](/img/SpringMVC结构图.png)

解释：

1.用户发送请求至 前端控制器DispatcherServlet。

2.前端控制器DispatcherServlet收到请求后调用处理器映射器HandlerMapping。

3.处理器映射器`HandlerMapping`根据请求的Url找到具体的处理器，生成处理器对象Handler及处理器拦截器HandlerIntercepter（如果有则生成）一并返回给前端控制器DispatcherServlet。

4.前端控制器DispatcherServlet通过处理器适配器HandlerAdapter调用处理器Controller。

5.执行处理器（Controller，也叫后端控制器）

6.处理器Controller执行完后返回ModelAnView。

7.处理器适配器`HandlerAdapter`将处理器Controller执行返回的结果ModelAndView返回给前端控制器DispatcherServlet。

8.前端控制器DispatcherServlet将ModelAnView传给视图解析器ViewResolver。

9.视图解析器`ViewResolver`解析后返回具体的视图View。

10.前端控制器DispatcherServlet对视图View进行渲染视图（即：将模型数据填充至视图中）

11.前端控制器DispatcherServlet响应用户。



#### 4. SpringMVC常用注解

@Controller

　　负责注册一个bean 到spring 上下文中
@RequestMapping

　　注解为控制器指定可以处理哪些 URL 请求
@RequestBody

　　该注解用于读取Request请求的body部分数据，使用系统默认配置的HttpMessageConverter进行解析，然后把相应的数据绑定到要返回的对象上 ,再把HttpMessageConverter返回的对象数据绑定到 controller中方法的参数上

@ResponseBody

　　 该注解用于将Controller的方法返回的对象，通过适当的HttpMessageConverter转换为指定格式后，写入到Response对象的body数据区

@ModelAttribute 　　　

　　在方法定义上使用 @ModelAttribute 注解：Spring MVC 在调用目标处理方法前，会先逐个调用在方法级上标注了@ModelAttribute 的方法

　　在方法的入参前使用 @ModelAttribute 注解：可以从隐含对象中获取隐含的模型数据中获取对象，再将请求参数 –绑定到对象中，再传入入参将方法入参对象添加到模型中 

@RequestParam　

　　在处理方法入参处使用 @RequestParam 可以把请求参 数传递给请求方法

@PathVariable

　　绑定 URL 占位符到入参
@ExceptionHandler

　　注解到方法上，出现异常时会执行该方法
@ControllerAdvice

　　使一个Contoller成为全局的异常处理类，类中用@ExceptionHandler方法注解的方法可以处理所有Controller发生的异常





#### 5. SSM 整合配置

整合思路：

- DAO层：
  - SqlMapConfig.xml   (空文件即可，不过需要包含头文件)
  - applicationContext-dao.xml
    - 数据库连接池
    - SqlSessionFactory对象
    - 配置Mapper文件扫描器
- Service层
  - applicationContext-service.xml    配置包扫描 ，扫描@Service
  - applicationContex-tx.xml   配置事务相关
- Controller层
  - springmvc.xml
    - 配置包扫描   扫描@Controller类
    - 配置注解驱动
    - 配置视图解析器
- web.xml
  - 配置Spring容器监听器
  - 配置前端控制器

