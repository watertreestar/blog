---
title: 搞定redis
date: 2018-08-20 15:32:31
tags: [数据库，redis,缓存]
categories: redis
---

#### Redis是什么，有什么特点和优势

Redis是一个开源用C语言编写的，基于内存，可以持久化，高性能的key-value数据库，并提供多种语言的API。

它也被称为数据结构服务器，因为值（value）可以是string,hash,list,sets,zsets(有序集合)类型

<!--more-->

Redis有以下特点：

- Redis支持数据的持久化，可以将内存中的数据保持在磁盘中，重启的时候可以再次加载进行使用。
- Redis不仅仅支持简单的key-value类型的数据，同时还提供list，set，zset，hash等数据结构的存储。
- Redis支持数据的备份，即master-slave模式的数据备份。

Redis的优势

- 性能极高 – Redis能读的速度是110000次/s,写的速度是81000次/s 。
- 丰富的数据类型 – Redis支持二进制案例的 Strings, Lists, Hashes, Sets 及 Ordered Sets 数据类型操作。
- 原子 – Redis的所有操作都是原子性的，同时Redis还支持对几个操作全并后的原子性执行。
- 丰富的特性 – Redis还支持 publish/subscribe, 通知, key 过期等等特性




#### 安装Redis

从redis.io下载最新版redis-X.Y.Z.tar.gz后解压，然后进入redis-X.Y.Z文件夹后直接make即可，

这是用于`linux`下运行的redis服务器，

从redis.io下载最新版redis-X.Y.Z.tar.gz后解压，然后进入redis-X.Y.Z文件夹后直接make即可，

```
./redis-benchmark //用于进行redis性能测试的工具
./redis-check-dump //用于修复出问题的dump.rdb文件
./redis-cli //redis的客户端
./redis-server //redis的服务端
./redis-check-aof //用于修复出问题的AOF文件
./redis-sentinel //用于集群管理
```

启动Redis服务器：`./redis-server ./redis.conf`

