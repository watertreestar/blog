---
title: 动手写一个LRU缓存
date: 2018-11-27 15:22:24
tags: [Java,LRU,算法，缓存]
categories: 算法
---



#  前言

LRU 是 `Least Recently Used` 的简写，字面意思则是`最近最少使用`。

通常用于缓存的淘汰策略实现，由于缓存的内存非常宝贵，所以需要根据某种规则来剔除数据保证内存不被占满。



在`redis`的数据淘汰策略中就包含`LRU淘汰算法`

如何实现一个完整的`LRU缓`存呢？这个缓存要满足：

+ 这个缓存要记录使用的顺序
+ 随着缓存的使用变化，要能更新缓存的顺序

<!--more-->

基于这种特点，可以使用一个常用的数据结构：`链表`

- 每次加入新的缓存时都添加到链表的`头节点`
- 当缓存再次被使用时移动缓存到`头节点`
- 当添加的缓存超过能够缓存的最大时，删除链表`尾节点`的元素

# 单链表和双向链表的选择

单链表的方向只有一个，节点中有一个`next`指针指向后继节点。而双链表有两个指针，可以支持两个方向，每个节点不止有一个`next`指针，还有一个`pre`v指针指向前驱节点

双向链表需要额外的两个空间来存放前驱节点的指针`prev`和后继节点指针`next`,所以，存储相同大小的数据，双向链表需要更多的空间。虽然相比单向链表，双向链表的每个节点多个一个指针空间，但是这样的结构带来了更多的灵活性，在某些场景下非常适合使用这样的数据结构。删除和添加节点操作，双向链表的时间复杂度为O(1)

在单向链表中，删除和添加节点的时间复杂度已经是O(1)了，双向链表还能比单向链表更加高效吗？

先来看看`删除操作`：

在删除操作中有两种情况：

- 删除给定值的节点
- 删除给定指针的节点

对于第一种情况，无论是删除给定值或者是给定的指针都需要从链表头开始依此遍历，直到找到所要删除的值

尽管删除这个操作的时间复杂度为O(1)，但是删除的时间消耗主要是遍历节点，对应的时间复杂度为O(n),所以总的时间复杂度为O(n)。

对于第二种情况，已经给定了要删除的节点，如果使用单向链表，还得从链表头部开始遍历，直到找到待删除节点的前驱节点。但是对于双向链表来所，这就很有优势了，双向链表的待删除节点种包含了前驱节点，删除操作只需要O(1)的时间复杂度

同理对于`添加操作：`

我们如果想要在指定的节点前面或者后面插入一个元素，双向了链表就有很大的优势，他可以在O(1)的时间复杂度搞定，而单向链表还需要从头遍历。

所以，虽然双向链表比单向链表需要更多的存储空间，但是双向链表的应用更加广泛，JDK种LinkedHashMap这种数据结构就使用了双向链表

# 如何实现LRU缓存

##　单链表实现

下面我们基于单链表给出简单的代码实现：

