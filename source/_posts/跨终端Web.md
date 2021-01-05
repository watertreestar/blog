---
title: 跨终端Web
date: 2018-09-07 17:43:45
tags: [web]
categories: web
---

### 一、跨终端web

一提到跨终端，第一反应往往就是响应式布局。这至少说明两点：首先，响应式本身与跨终端之间有着某种本质的联系；其次，人们误以为跨终端和响应式是同一件事。“跨终端 Web”是最终希望达到的目的，而达到这个目的的手段有很多，响应式仅仅是其中的一种方式而已。这些方式至少包括：

- 响应式
- 多站点
- 多模板
- 多平台

<!--more-->

#### 1、响应式(单域)

**缺点：**

- **DOM冗余，javascript冗余**：对于DOM结构异常庞大复杂的页面而言，响应式不能解决移动端DOM冗余的问题，JavaScript 脚本冗余也是一个问题；
- **耦合度高**：从工程实践来看，单个复杂响应式页面的维护成本并不比单独维护多个版本的页面成本低，并且由于响应式存在的内在耦合性，这个维护成本在复杂页面频繁更新时反而更高。
- **超出css可控制范围**：响应式本质上是依靠 CSS 处理展现层面的差异，大部分项目的移动端和 PC 端存在着不仅仅是展示上的差异，在交互形式上的巨大差异也会导致 DOM 结构上的差异，这种差异已经远远超出 CSS 所能控制的范围。

#### 2、多站点(单域)

**缺点：**

通常一个网站要适配几个版本，针对手机、IPAD、小屏笔记本、大屏台式机，仅仅首页就要适配多个站点，整站下来维护成本太高。

#### 3、多模板(多域)

> 多模板是响应式和多站点相结合的一种方案。

多模板的优点在于一个页面只有一个 URL，无须服务器端复杂的 URL 映射规则和终端检测等手段进行跳转。虽然解决了响应式中 DOM 冗余的问题，但是由于单个页面存在多套模板，还需要在模板动态加载和首次服务器渲染等环节进行优化。

#### 4、多平台

Native App 的确也是实现跨终端 Web 的一种途径

**优点：**

- 更好的性能、
- 更丰富的系统级功能的调用、
- 标准的发布渠道（通常是应用商店）

**缺点：**

- 发布成本高
- 开发成本高
- 潜在的风险：如：ios严重依赖app store



### 二、Mobile Web

html5有几大特性，虽然表面看上去只是一个版本的html，但其实我们通常意义上所说的html ~= html5 + css3 + javascript

#### 1、html5特点

- 语意化：新增了一系列的语意化标签，更利于网页的seo优化等等
- 离线存储：包括local storage等
- 设备访问：如定位信息、移动设备传感器等
- 多媒体：增加video、audio标签，提供原生的视频、音频访问
- 图形接口：增加canvas 标签
- 性能&优化：
- css3：

#### 2、针对移动web的页面模板

