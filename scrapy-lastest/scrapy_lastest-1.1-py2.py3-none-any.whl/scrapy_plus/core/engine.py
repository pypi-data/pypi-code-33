from demo_setup.scrapy_lastest.http.request import Request  # 导入Request对象
from demo_setup.scrapy_lastest.middlewares.spider_middlewares import SpiderMiddleware
from demo_setup.scrapy_lastest.middlewares.downloader_middlewares import DownloaderMiddleware

from .scheduler import Scheduler
from .downloader import Downloader
from .pipeline import Pipeline
from .spider import Spider


class Engine(object):
    """
    a. 对外提供整个的程序的入口
    b. 依次调用其他组件对外提供的接口，实现整个框架的运作(驱动)
    """


def __init__(self):
    self.spider = Spider()  # 接收爬虫对象
    self.scheduler = Scheduler()  # 初始化调度器对象
    self.downloader = Downloader()  # 初始化下载器对象
    self.pipeline = Pipeline()  # 初始化管道对象
    self.spider_mid = SpiderMiddleware()  # 初始化爬虫中间件对象
    self.downloader_mid = DownloaderMiddleware()  # 初始化下载器中间件对象


def start(self):
    """启动整个引擎"""
    self._start_engine()


def _start_engine(self):
    """依次调用其他组件对外提供的接口，实现整个框架的运作(驱动)"""
    # 1. 爬虫模块发出初始请求
    start_request = self.spider.start_requests()

    # 利用爬虫中间件预处理请求对象
    start_request = self.spider_mid.process_request(start_request)
    # 2. 把初始请求添加给调度器
    self.scheduler.add_request(start_request)
    # 3. 从调度器获取请求对象，交给下载器发起请求，获取一个响应对象
    request = self.scheduler.get_request()

    # 利用下载器中间件预处理请求对象
    request = self.downloader_mid.process_request(request)
    # 4. 利用下载器发起请求
    response = self.downloader.get_response(request)

    # 利用下载器中间件预处理响应对象
    response = self.downloader_mid.process_response(response)

    # 5. 利用爬虫的解析响应的方法，处理响应，得到结果
    result = self.spider.parse(response)
    # 6. 判断结果对象
    # 6.1 如果是请求对象，那么就再交给调度器
    if isinstance(result, Request):
        # 利用爬虫中间件预处理请求对象
        result = self.spider_mid.process_request(result)
        self.scheduler.add_request(result)
    # 6.2 否则，就交给管道处理
    else:
        self.pipeline.process_item(result)