```java
package com.ranger.lru;

import java.util.HashMap;
import java.util.Map;

/**
 * 
 * @author ranger
 * LRU缓存
 *
 */
public class LRUMap<K,V> {
	
	/**
	 * 定义链表节点
	 * @author ranger
	 *
	 * @param <K>
	 * @param <V>
	 */
	private class Node<K, V> {
        private K key;
        private V value;
        Node<K, V> next;
        
        public Node(K key, V value) {
            this.key = key;
            this.value = value;
        }
        public Node() {
        	
        }
        
    }
	
	
	/**
	 * 缓存最大值
	 */
	private int capacity;
	
	/**
	 * 当前缓存数量
	 */
	private int size;
	
	/**
	 * 缓存链表头节点
	 */
	private Node<K,V> head;
	
	/**
	 * 缓存链表尾节点
	 */
	private Node<K,V> tail;
	
	/**
	 * 定义带参构造函数,构造一个为空的双向链表
	 * @param capacity  缓存最大容量
	 */
	public LRUMap(int capacity) {
		this.capacity = capacity;
		head = null;
		tail = null;
		size = 0;
	}
	
	/**
	 * 无参构造函数，初始化容量为16
	 */
	public LRUMap() {
		this(16);
	}
	
	/**
	 * 向双向链表中添加节点
	 * @param key
	 * @param value
	 */
	public void put(K key,V value) {
		addNode(key,value);
	}
	
	/**
	 * 根据key获取缓存中的Value
	 * @param key
	 * @return
	 */
	public V get(K key) {
		Node<K,V> retNode = getNode(key);
		if(retNode != null) {
			// 存在，插入头部
			moveToHead(retNode);
			return retNode.value;
		}
		// 不存在
		return null;
	}
	
	/**
	 * 移动给定的节点到头节点
	 * @param node
	 */
	public void moveToHead(Node<K,V> node) {
		// 如果待移动节点是最后一个节点
		if(node == tail) {
			Node prev = head;
			while(prev.next != null && prev.next != node) {
				prev = prev.next;
			}
			tail = prev;
			node.next = head;
			head = node;
			prev.next = null;
			
		}else if(node == head){   // 如果是头节点
			return;
		}else {
			Node prev = head;
			while(prev.next != null && prev.next != node) {
				prev = prev.next;
			}
			prev.next = node.next;
			node.next = head;
			head = node;
		}
	}
	
	/**
	 * 获取给定key的节点
	 * @param key
	 * @return
	 */
	private Node<K,V> getNode(K key){
		if(isEmpty()) {
			throw new IllegalArgumentException("list is empty,cannot get node from it");
		}
		Node<K,V> cur = head;
		while(cur != null) {
			if(cur.key.equals(key)) {
				return cur;
			}
			cur = cur.next;
		}
		return null;
	}
	
	/**
	 * 添加到头节点
	 * @param key
	 * @param value
	 */
	private void addNode(K key,V value) {
		Node<K,V> node = new Node<>(key,value);
		// 如果容量满了，删除最后一个节点
		if(size == capacity) {
			delTail();
		}
		addHead(node);
	}
	
	/**
	 * 删除最后一个节点
	 */
	private void delTail() {
		if(isEmpty()) {
			throw new IllegalArgumentException("list is empty,cannot del from it");
		}
		// 只有一个元素
		if(tail == head) {
			tail = null;
			head = tail;
		}else {
			Node<K,V> prev = head;
			while(prev.next != null && prev.next != tail) {
				prev = prev.next;
			}
			prev.next = null;
			tail = prev;
		} 
		
		size--;
	}
	
	/**
	 * 链表是否为空
	 * @return
	 */
	private boolean isEmpty() {
		return size == 0;
	}
	
	/**
	 * 添加节点到头头部
	 * @param node
	 */
	private void addHead(Node node) {
		// 如果链表为空
		if(head == null) {
			head = node;
			tail = head;
		}else {
			node.next = head;
			head = node;
		}
		
		size ++;
		
	}
	
	@Override
	public String toString() {
		StringBuilder sb = new StringBuilder();
		Node<K,V> cur = head;
		while(cur != null) {
			sb.append(cur.key)
			.append(":")
			.append(cur.value);
			if(cur.next != null) {
				sb.append("->");
			}
			cur = cur.next;
		}
		return sb.toString();
	}
	
	/**
	 * 测试
	 * @param args
	 */
	public static void main(String[] args) {
		LRUMap<String,String> lruMap = new LRUMap(3) ;
        lruMap.put("1","tom") ;
        lruMap.put("2","lisa") ;
        lruMap.put("3","john") ;
        System.out.println(lruMap.toString());
        lruMap.put("4","july") ;
        System.out.println(lruMap.toString());
        lruMap.put("5","jack") ;
        System.out.println(lruMap.toString());
        String value = lruMap.get("3");
        System.out.println(lruMap.toString());
        System.out.println("the value is: "+value);
        String value1 = lruMap.get("1");
        System.out.println(value1);
        System.out.println(lruMap.toString());
        
	}
	
}


输出结果：
3:john->2:lisa->1:tom
4:july->3:john->2:lisa
5:jack->4:july->3:john
3:john->5:jack->4:july
the value is: john
null
3:john->5:jack->4:july

```



## LinkedHashMap实现

了解`LinkedHashMap`的都知道，它是基于链表实现，其中还有一个 `accessOrder` 成员变量，默认是 `false`，默认按照插入顺序排序，为 `true` 时按照访问顺序排序，也可以调用 构造函数传入`accessOrder`

`LinkedHashMap` 的排序方式有两种：

- 根据写入顺序排序。
- 根据访问顺序排序。

其中根据访问顺序排序时，每次 `get` 都会将访问的值移动到链表末尾，这样重复操作就能的到一个按照访问顺序排序的链表

我们可以重写`LinkedHashMap`中的`removeEldestEntry`方法来决定在添加节点的时候是否需要删除最久未使用的节点

代码实现如下：

```java
public class LRULinkedHashMap<K,V> {

	/**
	 * 缓存map
	 */
	private LinkedHashMap<K,V> cacheMap;
	
	/**
	 * 当前缓存数量
	 */
	private int size;
	
	/**
	 * 构造一个cacheMap，并设置可以缓存的数量
	 * @param size
	 */
	public LRULinkedHashMap(int size) {
		this.size = size;
		
		cacheMap = new LinkedHashMap<K,V>(16,0.75F,true) {
			@Override
			// 重写方法，判断是否删除最久没使用的节点
            protected boolean removeEldestEntry(Map.Entry eldest) {
                if (size + 1 == cacheMap.size()){
                    return true ;
                }else {
                    return false ;
                }
            }
		};
	}
	/**
	 * 添加缓存
	 * @param key
	 * @param value
	 */
	public void put(K key,V value){
        cacheMap.put(key,value) ;
    }
	
	/**
	 * 获取缓存
	 * @param key
	 * @return
	 */
    public V get(K key){
        return cacheMap.get(key) ;
    }
    
    public String toString() {
    	StringBuilder sb = new StringBuilder();
    	Set<Entry<K, V>> entrySet = cacheMap.entrySet();
    	for (Entry<K,V> entry : entrySet) {
    		sb.append(entry.getKey())
    		.append(":")
    		.append(entry.getValue())
    		.append("<-");
    	}
    	
    	return sb.toString();
    }
    
    
    public static void main(String[] args) {
    	LRULinkedHashMap<String,Integer> map = new LRULinkedHashMap(3) ;
        map.put("1",1);
        map.put("2",2);
        map.put("3",3);
        System.out.println(map);
        map.put("4", 4);
        System.out.println(map);
	}
    
}
```





