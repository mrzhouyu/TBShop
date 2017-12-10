#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/12/10 9:23
# @Author  : Yu
# @Site    : 
# @File    : config.py
#数据库连接信息配置
MONGO_HOST='localhost'
MONGO_DB='taobao'
MONGO_TABLE='meishi'
#无头浏览器配置 不加载图片 开启缓存
PHANTOMJS_ARGS=['--load-images=false','--disk-cache=true']
#这里可以自定义 信息
KEY_WORDLD='美食'