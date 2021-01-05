---
title: redis配置文件
date: 2018-09-02 12:04:41
tags: 数据库，redis
categories: redis
---

我们可以在启动redis服务器的时候指定配置文件

redis配置文件`redis.con`在开始的时候，先明确了一些单位

```properties
# 1k => 1000 bytes
# 1kb => 1024 bytes
# 1m => 1000000 bytes
# 1mb => 1024*1024 bytes
# 1g => 1000000000 bytes
# 1gb => 1024*1024*1024 bytes

```

redis支持从外部文件中引入配置文件

<!--more-->

`include /path/to/other.conf`

redis的配置文件中分成了几个部分：

- 通用(general)
- 快照(snapshotting)
- 复制(replicaion)
- 安全(security)
- 限制(limits)
- 追加模式(AOF)
- LUA脚本(LUA script)
- 慢日志(slow log)
- 事件通知(event notification)

##### 配置文件【通用】

默认情况下，redis并不是以daemon形式来运行的。通过daemonize配置项可以控制redis的运行形式，如果改为yes，那么redis就会以daemon形式运行：

```
daemonize no
```

默认情况下，redis会响应本机所有可用网卡的连接请求。当然，redis允许你通过bind配置项来指定要绑定的IP

```
bind 192.168.1.2 10.8.4.2
```

redis的默认服务端口是6379，你可以通过port配置项来修改。如果端口设置为0的话，redis便不会监听端口了。

```
port 6379
```

当一个redis-client一直没有请求发向server端，那么server端有权主动关闭这个连接，可以通过timeout来设置“空闲超时时限”，0表示永不关闭

```
timeout 0
```

TCP连接保活策略，可以通过tcp-keepalive配置项来进行设置，单位为秒，假如设置为60秒，则server端会每60秒向连接空闲的客户端发起一次ACK请求，以检查客户端是否已经挂掉，对于无响应的客户端则会关闭其连接。如果设置为0，则不会进行保活检测。

```
tcp-keepalive 0
```

redis支持通过loglevel配置项设置日志等级，共分四级，即debug、verbose、notice、warning。

```
loglevel notice
```

redis也支持通过logfile配置项来设置日志文件的生成位置。如果设置为空字符串，则redis会将日志输出到标准输出。假如你在daemon情况下将日志设置为输出到标准输出，则日志会被写到/dev/null中。

```
logfile ""
```

对于redis来说，可以设置其数据库的总数量，假如你希望一个redis包含16个数据库，那么设置如下：

> 这16个数据库的编号将是0到15。默认的数据库是编号为0的数据库。用户可以使用select <DBid>来选择相应的数据库。

```
databases 16
```

##### 配置文件【快照】

快照，主要涉及的是redis的RDB持久化相关的配置

我们可以用如下的指令来让数据保存到磁盘上，即控制RDB快照功能：

```
save 60 500      
#  60 秒内至少有500个key发生改变，就触发一次快照持久化
```

如果你想禁用RDB持久化的策略，只要不设置任何save指令就可以，或者给save传入一个空字符串参数也可以达到相同效果，

```
save ""
```

如果用户开启了RDB快照功能，那么在redis持久化数据到磁盘时如果出现失败，默认情况下，redis会停止接受所有的写请求。这样做的好处在于可以让用户很明确的知道内存中的数据和磁盘上的数据已经存在不一致了。如果redis不顾这种不一致，一意孤行的继续接收写请求，就可能会引起一些灾难性的后果。

如果下一次RDB持久化成功，redis会自动恢复接受写请求。

当然，如果你不在乎这种数据不一致或者有其他的手段发现和控制这种不一致的话，你完全可以关闭这个功能，以便在快照写入失败时，也能确保redis继续接受新的写请求。配置项如下：

```
stop-writes-on-bgsave-error yes
```

对于存储到磁盘中的快照，可以设置是否进行压缩存储。如果是的话，redis会采用LZF算法进行压缩。如果你不想消耗CPU来进行压缩的话，可以设置为关闭此功能，但是存储在磁盘上的快照会比较大。

```
rdbcompression yes
```

我们还可以设置快照文件的名称，默认是这样配置的：

```
dbfilename dump.rdb
```

最后，你还可以设置这个快照文件存放的路径。比如默认设置就是当前文件夹：

```
dir ./
```

##### 配置文件【复制】

redis提供了主从同步功能。

通过slaveof配置项可以控制某一个redis作为另一个redis的从服务器，通过指定IP和端口来定位到主redis的位置

```
slaveof <masterip> <masterport>
```

如果主redis设置了验证密码的话（使用requirepass来设置），则在从redis的配置中要使用masterauth来设置校验密码，否则的话，主redis会拒绝从redis的访问请求。

```
masterauth <master-password>
```



当从redis失去了与主redis的连接，或者主从同步正在进行中时，redis该如何处理外部发来的访问请求呢？这里，从redis可以有两种选择：

第一种选择：如果slave-serve-stale-data设置为yes（默认），则从redis仍会继续响应客户端的读写请求。

第二种选择：如果slave-serve-stale-data设置为no，则从redis会对客户端的请求返回“SYNC with master in progress”，当然也有例外，当客户端发来INFO请求和SLAVEOF请求，从redis还是会进行处理。



你可以控制一个从redis是否可以接受写请求。将数据直接写入从redis，一般只适用于那些生命周期非常短的数据，因为在主从同步时，这些临时数据就会被清理掉。自从redis2.6版本之后，默认从redis为只读。

```
slave-read-only yes
```

只读的从redis并不适合直接暴露给不可信的客户端。为了尽量降低风险，可以使用rename-command指令来将一些可能有破坏力的命令重命名，避免外部直接调用。比如

