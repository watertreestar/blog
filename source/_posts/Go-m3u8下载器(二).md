---
title: Go-m3u8下载器(二)
date: 2021-05-05 08:44:43
tags: [Go,m3u8]
categories: Go
---

## 前言

上篇中分析了一个m3u8文件的包含的属性，今天来通过代码来表示出这个数据结构并实现下载

## 代码

### 1. 数据结构定义

上一篇定义出了一个m3u8文件的结构，那我们现在就从这个文件中读取出计算机能够识别的结构。

<!--more-->

这个文件的parse非常简单，不涉及到复杂的语法，现在我们需要覆盖的范围也就只是上一篇提到的几个，所以关键字也没有几个。那么我们就可以按行读取出来，
每一行就是一个字符串，根据这个字符串的头部来判断是一个什么结构，读取的过程中顺便判断这个文件是不是合法的，很容易。


首先我们需要一个struct来表示一个m3u8文件
```go
type M3u8 struct {
	Version        int8              // EXT-X-VERSION:version
	MediaSequence  uint64            // Default 0, #EXT-X-MEDIA-SEQUENCE:sequence
	Segments       []*Segment        // Define a Play List
	MasterPlaylist []*MasterPlaylist // Define a Master Play List
	Keys           map[int]*Key      // Keys for per segment
	EndList        bool              // #EXT-X-ENDLIST
	PlaylistType   PlaylistType      // VOD or EVENT
	TargetDuration float64           // #EXT-X-TARGETDURATION:duration
}
```

上面看到有Segment和MasterPlayList,这两个二选一，也就是上篇说的一个m3u8可以是一个MasterPlayList来提供多码率，从MasterPalyList中可以选择一个
特定的码率，然后拿到一个新的m3u8文件，这个m3u8中包含了多个Segment，Segment包含了ts片段（也就是一个代表ts的URI）.还看到一个Key数组，这个是对于每一个
Segment的加密密钥

```go
// Segment
// #EXTINF:10.000000,
// 5dd92bfb879c6421d7281c769f0f8c93-4.ts
type Segment struct {
	URI      string
	KeyIndex int
	Title    string  // #EXTINF: duration,<title>
	Duration float32 // #EXTINF: duration,<title>
	Length   uint64  // #EXT-X-BYTERANGE: length[@offset]
	Offset   uint64  // #EXT-X-BYTERANGE: length[@offset]
}

// MasterPlaylist
// #EXT-X-STREAM-INF:PROGRAM-ID=1,BANDWIDTH=240000,RESOLUTION=416x234,CODECS="avc1.42e00a,mp4a.40.2"
type MasterPlaylist struct {
	URI        string
	BandWidth  uint32
	Resolution string
	Codecs     string
	ProgramID  uint32
}

// Key
// #EXT-X-KEY:METHOD=AES-128,URI="key.key"
type Key struct {
	// 'AES-128' or 'NONE'
	// If the encryption method is NONE, the URI and the IV attributes MUST NOT be present
	Method CryptMethod
	URI    string
	IV     string
}
```

### 2. parser

定义好这个结构后，就需要从文件中解析出这个结构，我们要做的就是从一个文件中读取一行，把这一行作为字符串，判断字符串的头部是什么开始的，如果匹配上了，就进一步处理
比如我们遇到一行
```
#EXTINF:10.000000,hello
```
我们就可以认为这是一个segment的的duration和title定义,那么我们就可以按照以下的方式来解析
```go
case strings.HasPrefix(line, "#EXTINF:"):
    if extInf {
        return nil, fmt.Errorf("duplicate EXTINF: %s, line: %d", line, i+1)
    }
    if seg == nil {
        seg = new(Segment)
    }
    var s string
    if _, err := fmt.Sscanf(line, "#EXTINF:%s", &s); err != nil {
        return nil, err
    }
    if strings.Contains(s, ",") {
        split := strings.Split(s, ",")
        seg.Title = split[1]
        s = split[0]
    }
    df, err := strconv.ParseFloat(s, 32)
    if err != nil {
        return nil, err
    }
    seg.Duration = float32(df)
    seg.KeyIndex = keyIndex
    extInf = true
```

整个parse过程就类似于上面这种，通过for + switch-case 来实现。其实就是一个简单的词法分析器，由于这里我们没有做语法分析，所以对于错误我们不能发现。
更加完善的词法分析可以了解编译原理的知识，或者通过有限自动机来实现

### 3. download

完成分析，构造出我们要的结构以后，就可以来进行下载了，通过http请求，然后保存每一个ts片段，最后我们把所有的ts片段合并成一个文件便完成了下载。
为了加快下载的速度，当然不能少了协程

关键下载的代码：
```go
var wg sync.WaitGroup
for {
    tsIdx, end, err := d.next()
    if err != nil {
        if end {
            break
        }
        continue
    }
    wg.Add(1)
    go func(idx int) {
        defer wg.Done()
        if err := d.download(idx); err != nil {
            // Back into the queue, retry request
            fmt.Printf("[failed] %s\n", err.Error())
            if err := d.back(idx); err != nil {
                fmt.Printf(err.Error())
            }
        }
    }(tsIdx)
}
wg.Wait()
if err := d.merge(); err != nil {
    return err
}
return nil
```

这个工具整体来说比较简单，这里这是提供一种思路，本身就很容易通过任何一门语言来实现

在做这个过程中，我也参考了别人的思路和代码。