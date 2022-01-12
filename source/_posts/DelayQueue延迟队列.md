---
title: DelayQueue延迟队列
date: 2018-011-30 10:24:34
tags: [Java,队列]
categories: Java基础
---



###  介绍

DelayQueue 是一个支持延时获取元素的阻塞队列， 
内部采用优先队列 PriorityQueue 存储元素，
同时元素必须实现 Delayed 接口；在创建元素时可以指定多久才可以从队列中获取当前元素，只有在延迟期满时才能从队列中提取元素。

### 使用场景
- 缓存系统：当能够从延迟队列DelayQueue中获取到元素时，说明缓存已经过期
- 定时任务调度：一分钟后发送短信

<!--more-->

### 基于延迟队列，实现一个缓存系统
延迟队列中添加的元素，实现了Delayed接口
```java
public class CacheItem implements Delayed{
	private long expireTime;
	
	private long currentTime;
	
	private String key;
	
	public String getKey() {
		return key;
	}
	
	public CacheItem(String key,long expireTime) {
		this.key = key;
		this.expireTime = expireTime;
		this.currentTime = System.currentTimeMillis();
	}

	/**
	 * 比较方法，用于排序
	 * 过期时间长的放队尾，时间短的放队首
	 */
	@Override
	public int compareTo(Delayed o) {
		if(this.getDelay(TimeUnit.MICROSECONDS) > o.getDelay(TimeUnit.MICROSECONDS))
			return 1;
		if(this.getDelay(TimeUnit.MICROSECONDS) > o.getDelay(TimeUnit.MICROSECONDS))
			return -1;
		return 0;
	}

	/**
	 * 计算剩余的过期时间
	 * 大于0说明没有过期
	 */
	@Override
	public long getDelay(TimeUnit unit) {
		
		return expireTime - unit.MILLISECONDS.toSeconds(System.currentTimeMillis()-currentTime);
		
	}

}

```

缓存实现
```java

public class DelayQueueDemo {
	static class Cache implements Runnable{
		private Map<String,String> itemMap = new HashMap<>();
	
		private DelayQueue<CacheItem> delayQueue = new DelayQueue<>();
		
		private boolean stop = false;
		
		// 初始化后就开始检测
		public Cache() {
			new Thread(this).start();
		}
		
		public void add(String key,String value,long expireTime) {
			CacheItem item = new CacheItem(key,expireTime);
			itemMap.put(key, value);
			delayQueue.add(item);
			
		}
		
		public String get(String key) {
			return itemMap.get(key);
		}
		
		public void shutdown() {
			stop = true;
		}
		
		// 开启多线程，检测缓存是否过期
		@Override
		public void run() {
			while(!stop) {
				CacheItem item = delayQueue.poll();
				if(item != null) {
					// 缓存过期
					 itemMap.remove(item.getKey());
					 System.out.println("delete expired key:"+item.getKey());
				}
			}
			System.out.println("Cache stop");
		}
	}
	
	public static void main(String[] args) throws Exception{
		Cache cache = new Cache();
		cache.add("a", "1", 1);
		cache.add("b", "2", 2);
		cache.add("c", "3", 2);
		cache.add("d", "4", 4);
		cache.add("e", "5", 6);
		
		while(true) {
			String a = cache.get("a");
			String b = cache.get("b");
			String c = cache.get("c");
			String d = cache.get("d");
			String e = cache.get("e");
			
			if(a == null && b == null && c == null && d == null && e == null) {
				break;
			}
		}
		
		TimeUnit.SECONDS.sleep(1);
		cache.shutdown();
	}
	
}

```

### 延迟队列实现原理部分说明

- 可重入锁 `ReentrantLock`
- 优先队列 `PriorityQueue`


参考连接[](https://juejin.im/post/5bf945b95188254e2a04329b)

