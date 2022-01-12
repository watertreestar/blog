---
title: SpringBoot自动配置的魔法
date: 2019-02-19 19:51:02
tags: [springboot,spring]
categories: spring boot
---


### 从@SpringBootApplication注解说起

`SpringBoot`会根据类路径下的类自动配置，省去了编写繁琐的`xml`配置文件。原本基于`xml`配置`bean`的方式编程基于Java代码，并且可以条件化配置，根据不同的场景配置也随之不同。是不是很智能

<!--more-->

为了清楚`SpringBoot`自动配置的原理，我们从最简单的`SpringBoot`的启动类说起，看一个简单的启动实例

```java
@SpringBootApplication
public class Application {
    public static void main(String[] args) {
        SpringApplication.run(Application.class);
    }
}
```

`SpringBoot`应用的启动很简单，就是一个`main`方法，然后执行`SpringApplication`的run方法。先不关心run方法是怎么执行的。我们先看`SpringBoot`应用的核心注解`@SpringBootApplication`

```java
@Target(ElementType.TYPE)
@Retention(RetentionPolicy.RUNTIME)
@Documented
@Inherited
@SpringBootConfiguration
@EnableAutoConfiguration
@ComponentScan(excludeFilters = {
		@Filter(type = FilterType.CUSTOM, classes = TypeExcludeFilter.class),
		@Filter(type = FilterType.CUSTOM, classes = AutoConfigurationExcludeFilter.class) })
public @interface SpringBootApplication {
	.....
}
```

查看该注解的源代码可知，这是一个组合注解。

分别查看每个注解的含义

`@SpringBootConfiguration`

```java
@Target({ElementType.TYPE})
@Retention(RetentionPolicy.RUNTIME)
@Documented
@Configuration
public @interface SpringBootConfiguration {
}

```

可知该注解就是`@Configuration`注解，该注解什么这个一个配置类，在`SpringBoot`中很常见。

`@CompontScan`注解指定哪些包扫描或者不扫描。

使`SpringBoot`应用拥有自动配置魔法的注解是`@EnableAutoConfiguraion`。该注解可以让SpringBoot根据类路径中的依赖为当前项目进行自动配置 ，所以SpringBoot可以自动配置主要是因为SpringBoot应用上的@EnableAutoConfiguraion注解来实现的，所以在启动类上加入该注解，就会开启自动配置。

那么，这个注解是如何实现自动化配置的呢。接下来我们要一探究竟。

### 自动配置背后的注解

```java
@Target(ElementType.TYPE)
@Retention(RetentionPolicy.RUNTIME)
@Documented
@Inherited
@AutoConfigurationPackage
@Import(AutoConfigurationImportSelector.class)
public @interface EnableAutoConfiguration {
	.....
}
```

该注解也是一个组合注解，这里有一个`@Import(AutoConfigurationImportSelector.class)`，那么`@Import`注解的作用是什么呢，查看`@Import`的源码注释，写着`Indicates one or more {@link Configuration @Configuration} classes to import.Provides functionality equivalent to the {@code <import/>} element in Spring XML.`，注释表明这个注解指明了要导入的配置类，在功能上和`Spring XML配置`中的`<import>`相同

那这里`@Import`导入的一个`AutoConfigurationImportSelector`又什么作用呢？根据下面注释中的内容可以知道，`@Import`允许导入`ImportSelector,ImportBeanDefinitionRegistrar`的实现类，还有普通的类（在版本4.2后）

```
Allows for importing {@code @Configuration} classes, {@link ImportSelector} and {@link ImportBeanDefinitionRegistrar} implementations, as well as regular component classes (as of 4.2; analogous to {@link AnnotationConfigApplicationContext#register}).
```

> 到了这里，说一个与@Import注解相关的东西，Spring框架本身提供了几个以Enable打头的注解，根据名字可知这是开启某个功能，比如`@EnableScheduling`、`@EnableCaching`、`@EnableMBeanExport`等，`@EnableAutoConfiguration`的理念和这些注解其实是相同的的。 

> `@EnableScheduling`是通过`@Import`将Spring调度框架相关的bean定义都加载到IoC容器。`@EnableMBeanExport`是通过`@Import`将JMX相关的bean定义加载到IoC容器。
>
> `@EnableAutoConfiguration`也是借助`@Import`的帮助，将所有符合自动配置条件的bean定义加载到IoC容器。

