---
title: SpringSecurity初探
date: 2019-07-02 21:56:33
categories: Spring
tags: [认证，授权，SpringSecurity]
---

## SpringSecurity，为什么？

在权限管理框架中，有两座大山，Shiro和SpringSecurity,后者具有天然具有Spring家族的支撑，提供了一系列完整的功能，Shiro作为一个简单的框架，也可以满足大多数场景下的需求。之前简单使用过Shiro，知道它是通过一些列的Filter来做认证的鉴权。这次打算看一下SpringSecurity的使用，听过这个框架比较复杂，在网上看的一些文字教程也比较晕，还是自己来探究一下才能有更好的理解
<!--more-->

## Spring Security介绍

- 开源
- 提供企业级的安全认证和授权

Spring安全拦截器

- 认证管理器

  - 认证模式

    - Basic 

      HTTP 1.0中使用的认证方法，使用用户名和密码Base64编码的方式

      浏览器弹出对话框，用户输入用户名和密码，加入头部

      无状态

      安全性不足

    - Digest

      解决安全性问题

      浏览器对用户名和密码请求方法，URL等进行MD5运算，发送到服务器

      服务器获取到用户名密码，请求方法，URL等MD5运算，查看是否相等

      安全性问题依然存在

    - X.509

    

- 访问决策管理器

- 运行身份管理器

### 常用权限拦截器

Spring-Security拦截器链流程图

![](Spring-Security认证Filter.jpg)

介绍几个常用的Filter

1. SecurityContextPersistenceFilter

   基于ThreadLocal

2. LogoutFilter

   发送注销请求时，清空用户的session,cookie，重定向

3. AbstractAuthenticationProcessingFilter

   用户登录的请求

4. DefaultLoginPageGeneratingFilter

   生成登录页面

5. BasicAuthencationFilter

6. SecurityContextHolderAwareRequestFilter

   包装，提供额外的数据

7. RememberMeAuthemticationFilter

   提供RememberMe功能，当cookie中存在rememberme时，登录成功后生成唯一cookie

8. ExceptionTranlationFilter

   请求到对应的页面，响应异常

   ExceptionTranslationFilter异常处理过滤器,该过滤器用来处理在系统认证授权过程中抛出的异常（也就是下一个过滤器`FilterSecurityInterceptor`）,主要是 处理  `AuthenticationException` 和`AccessDeniedException`

9. SessionManagerFilter

10. FilterSecurityInterceptor（授权）

    用户没有登录，抛出未登录异常

    用户登录，但是没有权限访问该资源，抛出拒绝访问的异常

    用户登录，有权限，则放行
    
    
    
    此过滤器为认证授权过滤器链中最后一个过滤器，该过滤器之后就是请求真正的 服务
    
    

### Filter如何执行

> FilterChainProxy会按照顺序调用一组Filter，完成授权验证



请求首先经过Servlet Filter链，这里面包含6个Filter

![](springboot mvc 启动6大Filter.png)

可以看到如下的一个Filter

`ApplicationFilterConfig[name=springSecurityFilterChain, filterClass=org.springframework.boot.web.servlet.DelegatingFilterProxyRegistrationBean$1]`

这个就是Spring Security Filter的入口，它的类型是`DelegationFilterProxy`

那么，这个DelegationFilterProxy到底执行了什么样的操作呢？可以简单看一下源码

重点看一下部分的源码：

