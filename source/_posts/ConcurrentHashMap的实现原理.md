---
title: ConcurrentHashMap的实现原理
date: 2018-08-18 19:22:34
tags: [Java,集合]
categories: Java基础
---

HashMap是一个线程不安全的容器，当容量大于`总量*负载因子`发生扩容时可能会出现环形链表从而导致死循环

> 扩容就是rehash，这个会重新将原数组的内容重新hash到新的扩容数组中，在多线程的环境下，存在同时其他的元素也在进行put操作，如果hash值相同，可能出现同时在同一数组下用链表表示

因此引进了线程安全的容器`ConcurrentHashMap`

<!--more-->

`ConcurrentHashMap`在JDK1.7 和 JDK1.8中的实现有所不同

#### JDK1.7中的实现

##### 先来看看1.7中数据结构实现的图示

![img](ConcurrentHashMap1.7中数据结构.png)

由图中可以看出ConcurrentHashMap是由`Segment数组`，`HashEntry数组`组成的。这里和`HashMap`一样,都是`数组+链表`的形式

ConcurrentHashMap采用了分段锁的技术，其中一个`Segement`就是一个Lock，其继承自`ReentrantLock`,这样当一个线程占用了锁访问一个`Segment`时，不会影响到其它的`Segment`

`Segment`数组的意义就是将一个大的table分成多个小的table来进行加锁，而一个Segment存储的是HashEntry数组+链表，这和HashMap的数据结构一致

- Segment的大小最多65536个，没有指定concurrencyLevel元素初始化，Segment的大小ssize默认为16

- 每一个Segment元素下的HashEntry的初始化也是按照位于运算来计算

  ```
  int cap = 1;
  while (cap < c)
      cap <<= 1;
  ```

  所以，HashEntry数组的最小为2

  ​

##### get 方法

ConcurrentHashMap的get方法在整个过程中都不需要加锁

执行`get`方法的时候，需要先将`key`通过`hash`之后定位到具体的`Segment`，然后再通过一次`hash`定位到具体的元素上。

注意：为了保证可见性,HashEntry中的 `value`属性使用了`volatile`修饰

##### put 方法

内部 `HashEntry` 类

```
static final class HashEntry<K,V> {
       final int hash;
       final K key;
       volatile V value;
       volatile HashEntry<K,V> next;

       HashEntry(int hash, K key, V value, HashEntry<K,V> next) {
           this.hash = hash;
           this.key = key;
           this.value = value;
           this.next = next;
       }
   }
```

虽然 HashEntry 中的 value 是用 `volatile` 关键词修饰的，但是并不能保证并发的原子性，所以 put 操作时仍然需要加锁处理

首先也是通过 Key 的 Hash 定位到具体的 Segment，在 put 之前会进行一次扩容校验。

Segment实现了ReentrantLock,也就带有锁的功能，当执行put操作时，会进行第一次key的hash来定位Segment的位置，如果该Segment还没有初始化，即通过CAS操作进行赋值，然后进行第二次hash操作，找到相应的HashEntry的位置，这里会利用继承过来的锁的特性，在将数据插入指定的HashEntry位置时（链表的尾端），会通过继承ReentrantLock的tryLock（）方法尝试去获取锁，如果获取成功就直接插入相应的位置，如果已经有线程获取该Segment的锁，那当前线程会以自旋的方式去继续的调用tryLock（）方法去获取锁，超过指定次数就挂起，等待唤醒。

##### size 方法

每一个`Segment`都有一个volatile修饰的全局变量`count`,要获取整个Map集合的size的时候，就需要获取每个Segment的count，然后累加起来。虽然`count`变量被`volatile`修饰符修饰，但这个不能保证操作的原子性，可能出现当获取size的时候还有其它线程在做插入操作。这样就引发了并发的问题

但是如果在获取size的时候将其它操作也加锁，这样就造成效率问题

所以解决的办法是：先尝试两次将`count`累加，当两次结果不一致时，才加锁来统计count

`Councurrent` 中每一个`Segment`都包含一个`modCount`变量，每当进行一次添加/删除操作，`modCount`的值就会发生变化，只要`modCount`发生变化那么就认为容器大小也在发生变化

#### JDK 1.8实现

