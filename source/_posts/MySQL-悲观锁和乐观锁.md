---
title: MySQL 悲观锁和乐观锁
date: 2019-3-4 12:14:27
categories: MySQL
tags: [MySQL,锁]
---

###  悲观锁

悲观锁（Pessimistic Lock），顾名思义，就是很悲观，每次去拿数据的时候都认为别人会修改，所以每次在拿数据的时候都会上锁，这样别人想拿这个数据就会block直到它拿到锁。

悲观锁：假定会发生并发冲突，屏蔽一切可能违反数据完整性的操作。

Java synchronized 就属于悲观锁的一种实现，每次线程要修改数据时都先获得锁，保证同一时刻只有一个线程能操作数据，其他线程则会被block。

<!--more-->

### 悲观锁

乐观锁（Optimistic Lock），顾名思义，就是很乐观，每次去拿数据的时候都认为别人不会修改，所以不会上锁，但是在提交更新的时候会判断一下在此期间别人有没有去更新这个数据。乐观锁适用于读多写少的应用场景，这样可以提高吞吐量 

>  乐观锁：假设不会发生并发冲突，只在提交操作时检查是否违反数据完整性 

 乐观锁一般来说有以下2种方式：

1. 使用数据版本（Version）记录机制实现，这是乐观锁最常用的一种实现方式。何谓数据版本？即为数据增加一个版本标识，一般是通过为数据库表增加一个数字类型的 “version” 字段来实现。当读取数据时，将version字段的值一同读出，数据每更新一次，对此version值加一。当我们提交更新的时候，判断数据库表对应记录的当前版本信息与第一次取出来的version值进行比对，如果数据库表当前版本号与第一次取出来的version值相等，则予以更新，否则认为是过期数据。
2. 使用时间戳（timestamp）。乐观锁定的第二种实现方式和第一种差不多，同样是在需要乐观锁控制的table中增加一个字段，名称无所谓，字段类型使用时间戳（timestamp）, 和上面的version类似，也是在更新提交的时候检查当前数据库中数据的时间戳和自己更新前取到的时间戳进行对比，如果一致则OK，否则就是版本冲突。

Java JUC中的atomic包就是乐观锁的一种实现，AtomicInteger 通过CAS（Compare And Set）操作实现线程安全的自增。

 MySQL InnoDB采用的是两阶段锁定协议（two-phase locking protocol）。在事务执行过程中，随时都可以执行锁定，锁只有在执行 COMMIT或者ROLLBACK的时候才会释放，并且所有的锁是在同一时刻被释放。前面描述的锁定都是隐式锁定，InnoDB会根据事务隔离级别在需要的时候自动加锁。

另外，InnoDB也支持通过特定的语句进行显示锁定，这些语句不属于SQL规范：

- SELECT ... LOCK IN SHARE MODE
- SELECT ... FOR UPDATE

 

### 案例

通过一个小案例展示乐观锁和悲观锁的使用

考虑电商秒杀系统中，如果保证商品不超买，要保证数据的一致性

假设一张商品表

```sql
create table tb_product(
	id int not null auto_increment primary key,
    stock int not null 
)ENGINE=InnoDB DEFAULT CHARSET=utf8
```

 在不考虑并发的情况下，修改商品库存的伪代码如下：

```java
 /**
     * 更新库存(不考虑并发)
     * @param productId
     * @return
     */
public boolean updateStockRaw(Long productId){
    ProductStock product = query("SELECT * FROM tb_product WHERE id=#{productId}", productId);
    if (product.getNumber() > 0) {
        int updateCnt = update("UPDATE tb_product SET stock=stock-1 WHERE id=#{productId}", productId);
        if(updateCnt > 0){    //更新库存成功
            return true;
        }
    }
    return false;
    }
```

但是这种方式在多线程并发的情况下可能会出现超卖问题。

下面演示使用悲观锁和乐观锁来解决这个问题。

#### 使用悲观锁

```java
/**
     * 更新库存(使用悲观锁)
     * @param productId
     * @return
     */
public boolean updateStock(Long productId){
    //先锁定商品库存记录
    ProductStock product = query("SELECT * FROM tb_product WHERE id=#{productId} FOR UPDATE", productId);
    if (product.getNumber() > 0) {
        int updateCnt = update("UPDATE tb_product SET stock=stock-1 WHERE id=#{productId}", productId);
        if(updateCnt > 0){    //更新库存成功
            return true;
        }
    }
    return false;
}
```



 #### 使用乐观锁

```java
/**
     * 下单减库存
     * @param productId
     * @return
     */
public boolean updateStock(Long productId){
    int updateCnt = 0;
    while (updateCnt == 0) {
        ProductStock product = query("SELECT * FROM tb_product WHERE product_id=#{productId}", productId);
        if (product.getNumber() > 0) {
            updateCnt = update("UPDATE tb_product SET stock=stock-1 WHERE product_id=#{productId} AND number=#{number}", productId, product.getNumber());
            if(updateCnt > 0){    //更新库存成功
                return true;
            }
        } else {    //卖完啦
            return false;
        }
    }
    return false;
}
```



 

 

 

 

 

 

 

 

 