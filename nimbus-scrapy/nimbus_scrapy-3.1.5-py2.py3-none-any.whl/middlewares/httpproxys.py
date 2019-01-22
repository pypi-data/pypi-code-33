# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, division, unicode_literals

import os
import logging
import time
from datetime import datetime, timedelta
import redis
from redis.exceptions import RedisError
from twisted.web._newclient import ResponseNeverReceived
from scrapy.core.downloader.handlers.http11 import TunnelError
from twisted.internet import defer
from twisted.internet.error import TimeoutError, DNSLookupError, \
    ConnectionRefusedError, ConnectionDone, ConnectError, \
    ConnectionLost, TCPTimedOutError
from scrapy.exceptions import NotConfigured
from scrapy.utils.response import response_status_message
from scrapy import signals
from ..utils import smart_text, md5

logger = logging.getLogger(__name__)


DEFAULT_REDIS_CONFIG = {
    "host": '127.0.0.1',
    "port": 6379,
    "db": 4,
    "password": None
}


class HttpProxyMiddleware(object):
    # 遇到这些类型的错误直接当做代理不可用处理掉, 不再传给retrymiddleware
    DONT_RETRY_ERRORS = (TimeoutError, ConnectionRefusedError, ResponseNeverReceived, ConnectError, ValueError)

    def __init__(self, enabled=False, proxy_type="", flush=False, clean=False, stats=None, config=None):
        self.enabled = enabled
        self.proxy_type = proxy_type
        self.flush = flush
        self.clean = clean
        self.stats = stats
        self.config = config or {}
        self.redis = redis.StrictRedis(**self.config)
        self.prefix = "proxy"
        self.expire = timedelta(minutes=2)
        self.name = ""

        # 保存上次不用代理直接连接的时间点
        self.last_no_proxy_time = datetime.now()
        # 一定分钟数后切换回不用代理, 因为用代理影响到速度
        self.recover_interval = 20
        # 一个proxy如果没用到这个数字就被发现老是超时, 则永久移除该proxy. 设为0则不会修改代理文件.
        self.dump_count_threshold = 20
        # 存放代理列表的文件, 每行一个代理, 格式为proto://ip:port, 这个文件会被修改, 注意备份
        self.proxy_file = "proxyes.dat"
        # 是否在超时的情况下禁用代理
        self.invalid_proxy_flag = True
        # 当有效代理小于这个数时(包括直连), 从网上抓取新的代理, 可以将这个数设为为了满足每个ip被要求输入验证码后得到足够休息时间所需要的代理数
        # 例如爬虫在十个可用代理之间切换时, 每个ip经过数分钟才再一次轮到自己, 这样就能get一些请求而不用输入验证码.
        # 如果这个数过小, 例如两个, 爬虫用A ip爬了没几个就被ban, 换了一个又爬了没几次就被ban, 这样整个爬虫就会处于一种忙等待的状态, 影响效率
        self.extend_proxy_threshold = 10
        # 初始化代理列表
        self.proxyes = [{"proxy": None, "valid": True, "count": 0}]
        # 初始时使用0号代理(即无代理)
        self.proxy_index = 0
        # 表示可信代理的数量(如自己搭建的HTTP代理)+1(不用代理直接连接)
        self.fixed_proxy = len(self.proxyes)
        # 上一次抓新代理的时间
        self.last_fetch_proxy_time = datetime.now()
        # 每隔固定时间强制抓取新代理(min)
        self.fetch_proxy_interval = 120
        # 一个将被设为invalid的代理如果已经成功爬取大于这个参数的页面， 将不会被invalid
        self.invalid_proxy_threshold = 200

    @classmethod
    def from_crawler(cls, crawler):
        s = crawler.settings
        enabled = s.getbool('HTTP_PROXY_ENABLED', False)
        proxy_type = s.get('HTTP_PROXY_TYPE', "")
        flush = s.getbool('HTTP_PROXY_FLUSH', False)
        clean = s.getbool('HTTP_PROXY_CLEAN', True)
        config = s.get('HTTP_PROXY_REDIS', DEFAULT_REDIS_CONFIG)
        o = cls(enabled=enabled, proxy_type=proxy_type, flush=flush, clean=clean, stats=crawler.stats, config=config)
        crawler.signals.connect(o.spider_opened, signal=signals.spider_opened)
        crawler.signals.connect(o.spider_closed, signal=signals.spider_closed)
        return o

    def spider_opened(self, spider):
        try:
            if not self.config:
                self.enabled = False
                return
            self.redis = redis.StrictRedis(**self.config)
            self.redis.ping()
            self.name = smart_text(spider.name).lower()
            if self.flush:
                self.redis.flushdb()
            self._read_proxy_redis()
        except Exception as e:
            self.enabled = False

    def spider_closed(self, spider):
        self.redis = None

    def _get_prefix_key(self, key="*"):
        if self.proxy_type:
            f = "{}-{}-{}".format(self.prefix, self.proxy_type, key)
        else:
            f = "{}-{}".format(self.prefix, key)
        return f

    def _read_proxy_redis(self):
        key = self._get_prefix_key("*")
        keys = self.redis.keys(key)
        for k in keys:
            v = self.redis.get(k)
            v = v.strip()
            if not v or self.url_in_proxyes(v):
                continue
            self.proxyes.append({"proxy": v,
                                 "valid": True,
                                 "count": 0})

    def _set_invalid_proxy(self, index=0):
        try:
            if len(self.proxyes) > index > 0:
                proxy = self.proxyes[index].get("proxy", "")
                key = self._get_prefix_key(proxy)
                self.redis.expire(key, self.expire)
        except Exception as e:
            pass

    def _exists(self, key):
        return self.redis.exists(key)

    def _set_key(self, key, value):
        self.redis.set(key, value)

    def process_request(self, request, spider):
        """
        将request设置为使用代理
        """
        if self.proxy_index > 0 and datetime.now() > (self.last_no_proxy_time + timedelta(minutes=self.recover_interval)):
            logger.info("After %d minutes later, recover from using proxy" % self.recover_interval)
            self.last_no_proxy_time = datetime.now()
            self.proxy_index = 0
        request.meta["dont_redirect"] = True  # 有些代理会把请求重定向到一个莫名其妙的地址

        # spider发现parse error, 要求更换代理
        if "change_proxy" in list(request.meta.keys()) and request.meta["change_proxy"]:
            logger.info("change proxy request get by spider: %s" % request)
            self.invalid_proxy(request.meta["proxy_index"])
            request.meta["change_proxy"] = False
        self.set_proxy(request)

    def process_response(self, request, response, spider):
        """
        检查response.status, 根据status是否在允许的状态码中决定是否切换到下一个proxy, 或者禁用proxy
        """
        if "proxy" in list(request.meta.keys()):
            logger.debug("%s %s %s" % (request.meta["proxy"], response.status, request.url))
        else:
            logger.debug("None %s %s" % (response.status, request.url))

        # status不是正常的200而且不在spider声明的正常爬取过程中可能出现的
        # status列表中, 则认为代理无效, 切换代理
        if response.status != 200 \
                and (not hasattr(spider, "website_possible_httpstatus_list") \
                             or response.status not in spider.website_possible_httpstatus_list):
            logger.info("response status[%d] not in spider.website_possible_httpstatus_list" % response.status)
            self.invalid_proxy(request.meta["proxy_index"])
            new_request = request.copy()
            new_request.dont_filter = True
            return new_request
        else:
            return response

    def process_exception(self, request, exception, spider):
        """
        处理由于使用代理导致的连接异常
        """
        logger.debug("%s exception: %s" % (self.proxyes[request.meta["proxy_index"]]["proxy"], exception))
        request_proxy_index = request.meta["proxy_index"]

        # 只有当proxy_index>fixed_proxy-1时才进行比较, 这样能保证至少本地直连是存在的.
        if isinstance(exception, self.DONT_RETRY_ERRORS):
            if request_proxy_index > self.fixed_proxy - 1 and self.invalid_proxy_flag: # WARNING 直连时超时的话换个代理还是重试? 这是策略问题
                if self.proxyes[request_proxy_index]["count"] < self.invalid_proxy_threshold:
                    self.invalid_proxy(request_proxy_index)
                elif request_proxy_index == self.proxy_index:  # 虽然超时，但是如果之前一直很好用，也不设为invalid
                    self.inc_proxy_index()
            else:               # 简单的切换而不禁用
                if request.meta["proxy_index"] == self.proxy_index:
                    self.inc_proxy_index()
            new_request = request.copy()
            new_request.dont_filter = True
            return new_request

    def url_in_proxyes(self, url):
        """
        返回一个代理url是否在代理列表中
        """
        for p in self.proxyes:
            if url == p["proxy"]:
                return True
        return False

    def reset_proxyes(self):
        """
        将所有count>=指定阈值的代理重置为valid,
        """
        logger.info("reset proxyes to valid")
        for p in self.proxyes:
            if p["count"] >= self.dump_count_threshold:
                p["valid"] = True

    def fetch_new_proxyes(self):
        """
        从网上抓取新的代理添加到代理列表中
        """
        logger.info("extending proxyes using fetch_free_proxyes.py")
        new_proxyes = fetch_free_proxyes.fetch_all(https=self.use_https)
        logger.info("new proxyes: %s" % new_proxyes)
        self.last_fetch_proxy_time = datetime.now()

        for np in new_proxyes:
            if self.url_in_proxyes(np):
                continue
            else:
                self.proxyes.append({"proxy": np,
                                     "valid": True,
                                     "count": 0})
        if self.len_valid_proxy() < self.extend_proxy_threshold: # 如果发现抓不到什么新的代理了, 缩小threshold以避免白费功夫
            self.extend_proxy_threshold -= 1

    def len_valid_proxy(self):
        """
        返回proxy列表中有效的代理数量
        """
        count = 0
        for p in self.proxyes:
            if p["valid"]:
                count += 1
        return count

    def inc_proxy_index(self, current=-1):
        """
        将代理列表的索引移到下一个有效代理的位置
        如果发现代理列表只有fixed_proxy项有效, 重置代理列表
        如果还发现已经距离上次抓代理过了指定时间, 则抓取新的代理
        """
        assert self.proxyes[0]["valid"]
        if current != -1 and self.proxy_index != current:
            return
        while True:
            self.proxy_index = (self.proxy_index + 1) % len(self.proxyes)
            if self.proxyes[self.proxy_index]["valid"]:
                break

        # 两轮proxy_index==0的时间间隔过短， 说明出现了验证码抖动，扩展代理列表
        if self.proxy_index == 0 and datetime.now() < self.last_no_proxy_time + timedelta(minutes=2):
            logger.info("captcha thrashing")
            self.fetch_new_proxyes()

        if self.len_valid_proxy() <= self.fixed_proxy or self.len_valid_proxy() < self.extend_proxy_threshold: # 如果代理列表中有效的代理不足的话重置为valid
            self.reset_proxyes()

        if self.len_valid_proxy() < self.extend_proxy_threshold:  # 代理数量仍然不足, 抓取新的代理
            logger.info("valid proxy < threshold: %d/%d" % (self.len_valid_proxy(), self.extend_proxy_threshold))
            self.fetch_new_proxyes()

        logger.info("now using new proxy: %s" % self.proxyes[self.proxy_index]["proxy"])

        # 一定时间没更新后可能出现了在目前的代理不断循环不断验证码错误的情况, 强制抓取新代理
        #if datetime.now() > self.last_fetch_proxy_time + timedelta(minutes=self.fetch_proxy_interval):
        #    logger.info("%d munites since last fetch" % self.fetch_proxy_interval)
        #    self.fetch_new_proxyes()

    def set_proxy(self, request):
        """
        将request设置使用为当前的或下一个有效代理
        """
        proxy = self.proxyes[self.proxy_index]
        if not proxy["valid"]:
            self.inc_proxy_index()
            proxy = self.proxyes[self.proxy_index]

        if self.proxy_index == 0: # 每次不用代理直接下载时更新self.last_no_proxy_time
            self.last_no_proxy_time = datetime.now()

        if proxy["proxy"]:
            request.meta["proxy"] = proxy["proxy"]
        elif "proxy" in list(request.meta.keys()):
            del request.meta["proxy"]
        request.meta["proxy_index"] = self.proxy_index
        proxy["count"] += 1

    def invalid_proxy(self, index):
        """
        将index指向的proxy设置为invalid,
        并调整当前proxy_index到下一个有效代理的位置
        """
        if index < self.fixed_proxy: # 可信代理永远不会设为invalid
            logger.info("fixed proxy will not be invalid: %s" % self.proxyes[index])
            self.inc_proxy_index(index)
            return

        if self.proxyes[index]["valid"]:
            logger.info("invalidate %s" % self.proxyes[index])
            self.proxyes[index]["valid"] = False
            if index == self.proxy_index:
                self.inc_proxy_index()

            # if self.proxyes[index]["count"] < self.dump_count_threshold:
            #     self.dump_valid_proxy()

    def dump_valid_proxy(self):
        """
        保存代理列表中有效的代理到文件
        """
        if self.dump_count_threshold <= 0:
            return
        logger.info("dumping proxyes to file")
        with open(self.proxy_file, "w") as fd:
            for i in range(self.fixed_proxy, len(self.proxyes)):
                p = self.proxyes[i]
                if p["valid"] or p["count"] >= self.dump_count_threshold:
                    fd.write(p["proxy"]+"\n") # 只保存有效的代理