##### 先来看看1.8中数据结构实现的图示

![img](ConcurrentHashMap1.8中数据结构.png)

JDK 1.8中的`ConcurrentHashMap`和1.7中的实现有着明显的差异

其中抛弃了原有的 Segment 分段锁，而采用了 `CAS + synchronized` 来保证并发安全性.

采用了`Node数组+链表+红黑树`的数据结构来实现

##### 基本常量设计和数据结构

在深入了解JDK1.8中的`ConcurrentHashMap`前，先来了解一下基本常量和数据结构

```
// node数组最大容量：2^30=1073741824
private static final int MAXIMUM_CAPACITY = 1 << 30;
// 默认初始值，必须是2的幕数
private static final int DEFAULT_CAPACITY = 16;
//数组可能最大值，需要与toArray（）相关方法关联
static final int MAX_ARRAY_SIZE = Integer.MAX_VALUE - 8;
//并发级别，遗留下来的，为兼容以前的版本
private static final int DEFAULT_CONCURRENCY_LEVEL = 16;
// 负载因子
private static final float LOAD_FACTOR = 0.75f;
// 链表转红黑树阀值,> 8 链表转换为红黑树
static final int TREEIFY_THRESHOLD = 8;
//树转链表阀值，小于等于6（tranfer时，lc、hc=0两个计数器分别++记录原bin、新binTreeNode数量，<=UNTREEIFY_THRESHOLD 则untreeify(lo)）
static final int UNTREEIFY_THRESHOLD = 6;
static final int MIN_TREEIFY_CAPACITY = 64;
private static final int MIN_TRANSFER_STRIDE = 16;
private static int RESIZE_STAMP_BITS = 16;
// 2^15-1，help resize的最大线程数
private static final int MAX_RESIZERS = (1 << (32 - RESIZE_STAMP_BITS)) - 1;
// 32-16=16，sizeCtl中记录size大小的偏移量
private static final int RESIZE_STAMP_SHIFT = 32 - RESIZE_STAMP_BITS;
// forwarding nodes的hash值
static final int MOVED     = -1; 
// 树根节点的hash值
static final int TREEBIN   = -2; 
// ReservationNode的hash值
static final int RESERVED  = -3; 
// 可用处理器数量
static final int NCPU = Runtime.getRuntime().availableProcessors();
//存放node的数组
transient volatile Node<K,V>[] table;
/*控制标识符，用来控制table的初始化和扩容的操作，不同的值有不同的含义
 *当为负数时：-1代表正在初始化，-N代表有N-1个线程正在 进行扩容
 *当为0时：代表当时的table还没有被初始化
 *当为正数时：表示初始化或者下一次进行扩容的大小
private transient volatile int sizeCtl;
```

##### Node的数据结构

```
static class Node<K,V> implements Map.Entry<K,V> {
        final int hash;
        final K key;
        volatile V val;
        volatile Node<K,V> next;

        Node(int hash, K key, V val, Node<K,V> next) {
            this.hash = hash;
            this.key = key;
            this.val = val;
            this.next = next;
        }

        public final K getKey()       { return key; }
        public final V getValue()     { return val; }
        public final int hashCode()   { return key.hashCode() ^ val.hashCode(); }
        public final String toString(){ return key + "=" + val; }
        public final V setValue(V value) {
            throw new UnsupportedOperationException();
        }

        public final boolean equals(Object o) {
            Object k, v, u; Map.Entry<?,?> e;
            return ((o instanceof Map.Entry) &&
                    (k = (e = (Map.Entry<?,?>)o).getKey()) != null &&
                    (v = e.getValue()) != null &&
                    (k == key || k.equals(key)) &&
                    (v == (u = val) || v.equals(u)));
        }
         //用于map中的get（）方法，子类重写
        Node<K,V> find(int h, Object k) {
            Node<K,V> e = this;
            if (k != null) {
                do {
                    K ek;
                    if (e.hash == h &&
                        ((ek = e.key) == k || (ek != null && k.equals(ek))))
                        return e;
                } while ((e = e.next) != null);
            }
            return null;
        }
}
```

##### TreeNode的数据结构