运行此命令后，redis服务器将会以非daemon的方法启动，默认端口号为`6379`,关于端口号为什么是6379，可以[参考](http://oldblog.antirez.com/post/redis-as-LRU-cache.html)

#### 使用Redic-cli

```
./redis-cli  
127.0.0.1:6379> auth ranger
OK
127.0.0.1:6379> keys *
1) "key1"
2) "key2"
127.0.0.1:6379> get key1
"123456"
```

#### Redis数据结构简介

redis是一种`key-value`的数据结构，其`value`支持五种数据结构：

1. 字符串（string）
2. 字符串列表(list)
3. 字符串集合（stes）
4. 有序字符串集合（zsets）
5. 哈希（hash）

如何选择合适的`key`

- `key`不要太长，太长会消耗大量内存，且降低了查找效率
- `key`也不要太短，太短降低可读性
- 在一个项目中，`key`最好使用统一的命名规则



#### Redis数据结构之string

如果redis只是使用string类型和且不使用持久化功能，redis就和memcached非常相似了。

string是一个很基础的数据类型

```
127.0.0.1:6379> set mystr "hello redis"
OK
127.0.0.1:6379> get mystr
"hello redis"
```

```
127.0.0.1:6379> set num "2"
OK
127.0.0.1:6379> get num
"2"
127.0.0.1:6379> incr num
(integer) 3
127.0.0.1:6379> get num
"3"

```

在遇到数值操作时，redis会将字符串类型转换成数值。例如`incr`指令

由于INCR等指令本身就具有原子操作的特性，所以我们完全可以利用redis的INCR、INCRBY、DECR、DECRBY等指令来实现原子计数的效果

#### Redis数据结构之list

redis的另外一个重要的数据结构，中文翻译作列表。list在redis中存储的底层数据结构是链表。所以list在头部和尾部插入一个元素的速度一致且相当快，但是定位元素比较慢

`list`常用的操作有`lpush`,`rpush`,`lrange`

`lpush`用来在list左边插入一个元素，

`rpush`用来在list右边插入一个元素

`lrange`可以指定一个范围从list中提取元素

```
127.0.0.1:6379> lpush mylist tom
(integer) 1
127.0.0.1:6379> lpush mylist jery
(integer) 2
127.0.0.1:6379> lrange mylist 0 2
1) "jery"
2) "tom"
127.0.0.1:6379> rpush mylist jack
(integer) 3
127.0.0.1:6379> lrange mylist 0 3
1) "jery"
2) "tom"
3) "jack"
127.0.0.1:6379> lrange mylist 1 2
1) "tom"
2) "jack"

```

`list`的应用

1. 利用list来实现一个简单的消息队列，可以保证先后顺序，不必排序
2. 利用lrange可以实现分页功能
3. 可以用作博客的评论

#### Redis数据结构之sets

redis的sets是一种无序的集合，集合中的元素没有先后顺序。

```
127.0.0.1:6379> sadd mysets one
(integer) 1
127.0.0.1:6379> sadd mysets tow
(integer) 1
127.0.0.1:6379> smembers mysets
1) "one"
2) "tow"
127.0.0.1:6379> scard mysets
(integer) 2
127.0.0.1:6379> srem mysets tow
(integer) 1
127.0.0.1:6379> scard mysets
(integer) 1
127.0.0.1:6379> smembers mysets
1) "one"
127.0.0.1:6379> sismember mysets one
(integer) 1
```

`sets`应用场景

社交号的好友标签，每一个用户的好友标签都存在一个set集合中



#### Redis数据结构之zsets

redis不但提供了无序集合，还提供了有序的集合（sorted ses）。有序集合中每一个元素都关联一个序号。

很多时候，我们都将redis中的有序集合叫做zsets，这是因为在redis中，有序集合相关的操作指令都是以z开头的，比如zrange、zadd、zrevrange、zrangebyscore等等

```
127.0.0.1:6379> zadd myzsets 1 baidu.com
(integer) 1
127.0.0.1:6379> zadd myzsets 2 qq.com
(integer) 1
127.0.0.1:6379> zrange myzsets 0 3
1) "baidu.com"
2) "qq.com"
127.0.0.1:6379> zrange myzsets 0 3 withscores
1) "baidu.com"
2) "1"
3) "qq.com"
4) "2"
127.0.0.1:6379> 

```

#### Redis数据结构之hash

哈希是从redis-2.0.0版本之后才有的数据结构。

hashes存的是字符串和字符串值之间的映射，比如一个用户要存储其全名、姓氏、年龄等等，就很适合使用哈希。

```
127.0.0.1:6379> hgetall ranger
1) "name"
2) "cyp"
3) "age"
4) "20"
127.0.0.1:6379> hset ranger age 21
(integer) 0
127.0.0.1:6379> hgetall ranger
1) "name"
2) "cyp"
3) "age"
4) "21"
```



#### Redis的持久化

redis提供了两种持久化的方法:`RDB(Redis DataBase)`和`AOF(Append Only File)`

`RDB`:就是在不同的时间点，生成数据快照，将数据存储到磁盘上

`AOF:`将redis执行过的指令记录下来，再把这些指令重新执行一次，就达到了数据重现的目的

这两种持久化的方式可以同时使用，redis重启会优先选择AOF,这样数据的完整性更高

如果没有持久化数据的需求，可以关闭此功能



##### Redis的持久化之RDB

RDB方式，是将redis某一时刻的数据持久化到磁盘中，是一种快照式的持久化方法。

redis在进行数据持久化的过程中，会先将数据写入到一个临时文件中，待持久化过程都结束了，才会用这个临时文件替换上次持久化好的文件。正是这种特性，让我们可以随时来进行备份，因为快照文件总是完整可用的。

对于RDB方式，redis会单独创建（fork）一个子进程来进行持久化，而主进程是不会进行任何IO操作的，这样就确保了redis极高的性能。

如果需要进行大规模数据的恢复，且对于数据恢复的完整性不是非常敏感，那RDB方式要比AOF方式更加的高效(其直接保存了数据)。

虽然RDB有不少优点，但它的缺点也是不容忽视的。如果你对数据的完整性非常敏感，那么RDB方式就不太适合你，因为即使你每5分钟都持久化一次，当redis故障时，仍然会有近5分钟的数据丢失。所以，redis还提供了另一种持久化方式，那就是AOF。

如果要开启redis的RDB方式持久化

- 你可以配置保存点，使Redis如果在每N秒后数据发生了M次改变就保存快照文件。例如下面这个保存点配置表示每60秒，如果数据发生了1000次以上的变动，Redis就会自动保存快照文件：`save 60 1000`

- 保存点可以设置多个，Redis的配置文件就默认设置了3个保存点：

  ```
  # 格式为：save <seconds> <changes>
  # 可以设置多个。
  save 900 1 #900秒后至少1个key有变动
  save 300 10 #300秒后至少10个key有变动
  save 60 10000 #60秒后至少10000个key有变动
  ```

- 如果想禁用快照保存的功能，可以通过注释掉所有"save"配置达到，或者在最后一条"save"配置后添加如下的配置：`save ""`

#####  Redis的持久化之AOF

`AOF`，英文是`Append Only File`，即只允许追加不允许改写的文件。

我们通过配置`redis.conf中的appendonly yes`就可以打开AOF功能。如果有写操作（如SET等），redis就会被追加到AOF文件的末尾。

默认的AOF持久化策略是每秒钟fsync一次（fsync是指把缓存中的写指令记录到磁盘中），因为在这种情况下，redis仍然可以保持很好的处理性能，即使redis故障，也只会丢失最近1秒钟的数据。

因为采用了追加方式，如果不做任何处理的话，AOF文件会变得越来越大，为此，redis提供了`AOF文件重写`（rewrite）机制，即当AOF文件的大小超过所设定的阈值时，redis就会启动AOF文件的内容压缩，只保留可以恢复数据的最小指令集。举个例子或许更形象，假如我们调用了100次INCR指令，在AOF文件中就要存储100条指令，但这明显是很低效的，完全可以把这100条指令合并成一条SET指令，这就是重写机制的原理。

虽然优点多多，但AOF方式也同样存在缺陷，比如在同样数据规模的情况下，AOF文件要比RDB文件的体积大。而且，AOF方式的恢复速度也要慢于RDB方式

##### Redis持久化之AOF重写

在重写即将开始之际，redis会创建（fork）一个“重写子进程”，这个子进程会首先读取现有的AOF文件，并将其包含的指令进行分析压缩并写入到一个临时文件中。

与此同时，主工作进程会将新接收到的写指令一边累积到内存缓冲区中，一边继续写入到原有的AOF文件中，这样做是保证原有的AOF文件的可用性，避免在重写过程中出现意外。

当“重写子进程”完成重写工作后，它会给父进程发一个信号，父进程收到信号后就会将内存中缓存的写指令追加到新AOF文件中。

当追加结束后，redis就会用新AOF文件来代替旧AOF文件，之后再有新的写指令，就都会追加到新的AOF文件中了。



#### Redis的主从同步

像MySQL一样，redis是支持主从同步的，而且也支持一主多从以及多级从结构。

主从结构，一是为了纯粹的冗余备份，二是为了提升读性能

redis的主从同步是异步进行的，这意味着主从同步不会影响主逻辑，也不会降低redis的处理性能。

在主从架构中，从服务器通常被设置为只读模式，这样可以避免从服务器的数据被误修改。但是从服务器仍然可以接受CONFIG等指令，所以还是不应该将从服务器直接暴露到不安全的网络环境中。如果必须如此，那可以考虑给重要指令进行重命名，来避免命令被外人误执行。

##### 主从的原理

从服务器会向主服务器发出SYNC指令，当主服务器接到此命令后，就会调用BGSAVE指令来创建一个子进程专门进行数据持久化工作，也就是将主服务器的数据写入RDB文件中。在数据持久化期间，主服务器将执行的写指令都缓存在内存中。

在BGSAVE指令执行完成后，主服务器会将持久化好的RDB文件发送给从服务器，从服务器接到此文件后会将其存储到磁盘上，然后再将其读取到内存中。这个动作完成后，主服务器会将这段时间缓存的写指令再以redis协议的格式发送给从服务器。

另外，要说的一点是，即使有多个从服务器同时发来SYNC指令，主服务器也只会执行一次BGSAVE，然后把持久化好的RDB文件发给多个下游。在redis2.8版本之前，如果从服务器与主服务器因某些原因断开连接的话，都会进行一次主从之间的全量的数据同步

而在2.8版本之后，redis支持了效率更高的增量同步策略，这大大降低了连接断开的恢复成本。

主服务器会在内存中维护一个缓冲区，缓冲区中存储着将要发给从服务器的内容。从服务器在与主服务器出现网络瞬断之后，从服务器会尝试再次与主服务器连接，一旦连接成功，从服务器就会把“希望同步的主服务器ID”和“希望请求的数据的偏移位置（replication offset）”发送出去。主服务器接收到这样的同步请求后，首先会验证主服务器ID是否和自己的ID匹配，其次会检查“请求的偏移位置”是否存在于自己的缓冲区中，如果两者都满足的话，主服务器就会向从服务器发送增量内容。

增量同步功能，需要服务器端支持全新的PSYNC指令。这个指令，只有在redis-2.8之后才具有。



#### Redis的事务

redis事务相关的4个指令： multi，exec，discard，watch

- multi : 用来组装一个事务
- exec : 用来执行一个事务
- discard ： 用来取消一个事务
- watch ： 用来监视一些key，一旦这些key在事务执行之前被改变，则取消事务的执行。

multi和exec

```
127.0.0.1:6379> multi
OK
127.0.0.1:6379> sadd mysets ranger
QUEUED
127.0.0.1:6379> lpush mylist hello
QUEUED
127.0.0.1:6379> ping
QUEUED
127.0.0.1:6379> exec
1) (integer) 1
2) (integer) 4
3) PONG
```



#### Redis的数据淘汰策略

在redis中，允许用户设置可以使用的最大内存大小(`maxmemory 100mb`)，这在内存紧张的情况下很有用。

redis内存数据大小上升到一定的大小，就会使用内存淘汰策略淘汰一部分数据。redis提供6中数据淘汰策略

- volatile-lru :从已设置过期时间的数据集（server.db[i].expires）中挑选最近最少使用的数据淘汰
- volatile-ttl：从已设置过期时间的数据集（server.db[i].expires）中挑选将要过期的数据淘汰
- volatile-random：从已设置过期时间的数据集（server.db[i].expires）中任意选择数据淘汰
- allkeys-lru：从数据集（server.db[i].dict）中挑选最近最少使用的数据淘汰
- allkeys-random：从数据集（server.db[i].dict）中任意选择数据淘汰
- no-enviction（驱逐）：禁止驱逐数据

redis 确定驱逐某个键值对后，会删除这个数据并，并将这个数据变更消息发布到本地（AOF 持久化）和从机（主从连接）。