接下来关注EnableAutoConfigurationImportSelector 这个作用是什么。主要就是使用Spring 4 提供的的`SpringFactoriesLoader`工具类。通过`SpringFactoriesLoader.loadFactoryNames()`读取了ClassPath下面的`META-INF/spring.factories`文件 

`EnableAutoConfigurationImportSelector`通过读取`spring.factories`中的key为`org.springframework.boot.autoconfigure.EnableAutoConfiguration`的值。如`spring-boot-autoconfigure-1.5.1.RELEASE.jar`中的`spring.factories`文件包含以下内容：

```properties
org.springframework.boot.autoconfigure.EnableAutoConfiguration=\
org.springframework.boot.autoconfigure.admin.SpringApplicationAdminJmxAutoConfiguration,\
org.springframework.boot.autoconfigure.aop.AopAutoConfiguration,\
org.springframework.boot.autoconfigure.amqp.RabbitAutoConfiguration,\
org.springframework.boot.autoconfigure.batch.BatchAutoConfiguration,\
org.springframework.boot.autoconfigure.cache.CacheAutoConfiguration,\
org.springframework.boot.autoconfigure.cassandra.CassandraAutoConfiguration,\
org.springframework.boot.autoconfigure.cloud.CloudAutoConfiguration,\
org.springframework.boot.autoconfigure.context.ConfigurationPropertiesAutoConfiguration,\
org.springframework.boot.autoconfigure.context.MessageSourceAutoConfiguration,\
org.springframework.boot.autoconfigure.context.PropertyPlaceholderAutoConfiguration,\
org.springframework.boot.autoconfigure.couchbase.CouchbaseAutoConfiguration,\
org.springframework.boot.autoconfigure.dao.PersistenceExceptionTranslationAutoConfiguration,\
org.springframework.boot.autoconfigure.data.cassandra.CassandraDataAutoConfiguration,\
org.springframework.boot.autoconfigure.data.cassandra.CassandraReactiveDataAutoConfiguration,\
org.springframework.boot.autoconfigure.data.cassandra.CassandraReactiveRepositoriesAutoConfiguration,\
org.springframework.boot.autoconfigure.data.cassandra.CassandraRepositoriesAutoConfiguration,\
```

> 如果我们新定义了一个`starter`的话，也要在该`starter`的`jar`包中提供 `META-INFO/spring.factories`文件，并且为其配置`org.springframework.boot.autoconfigure.EnableAutoConfiguration`对应的配置类 

从`EnableAutoConfiguration`寻找一个配置类CacheAutoConfiguration

```java
@Configuration
@ConditionalOnClass(CacheManager.class)
@ConditionalOnBean(CacheAspectSupport.class)
@ConditionalOnMissingBean(value = CacheManager.class, name = "cacheResolver")
@EnableConfigurationProperties(CacheProperties.class)
@AutoConfigureAfter({ CouchbaseAutoConfiguration.class, HazelcastAutoConfiguration.class,
		HibernateJpaAutoConfiguration.class, RedisAutoConfiguration.class })
@Import(CacheConfigurationImportSelector.class)
public class CacheAutoConfiguration {

	@Bean
	@ConditionalOnMissingBean
	public CacheManagerCustomizers cacheManagerCustomizers(
			ObjectProvider<List<CacheManagerCustomizer<?>>> customizers) {
		return new CacheManagerCustomizers(customizers.getIfAvailable());
	}
    .......
}
```

这是一个`@Configuration`配置类，包含`@Bean`的方法的返回值会注册为一个`bean`

在这个类和方法上我们看到很多条件配置注解

条件配置主要的注解是`@Conditional`,这个注解指定一个实现了`Condition`的类，类中实现了`matchs`方法，如果方法返回`true`，被`@Conditional`修饰的类或者方法才会创建`bean`。为了方便`Spring4`中已经帮我们实现了一些常用的条件配置注解

```java
@ConditionalOnBean
@ConditionalOnClass
@ConditionalOnExpression
@ConditionalOnMissingBean
@ConditionalOnMissingClass
@ConditionalOnNotWebApplication
```

至此，我们已经分析了`SpringBoot`中自动化配置的基本原理，接下来我们会编写一个`spring-boot-starter`