`TreeNode`继承与`Node`，但是数据结构换成了二叉树结构，它是`红黑树`的数据的存储结构，用于红黑树中存储数据，当链表的节点数大于`8`时会转换成红黑树的结构，他就是通过TreeNode作为存储结构代替Node来转换成黑红树

红黑树数据结构源代码

```
static final class TreeNode<K,V> extends Node<K,V> {
    //树形结构的属性定义
    TreeNode<K,V> parent;  // red-black tree links
    TreeNode<K,V> left;
    TreeNode<K,V> right;
    TreeNode<K,V> prev;    // needed to unlink next upon deletion
    boolean red; //标志红黑树的红节点
    TreeNode(int hash, K key, V val, Node<K,V> next,
             TreeNode<K,V> parent) {
        super(hash, key, val, next);
        this.parent = parent;
    }
    Node<K,V> find(int h, Object k) {
        return findTreeNode(h, k, null);
    }
    //根据key查找 从根节点开始找出相应的TreeNode，
    final TreeNode<K,V> findTreeNode(int h, Object k, Class<?> kc) {
        if (k != null) {
            TreeNode<K,V> p = this;
            do  {
                int ph, dir; K pk; TreeNode<K,V> q;
                TreeNode<K,V> pl = p.left, pr = p.right;
                if ((ph = p.hash) > h)
                    p = pl;
                else if (ph < h)
                    p = pr;
                else if ((pk = p.key) == k || (pk != null && k.equals(pk)))
                    return p;
                else if (pl == null)
                    p = pr;
                else if (pr == null)
                    p = pl;
                else if ((kc != null ||
                          (kc = comparableClassFor(k)) != null) &&
                         (dir = compareComparables(kc, k, pk)) != 0)
                    p = (dir < 0) ? pl : pr;
                else if ((q = pr.findTreeNode(h, k, kc)) != null)
                    return q;
                else
                    p = pl;
            } while (p != null);
        }
        return null;
    }
}
```

##### ConcurrentHashMap的初始化

我们通过ConcurrentHashMap的构造方法可以看出，在构造方法中并没有做初始化的事。初始化放到了put操作中，这是和其它集合由区别的地方

![img](ConcurrentHashMap的构造方法.png)

##### put 操作过程

查看put 方法

```
/** Implementation for put and putIfAbsent */
final V putVal(K key, V value, boolean onlyIfAbsent) {
    if (key == null || value == null) throw new NullPointerException();
    int hash = spread(key.hashCode()); //两次hash，减少hash冲突，可以均匀分布
    int binCount = 0;
    for (Node<K,V>[] tab = table;;) { //对这个table进行迭代
        Node<K,V> f; int n, i, fh;
        //这里就是上面构造方法没有进行初始化，在这里进行判断，为null就调用initTable进行初始化，属于懒汉模式初始化
        if (tab == null || (n = tab.length) == 0)
            tab = initTable();
        else if ((f = tabAt(tab, i = (n - 1) & hash)) == null) {//如果i位置没有数据，就直接无锁插入
            if (casTabAt(tab, i, null,
                         new Node<K,V>(hash, key, value, null)))
                break;                   // no lock when adding to empty bin
        }
        else if ((fh = f.hash) == MOVED)//如果在进行扩容，则先进行扩容操作
            tab = helpTransfer(tab, f);
        else {
            V oldVal = null;
            //如果以上条件都不满足，那就要进行加锁操作，也就是存在hash冲突，锁住链表或者红黑树的头结点
            synchronized (f) {
                if (tabAt(tab, i) == f) {
                    if (fh >= 0) { //表示该节点是链表结构
                        binCount = 1;
                        for (Node<K,V> e = f;; ++binCount) {
                            K ek;
                            //这里涉及到相同的key进行put就会覆盖原先的value
                            if (e.hash == hash &&
                                ((ek = e.key) == key ||
                                 (ek != null && key.equals(ek)))) {
                                oldVal = e.val;
                                if (!onlyIfAbsent)
                                    e.val = value;
                                break;
                            }
                            Node<K,V> pred = e;
                            if ((e = e.next) == null) {  //插入链表尾部
                                pred.next = new Node<K,V>(hash, key,
                                                          value, null);
                                break;
                            }
                        }
                    }
                    else if (f instanceof TreeBin) {//红黑树结构
                        Node<K,V> p;
                        binCount = 2;
                        //红黑树结构旋转插入
                        if ((p = ((TreeBin<K,V>)f).putTreeVal(hash, key,
                                                       value)) != null) {
                            oldVal = p.val;
                            if (!onlyIfAbsent)
                                p.val = value;
                        }
                    }
                }
            }
            if (binCount != 0) { //如果链表的长度大于8时就会进行红黑树的转换
                if (binCount >= TREEIFY_THRESHOLD)
                    treeifyBin(tab, i);
                if (oldVal != null)
                    return oldVal;
                break;
            }
        }
    }
    addCount(1L, binCount);//统计size，并且检查是否需要扩容
    return null;
}
```

