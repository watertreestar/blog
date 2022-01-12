---
title: CopyOnWriteList揭秘
date: 2018-12-12 14:00:34
tags: [Java,集合]
categories: Java基础
---



## Vector和SynchronizedList

ArrayList是用来代替Vector，Vector是线程安全的容器，因为它在方法上都加上了synchronized同步关键字

例如：
```java
public synchronized void copyInto(Object[] anArray) {
        System.arraycopy(elementData, 0, anArray, 0, elementCount);
}

/**
 * Trims the capacity of this vector to be the vector's current
 * size. If the capacity of this vector is larger than its current
 * size, then the capacity is changed to equal the size by replacing
 * its internal data array, kept in the field {@code elementData},
 * with a smaller one. An application can use this operation to
 * minimize the storage of a vector.
 */
public synchronized void trimToSize() {
    modCount++;
    int oldCapacity = elementData.length;
    if (elementCount < oldCapacity) {
        elementData = Arrays.copyOf(elementData, elementCount);
    }
}
```

<!--more-->

而Collections.synchronizedList方法也是在方法内部加了synchronized关键字
![](/img/SynchronizedList对象.png)

## 问题
```java
public static void main(String[] args) {
	Vector vector = new Vector();
	vector.add("a");
	vector.add("b");
	vector.add("c");
	new Thread(()->{
		getLast(vector);
	}).start();
	new Thread(()->{
		removeLast(vector);
	}).start();
	
	new Thread(()->{
		getLast(vector);
	}).start();
	new Thread(()->{
		removeLast(vector);
	}).start();
}

private static void removeLast(Vector vector) {
	int index  = vector.size() - 1;
	vector.remove(index);
}

private static Object getLast(Vector vector) {
	int index = vector.size() - 1;
	return vector.get(index);
}
```
以上这样的代码可能会发生异常，线程在交替执行的时候，我们自己方法getLast和removeLast没有保证原子性

要解决以上问题也很简单，就是在我们自己写的方法中做同步处理，例如添加synchronized关键字，想下面示例这样：
```java
private synchronized static void removeLast(Vector vector) {
	int index  = vector.size() - 1;
	vector.remove(index);
}

private synchronized static Object getLast(Vector vector) {
	int index = vector.size() - 1;
	return vector.get(index);
}
```

再看遍历Vector集合的时候
![](/img/Vector遍历异常.png)

例如，遍历获取vector.size()为3，当其他线程对容器做了修改后，此时容器的size为2，遍历获取get(3)就会出现异常

如果使用for-each(迭代器)来做上面的操作，会抛出ConcurrentModificationException异常

![](/img/foreach遍历异常.png)

要解决这个问题，也是在遍历方法对vector加锁

## CopyOnWriteList

一般来说，我们会认为：CopyOnWriteArrayList是同步List的替代品，CopyOnWriteArraySet是同步Set的替代品

无论是Hashtable到ConcurrentHashMap，Vector到CopyOnWriteArrayList。
JUC下支持并发的容器与老一代的线程安全类相比，都是在做锁粒度的优化

### 实现

什么是COW
> 如果有多个调用者（callers）同时请求相同资源（如内存或磁盘上的数据存储），他们会共同获取相同的指针指向相同的资源，
直到某个调用者试图修改资源的内容时，系统才会真正复制一份专用副本（private copy）给该调用者，
而其他调用者所见到的最初的资源仍然保持不变。
优点是如果调用者没有修改该资源，就不会有副本（private copy）被建立，因此多个调用者只是读取操作时可以共享同一份资源。

看看CopyOnWriteArrayList中的数据结构
```java
/** The lock protecting all mutators */
final transient ReentrantLock lock = new ReentrantLock();

/** The array, accessed only via getArray/setArray. */
private transient volatile Object[] array;

/**
 * Gets the array.  Non-private so as to also be accessible
 * from CopyOnWriteArraySet class.
 */
final Object[] getArray() {
    return array;
}

/**
 * Sets the array.
 */
final void setArray(Object[] a) {
    array = a;
}

```

数据结构比起ConcurrentHashMap来说很简单,使用Lock来上锁（修改数据的时候），使用Object数组来保持数据

CopyOnWriteArrayList的特点
- CopyOnWriteArrayList是线程安全容器(相对于ArrayList)，底层通过复制数组的方式来实现。
- CopyOnWriteArrayList在遍历的使用不会抛出ConcurrentModificationException异常，并且遍历的时候就不用额外加锁
- 元素可以为null

### 揭秘

CopyOnWriteList如果做到并发环境下遍历容器而不发生异常呢？

接下来我们看看iterator方法，该方法返回的是COWIterator类。我们可以看看这个类是怎么组成的
```java
static final class COWIterator<E> implements ListIterator<E> {
    /** Snapshot of the array */
    private final Object[] snapshot;
    /** Index of element to be returned by subsequent call to next.  */
    private int cursor;

    private COWIterator(Object[] elements, int initialCursor) {
        cursor = initialCursor;
        snapshot = elements;
    }

    public boolean hasNext() {
        return cursor < snapshot.length;
    }

    public boolean hasPrevious() {
        return cursor > 0;
    }

    @SuppressWarnings("unchecked")
    public E next() {
        if (! hasNext())
            throw new NoSuchElementException();
        return (E) snapshot[cursor++];
    }

    @SuppressWarnings("unchecked")
    public E previous() {
        if (! hasPrevious())
            throw new NoSuchElementException();
        return (E) snapshot[--cursor];
    }

    public int nextIndex() {
        return cursor;
    }

    public int previousIndex() {
        return cursor-1;
    }

    /**
     * Not supported. Always throws UnsupportedOperationException.
     * @throws UnsupportedOperationException always; {@code remove}
     *         is not supported by this iterator.
     */
    public void remove() {
        throw new UnsupportedOperationException();
    }

    /**
     * Not supported. Always throws UnsupportedOperationException.
     * @throws UnsupportedOperationException always; {@code set}
     *         is not supported by this iterator.
     */
    public void set(E e) {
        throw new UnsupportedOperationException();
    }

    /**
     * Not supported. Always throws UnsupportedOperationException.
     * @throws UnsupportedOperationException always; {@code add}
     *         is not supported by this iterator.
     */
    public void add(E e) {
        throw new UnsupportedOperationException();
    }

    @Override
    public void forEachRemaining(Consumer<? super E> action) {
        Objects.requireNonNull(action);
        Object[] elements = snapshot;
        final int size = elements.length;
        for (int i = cursor; i < size; i++) {
            @SuppressWarnings("unchecked") E e = (E) elements[i];
            action.accept(e);
        }
        cursor = size;
    }
}
```

可以看到类中有一个 Object[] snapshot这样的数组，根据代码可以直到这个数组保持的是待遍历的数组，对应的的就是CopyOnWriteArrayList中
保存数据的数组

由上我们可以知道，迭代器中保存的是获取CopyOnWriteList集合迭代器时的数据。所以在迭代过程中修改原来集合的数据不会影响到迭代器的遍历，所以CopyOnWriteList不能保证数据的实时一致性。











