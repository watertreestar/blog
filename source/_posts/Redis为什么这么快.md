---
title: Redis为什么这么快
date: 2019-02-18 14:38:32
tags: [redis,数据库，缓存]
categories: 缓存
---

## Redis简介

- Redis是一个开源的内存中的数据结构存储系统，它可以用作：**数据库、缓存和消息中间件** 

- 它支持多种类型的数据结构，如字符串（String），散列（Hash），列表（List），集合（Set），有序集合（Sorted Set或者是ZSet）与范围查询，Bitmaps，Hyperloglogs 和地理空间（Geospatial）索引半径查询。其中常见的数据结构类型有：String、List、Set、Hash、ZSet这5种。

- Redis 内置了复制（Replication），LUA脚本（Lua scripting）， LRU驱动事件（LRU eviction），事务（Transactions） 和不同级别的磁盘持久化（Persistence），并通过 Redis哨兵（Sentinel）和自动分区（Cluster）提供高可用性（High Availability）。

  <!--more-->

- Redis也提供了持久化的选项，这些选项可以让用户将自己的数据保存到磁盘上面进行存储。根据实际情况，可以每隔一定时间将数据集导出到磁盘（快照），或者追加到命令日志中（AOF只追加文件），他会在执行写命令时，将被执行的写命令复制到硬盘里面。您也可以关闭持久化功能，将Redis作为一个高效的网络的缓存数据功能使用。

- Redis不使用表，他的数据库不会预定义或者强制去要求用户对Redis存储的不同数据进行关联。

- 数据库的工作模式按存储方式可分为：硬盘数据库和内存数据库。Redis 将数据储存在内存里面，读写数据的时候都不会受到硬盘 I/O 速度的限制，所以速度极快。



## Redis有多快

Redis采用的是基于内存的采用的是**单进程单线程**模型的 **KV 数据库**，**由C语言编写**，官方提供的数据是可以达到100000+的QPS（每秒内查询次数） 

简单测试(2G单核)

```shell
PING_INLINE: 82236.84 requests per second
PING_BULK: 89525.52 requests per second
SET: 82987.55 requests per second
GET: 67659.00 requests per second
INCR: 71022.73 requests per second
LPUSH: 73206.44 requests per second
RPUSH: 69252.08 requests per second
LPOP: 66800.27 requests per second
RPOP: 70671.38 requests per second
SADD: 68965.52 requests per second
SPOP: 90497.73 requests per second
LPUSH (needed to benchmark LRANGE): 85984.52 requests per second
LRANGE_100 (first 100 elements): 35050.82 requests per second
LRANGE_300 (first 300 elements): 13255.57 requests per second
LRANGE_500 (first 450 elements): 8701.71 requests per second
LRANGE_600 (first 600 elements): 6487.61 requests per second
MSET (10 keys): 64226.07 requests per second

```

## Redis为什么这么快

1. 完全基于内存，绝大部分请求是纯粹的内存操作，非常快速。数据存在内存中，类似于HashMap，HashMap的优势就是查找和操作的时间复杂度都是O(1)； 

2. 采用单线程，避免了不必要的上下文切换和竞争条件，也不存在多进程或者多线程导致的切换而消耗 CPU，不用去考虑各种锁的问题，不存在加锁释放锁操作，没有因为可能出现死锁而导致的性能消耗 

3. 使用多路I/O复用模型，非阻塞IO； 

   ```
   多路I/O复用模型是利用 select、poll、epoll 可以同时监察多个流的 I/O 事件的能力，在空闲的时候，会把当前线程阻塞掉，当有一个或多个流有 I/O 事件时，就从阻塞态中唤醒，于是程序就会轮询一遍所有的流（epoll 是只轮询那些真正发出了事件的流），并且只依次顺序的处理就绪的流，这种做法就避免了大量的无用操作
   ```

4. 数据结构简单，对数据操作也简单，Redis中的数据结构是专门进行设计的 

但是，我们使用单线程的方式是无法发挥多核CPU 性能，不过我们可以通过在单机开多个Redis 实例来完善 

## Redis为什么是单线程的

因为Redis是基于内存的操作，CPU不是Redis的瓶颈，Redis的瓶颈最有可能是机器内存的大小或者网络带宽。既然单线程容易实现，而且CPU不会成为瓶颈，那就顺理成章地采用单线程的方案了 ，多线程会增加复杂度，使用锁机制来保证数据一致性

> 这里我们一直在强调的单线程，只是在处理我们的网络请求的时候只有一个线程来处理，一个正式的Redis Server运行的时候肯定是不止一个线程的，这里需要大家明确的注意一下！例如Redis进行持久化的时候会以子进程或者子线程的方式执行 