针对移动web页面，html5增加了一系列的 meta 标签，在上一篇文章中做过详细介绍，这里就不在赘述了，[传送门：移动前端的html5头标签head](http://iqianduan.net/blog/mobile_web_html5_head)

#### 3、触屏事件

touch 以及 基于touch 的各种事件，drag（拖拽）、hold（长按）、pinch（捏）、rotate（旋转）、shake（重力感应等）

| 事件类别 | 事件描述                                                     | 简称     | 别称                                                         |
| -------- | ------------------------------------------------------------ | -------- | ------------------------------------------------------------ |
| tap      | 移动平台默认浏览器的click事件有300ms+的延时,通常使用touch事件模拟, 为区别点击称为拍击:. tap拍击 . doubletap 双击. hold 长按. tapn n(2,3..)指拍击 | 拍击     | . android: touch. hold称呼较多: . android/ios: long press.wp: tap and hold. 也有称为press |
| swipe    | 按方向细分为:. swipe 单指滑动. swipeleft 单指向左滑动. swiperight 单指向右滑动. swipeup 单指向上滑动. swipedown 单指向下滑动. swipen n(2,3..)指滑动 | 滑动     | wp: flick                                                    |
| drag     | . drag 拖拽. dragstart 拖拽开始. dragend 拖拽结束. dragup 向上拖拽. dragdown 向下拖拽. dragleft 向左拖拽. dragright 向右拖拽 | 拖拽     | ios/wp: pan                                                  |
| pinch    | 常用于放大(zoom in)缩小(zoom out)视图:. pinchin 双指捏合. pinchout 双指展开. squeeze 五指捏合. splay 五指展开 | 捏       | . android: pinch open/close. pinchout也有称为spread          |
| rotate   | 常用于旋转视图 . rotatecw 顺时针旋转. rotateccw 逆时针旋转   | 旋转     |                                                              |
| shake    | 常用于游戏中控制方向, 细分为:. shake 移动设备. shakeup 向上移动设备. shakedown 向下移动设备. shakeleft 向左移动设备. shakeright 向右移动设备. shakeforward 向前移动设备. shakeback 向后移动设备. shakeleftright 左右移动设备. shakeforwardback 前后移动设备. shakeupdown 上下移动设备 | 重力感应 |                                                              |

#### 4、调试

1、远程调试

- Mobile Emulation：chrome 上面启动开发者工具，即可开启移动仿真状态
- ios 远程调试 手机上 safari 浏览器开启开发者模式（设置--safari--高级--打开web检查器），电脑上面打开 safari 浏览器的开发模式，连接上手机，找到你手机上面打开的页面即可进行调试了。
- Android 远程调试 安装Addroid Chrome 31+，使用USB 连接上手机，开启android的 USB debugger，安装ADB 扩展，安装后手动启动，PC chrome 使用 about: inspect 开启远程调试的控制台，单击 inspect 开始调试
- weinre
- HTTP 代理服务器

2、设备调试

- 设备模拟器
- 远程设备

### 三、基准

### 四、检测

#### 1、终端

**分类**：

- 按设备类型划分：目前普遍说的终端为三大类：PC电脑、平板、手机，当然TV 电视也即将成为第四大类
- 按操作系统划分：
  - apple：OS X（桌面系统）、iOS（iPhone和Pad）
  - Google：Android（Phone和Pad）
  - Microsoft：覆盖手机、平板、个人电脑的windows系列

**终端检测**：

- 需要检测的场景：显示或隐藏特定内容////加载特定的静态资源样式、脚本////静态扫描修改文件源////返回指定图片质量、大小的图片
- 检测的原理：用户代理（User Agent---UA）最为常用
- 检测的实现：

**遗留问题**

- 硬件信息：UA 不准（浏览器厂商把UA伪装）
- 更精准的终端检测：引入机器学习，采集一定数量的样本学习后用于终端检测

### 五、接口

#### 1、跨终端流程复用

- 如：购物网站前台页面展示有5种形式（PC、Phone Web、Pad Web、Phone App、Pad App），但后台的逻辑基本一致，则使用一套接口，增加流程的复用性。
- 如：移动优先，优先考虑移动端页面的展示，再开发PC的时候可适当扩展API

#### 2、IF(interFace)

IF 主要包括以下几个部分：

- 接口描述：请求、响应数据格式
- 接口文档：由接口描述生成接口文档
- 接口Mock：由接口描述生成接口 Mock 数据
- 接口校验：提供校验服务（HTTP）和校验工具包，支持多重格式的接口校验

**缘由：来自于一次重构**

### 六、定位

#### 1、定位：

- hash：不利于SEO
- history API：可结合ajax通过pjax的方式实现修改路由同时不刷新页面，只刷新部分内容
  - history.pushState
  - history.replaceState
  - window.onpopstate：页面前进后退的时候触发
- 视图定位：

#### 2、数据：