```java
public class DelegatingFilterProxy extends GenericFilterBean {
    
    // 类中的属性
    @Nullable
	private String contextAttribute;

	@Nullable
	private WebApplicationContext webApplicationContext;

	@Nullable
	private String targetBeanName;

	private boolean targetFilterLifecycle = false;

    
    /**
    * 重点在于这个属性
    */
	@Nullable
	private volatile Filter delegate;

	private final Object delegateMonitor = new Object();

    @Override
	public void doFilter(ServletRequest request, ServletResponse response, FilterChain filterChain)
			throws ServletException, IOException {

		// Lazily initialize the delegate if necessary.
		Filter delegateToUse = this.delegate;
		if (delegateToUse == null) {
			synchronized (this.delegateMonitor) {
				delegateToUse = this.delegate;
				if (delegateToUse == null) {
					WebApplicationContext wac = findWebApplicationContext();
					if (wac == null) {
						throw new IllegalStateException("No WebApplicationContext found: " +
								"no ContextLoaderListener or DispatcherServlet registered?");
					}
					delegateToUse = initDelegate(wac);
				}
				this.delegate = delegateToUse;
			}
		}

		// Let the delegate perform the actual doFilter operation.
		invokeDelegate(delegateToUse, request, response, filterChain);
	}
    // .......
    
    /**
	 * Initialize the Filter delegate, defined as bean the given Spring
	 * application context.
	 * <p>The default implementation fetches the bean from the application context
	 * and calls the standard {@code Filter.init} method on it, passing
	 * in the FilterConfig of this Filter proxy.
	 
	 * @param wac the root application context
	 * @return the initialized delegate Filter
	 * @throws ServletException if thrown by the Filter
	 */
	protected Filter initDelegate(WebApplicationContext wac) throws ServletException 	{
		String targetBeanName = getTargetBeanName();
		Assert.state(targetBeanName != null, "No target bean name set");
		Filter delegate = wac.getBean(targetBeanName, Filter.class);
		if (isTargetFilterLifecycle()) {
			delegate.init(getFilterConfig());
		}
		return delegate;
	}
    
    // 调用delegate的doFilter方法
    protected void invokeDelegate(
			Filter delegate, ServletRequest request, ServletResponse response, FilterChain filterChain)
			throws ServletException, IOException {

		delegate.doFilter(request, response, filterChain);
	}
}
```

根据以上代码的注释我们可以看出大概的执行流程

那类中的Filter delegate是什么呢？断点调式运行可以找到以下东西

![](Spring-Security FilterProxy.png)

这是Spring Security 提供的一个FilterChainProxy,关注其中的关键源码

```java
public class FilterChainProxy extends GenericFilterBean {
    
    // 包含一组SecurityFilterChain
    private List<SecurityFilterChain> filterChains;
    
    @Override
	public void doFilter(ServletRequest request, ServletResponse response,
			FilterChain chain) throws IOException, ServletException {
		boolean clearContext = request.getAttribute(FILTER_APPLIED) == null;
		if (clearContext) {
			try {
				request.setAttribute(FILTER_APPLIED, Boolean.TRUE);
				doFilterInternal(request, response, chain);
			}
			finally {
				SecurityContextHolder.clearContext();
				request.removeAttribute(FILTER_APPLIED);
			}
		}
		else {
			doFilterInternal(request, response, chain);
		}
	}

	private void doFilterInternal(ServletRequest request, ServletResponse response,
			FilterChain chain) throws IOException, ServletException {

		FirewalledRequest fwRequest = firewall
				.getFirewalledRequest((HttpServletRequest) request);
		HttpServletResponse fwResponse = firewall
				.getFirewalledResponse((HttpServletResponse) response);
		
        
        // 根据请求获取匹配的一组Filter
        // 这里返回的Filter就是上述的那些AuthenticationFilter,比如UsernamePasswordAuthenticationFilter
		List<Filter> filters = getFilters(fwRequest);

		if (filters == null || filters.size() == 0) {
			if (logger.isDebugEnabled()) {
				logger.debug(UrlUtils.buildRequestUrl(fwRequest)
						+ (filters == null ? " has no matching filters"
								: " has an empty filter list"));
			}

			fwRequest.reset();

			chain.doFilter(fwRequest, fwResponse);

			return;
		}

		VirtualFilterChain vfc = new VirtualFilterChain(fwRequest, chain, filters);
		vfc.doFilter(fwRequest, fwResponse);
	}
    
    /**
	 * Returns the first filter chain matching the supplied URL.
	 *
	 * @param request the request to match
	 * @return an ordered array of Filters defining the filter chain
	 */
	private List<Filter> getFilters(HttpServletRequest request) {
		for (SecurityFilterChain chain : filterChains) {
			if (chain.matches(request)) {
				return chain.getFilters();
			}
		}

		return null;
	}

}
```

到此，我们可以总结出如下的流程图：

![](FilterChainProxy流程.png)