```
rename-command CONFIG b840fc02d524045429941cc15f59e41cb7be6c52
```

从redis会周期性的向主redis发出PING包。你可以通过repl_ping_slave_period指令来控制其周期。默认是10秒。

```
repl-ping-slave-period 10
```



在主从同步时，可能在这些情况下会有超时发生：

1.以从redis的角度来看，当有大规模IO传输时。
2.以从redis的角度来看，当数据传输或PING时，主redis超时
3.以主redis的角度来看，在回复从redis的PING时，从redis超时

用户可以设置上述超时的时限，不过要确保这个时限比repl-ping-slave-period的值要大，否则每次主redis都会认为从redis超时。

```
repl-timeout 60
```

我们可以控制在主从同步时是否禁用TCP_NODELAY。如果开启TCP_NODELAY，那么主redis会使用更少的TCP包和更少的带宽来向从redis传输数据。但是这可能会增加一些同步的延迟，大概会达到40毫秒左右。如果你关闭了TCP_NODELAY，那么数据同步的延迟时间会降低，但是会消耗更多的带宽。

```
repl-disable-tcp-nodelay no
```

我们还可以设置同步队列长度。队列长度（backlog)是主redis中的一个缓冲区，在与从redis断开连接期间，主redis会用这个缓冲区来缓存应该发给从redis的数据。这样的话，当从redis重新连接上之后，就不必重新全量同步数据，只需要同步这部分增量数据即可。

```
repl-backlog-size 1mb
```

如果主redis等了一段时间之后，还是无法连接到从redis，那么缓冲队列中的数据将被清理掉。我们可以设置主redis要等待的时间长度。如果设置为0，则表示永远不清理。默认是1个小时。

```
repl-backlog-ttl 3600
```



##### 配置文件【安全】

我们可以要求redis客户端在向redis-server发送请求之前，先进行密码验证。当你的redis-server处于一个不太可信的网络环境中时，相信你会用上这个功能。

```
requirepass ranger
```

redis允许我们对redis指令进行更名，比如将一些比较危险的命令改个名字，避免被误执行。比如可以把CONFIG命令改成一个很复杂的名字，这样可以避免外部的调用，同时还可以满足内部调用的需要

```
rename-command CONFIG b840fc02d524045429941cc15f59e41cb7be6c89
```

我们甚至可以禁用掉CONFIG命令，那就是把CONFIG的名字改成一个空字符串：

```
rename-command CONFIG ""
```





##### 配置文件【限制】

我们可以设置redis同时可以与多少个客户端进行连接。默认情况下为10000个客户端

```
maxclients 10000
```





我们甚至可以设置redis可以使用的内存量。一旦到达内存使用上限，redis将会试图移除内部数据，移除规则可以通过maxmemory-policy来指定。

如果redis无法根据移除规则来移除内存中的数据，或者我们设置了“不允许移除”，那么redis则会针对那些需要申请内存的指令返回错误信息，比如SET、LPUSH等。但是对于无内存申请的指令，仍然会正常响应，比如GET等。

```
maxmemory <bytes>
```



对于内存移除规则来说，redis提供了多达6种的移除规则

```
maxmemory-policy volatile-lru
```

LRU算法和最小TTL算法都并非是精确的算法，而是估算值。所以你可以设置样本的大小。假如redis默认会检查三个key并选择其中LRU的那个，那么你可以改变这个key样本的数量。

```
maxmemory-samples 3
```





##### 配置文件【追加模式】

我们建议大家，AOF机制和RDB机制可以同时使用，不会有任何冲突

```
appendonly yes
```

我们还可以设置aof文件的名称：

```
appendfilename "appendonly.aof"
```



fsync()调用，用来告诉操作系统立即将缓存的指令写入磁盘。一些操作系统会“立即”进行，而另外一些操作系统则会“尽快”进行。

redis支持三种不同的模式：

1.no：不调用fsync()。而是让操作系统自行决定sync的时间。这种模式下，redis的性能会最快。
2.always：在每次写请求后都调用fsync()。这种模式下，redis会相对较慢，但数据最安全。
3.everysec：每秒钟调用一次fsync()。这是性能和安全的折衷。

```
appendfsync everysec
```

我们允许redis自动重写aof。当aof增长到一定规模时，redis会隐式调用BGREWRITEAOF来重写log文件，以缩减文件体积。

redis是这样工作的：redis会记录上次重写时的aof大小。假如redis自启动至今还没有进行过重写，那么启动时aof文件的大小会被作为基准值。这个基准值会和当前的aof大小进行比较。如果当前aof大小超出所设置的增长比例，则会触发重写。另外，你还需要设置一个最小大小，是为了防止在aof很小时就触发重写。

```
auto-aof-rewrite-percentage 100
auto-aof-rewrite-min-size 64mb
```





##### 配置文件【lua脚本】

lua脚本的最大运行时间是需要被严格限制的，要注意单位是毫秒：

```
lua-time-limit 5000
```





##### 配置文件【慢日志】

redis慢日志是指一个系统进行日志查询超过了指定的时长。这个时长不包括IO操作，比如与客户端的交互、发送响应内容等，而仅包括实际执行查询命令的时间。

针对慢日志，你可以设置两个参数，一个是执行时长，单位是微秒，另一个是慢日志的长度。当一个新的命令被写入日志时，最老的一条会从命令日志队列中被移除。

单位是微秒，即1000000表示一秒。负数则会禁用慢日志功能，而0则表示强制记录每一个命令。

```
slowlog-log-slower-than 10000
```

慢日志最大长度，可以随便填写数值，没有上限，但要注意它会消耗内存。你可以使用SLOWLOG RESET来重设这个值。

```
slowlog-max-len 128
```

