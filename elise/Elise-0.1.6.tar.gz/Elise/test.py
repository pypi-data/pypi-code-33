# encoding=utf-8
# date: 2018/11/28
__Author__ = "Masako"

from Elise.spider import Spider
from Elise.crawler import Crawler


class TestSpider(Spider):
    def __init__(self):
        Spider.__init__(self)

    def parse_detail(self, content):
        print(content)
        return content


class TestCrawler(Crawler):
    def __init__(self, spider):
        Crawler.__init__(self, spider)


spider = TestSpider()
spider.detail_url = 'https://www.baidu.com/'
spider.get_detail()

crawler = TestCrawler(spider)
crawler.start_page_list = ['get']
crawler.out_file = 'test.txt'
crawler.crawl_func = crawler.crawl
crawler.run()
