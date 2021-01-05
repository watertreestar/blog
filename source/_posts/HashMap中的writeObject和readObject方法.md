---
title: HashMap中的writeObject和readObject?
date: 2018-08-17 15:22:19
tags: [Java,集合]
categories: Java基础
---

#### 前言

HashMap中有两个私有方法

```java
private void writeObject(ObjectOutputStrem oos) throws IOException
private void readObject(ObjectInputStream ois) throws IOException
```

- 两个方法都是私有方法
- HashMap内部不调用此方法


<!--more-->


#### 为什么会存在这两个方法

##### 这两个方法的作用是什么

`writeObject`和`readObject`方法都是为了我`HashMap`的序列化而创建的

`HashMap`实现了`Serializable`接口，这表明该类可以被序列化，而JDK中提供序列化的类是`ObjectOutputStream`和`ObjectInputStream`.

`ObjectOutputStream`提供了`writeObject`方法来序列化自定义类

查看`writeObject`方法的内部实现可知，方法内会判断序列化的对象内部是否实现了`writeObject`方法，如果实现了就调用此方法，没有实现就调用默认的序列化方法

#### 为什么HashMap要自己实现writeObject和readObject方法，而不是使用JDK统一的默认序列化和反序列化操作呢？

首先要明确序列化的目的，将java对象序列化，一定是为了在某个时刻能够将该对象反序列化，而且一般来讲序列化和反序列化所在的机器是不同的，因为序列化最常用的场景就是跨机器的调用（把对象转化为字节流，才能进行网络传输），而序列化和反序列化的一个最基本的要求就是，反序列化之后的对象与序列化之前的对象是一致的。

HashMap中，由于Entry的存放位置是根据Key的Hash值来计算，然后存放到数组中的，对于同一个Key，在不同的JVM实现中计算得出的Hash值可能是不同的。

Hash值不同导致的结果就是：有可能一个HashMap对象的反序列化结果与序列化之前的结果不一致。即有可能序列化之前，Key=’AAA’的元素放在数组的第0个位置，而反序列化值后，根据Key获取元素的时候，可能需要从数组为2的位置来获取，而此时获取到的数据与序列化之前肯定是不同的。 



所以为了避免这个问题，HashMap采用了下面的方式来解决：

1. 将可能会造成数据不一致的元素使用transient关键字修饰，从而避免JDK中默认序列化方法对该对象的序列化操作。不序列化的包括：Entry[ ] table,size,modCount。
2. 自己实现writeObject方法，从而保证序列化和反序列化结果的一致性。



####  那么，HashMap又是通过什么手段来保证序列化和反序列化数据的一致性的呢

1. 首先，HashMap序列化的时候不会将保存数据的数组序列化，而是将元素个数以及每个元素的Key和Value都进行序列化。
2. 在反序列化的时候，重新计算Key和Value的位置，重新填充一个数组。