put 操作可以描述为以下过程

1. 没有初始化就先调用initTable()方法初始化table数组
2. 如果没有hash冲突就直接CAS插入
3. 如果还在扩容就先进行扩容
4. 如果存在hash冲突，就加锁来保证线程安全，这里有两种情况，一种是链表形式就直接遍历到尾端插入，一种是红黑树就按照红黑树结构插入
5. 最后一个如果该链表的数量大于阈值8，就要先转换成黑红树的结构，
6. 如果添加成功就调用addCount（）方法统计size，并且检查是否需要扩容

##### initTable 方法

```
private final Node<K,V>[] initTable() {
    Node<K,V>[] tab; int sc;
    while ((tab = table) == null || tab.length == 0) {//空的table才能进入初始化操作
        if ((sc = sizeCtl) < 0) //sizeCtl<0表示其他线程已经在初始化了或者扩容了，挂起当前线程 
            Thread.yield(); // lost initialization race; just spin
        else if (U.compareAndSwapInt(this, SIZECTL, sc, -1)) {//CAS操作SIZECTL为-1，表示初始化状态
            try {
                if ((tab = table) == null || tab.length == 0) {
                    int n = (sc > 0) ? sc : DEFAULT_CAPACITY;
                    @SuppressWarnings("unchecked")
                    Node<K,V>[] nt = (Node<K,V>[])new Node<?,?>[n];//初始化
                    table = tab = nt;
                    sc = n - (n >>> 2);//记录下次扩容的大小
                }
            } finally {
                sizeCtl = sc;
            }
            break;
        }
    }
    return tab;
}
```

##### get 操作过程

ConcurrentHashMap的get操作的流程很简单，也很清晰，可以分为三个步骤来描述

1. 计算hash值，定位到该table索引位置，如果是首节点符合就返回
2. 如果遇到扩容的时候，会调用标志正在扩容节点ForwardingNode的find方法，查找该节点，匹配就返回
3. 以上都不符合的话，就往下遍历节点，匹配就返回，否则最后就返回null

##### size 操作

```
public int size() {
    long n = sumCount();
    return ((n < 0L) ? 0 :
            (n > (long)Integer.MAX_VALUE) ? Integer.MAX_VALUE :
            (int)n);
}
final long sumCount() {
    CounterCell[] as = counterCells; CounterCell a; //变化的数量
    long sum = baseCount;
    if (as != null) {
        for (int i = 0; i < as.length; ++i) {
            if ((a = as[i]) != null)
                sum += a.value;
        }
    }
    return sum;
}
```

#### 总结

其实可以看出JDK1.8版本的ConcurrentHashMap的数据结构已经接近HashMap，相对而言，ConcurrentHashMap只是增加了同步的操作来控制并发，从JDK1.7版本的ReentrantLock+Segment+HashEntry，到JDK1.8版本中synchronized+CAS+HashEntry+红黑树

总结如下：

1. JDK1.8的实现降低锁的粒度，JDK1.7版本锁的粒度是基于Segment的，包含多个HashEntry，而JDK1.8锁的粒度就是HashEntry（首节点）
2. JDK1.8版本的数据结构变得更加简单，使得操作也更加清晰流畅，因为已经使用synchronized来进行同步，所以不需要分段锁的概念，也就不需要Segment这种数据结构了，由于粒度的降低，实现的复杂度也增加了
3. JDK1.8使用红黑树来优化链表，基于长度很长的链表的遍历是一个很漫长的过程，而红黑树的遍历效率是很快的，代替一定阈值的链表，这样形成一个最佳拍档