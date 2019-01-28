#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : 河北雪域网络科技有限公司 A.Star
# @contact: astar@snowland.ltd
# @site: www.snowland.ltd
# @file: models.py
# @time: 2018/10/1 23:09
# @Software: PyCharm


from django.db import models


class FriendLink(models.Model):
    site_name = models.CharField(max_length=32)
    url = models.URLField()
    show_flag = models.BooleanField(default=True)
    date_start = models.DateField(auto_now=True)
    date_end = models.DateField(default='9999-12-31 23:59:59')
    logo = models.ImageField(default=None, null=True)
