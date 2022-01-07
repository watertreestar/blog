<meta charset="<?php $this->options->charset(); ?>">
<meta http-equiv="X-UA-Compatible" content="IE=edge">
<meta name="renderer" content="webkit">
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1">
<meta name="baidu-site-verification" content="bPNaHbBDdS" />
<title></title>

<!-- 使用url函数转换相关路径 -->
<!-- <link rel="stylesheet" href="//cdnjscn.b0.upaiyun.com/libs/normalize/2.1.3/normalize.min.css"> -->
<link rel="stylesheet" href="<?php $this->options->themeUrl('./asset/font-awesome-4.7.0/css/font-awesome.min.css'); ?>">
<link rel="stylesheet" href="<?php $this->options->themeUrl('grid.css'); ?>">
<link rel="stylesheet" href="<?php $this->options->themeUrl('style.css'); ?>">

<!--[if lt IE 9]>
<script src="//cdnjscn.b0.upaiyun.com/libs/html5shiv/r29/html5.min.js"></script>
<script src="//cdnjscn.b0.upaiyun.com/libs/respond.js/1.3.0/respond.min.js"></script>
<![endif]-->

<script id="page-configurations">
    // https://hexo.io/docs/variables.html
    CONFIG.page = {
        sidebar: {{ page.sidebar | json }},
        isHome : {{ is_home() }},
        isPost : {{ is_post() }},
        lang   : '{{ page.lang }}'
    };
</script>