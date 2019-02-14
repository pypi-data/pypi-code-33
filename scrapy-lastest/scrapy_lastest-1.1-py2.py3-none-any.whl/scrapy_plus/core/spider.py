from demo_setup.scrapy_lastest.item import Item  # 导入Item对象
from demo_setup.scrapy_lastest.http.request import Request  # 导入Request对象


class Spider(object):
    """
    1. 构建请求信息(初始的)，也就是生成请求对象(Request)
    2. 解析响应对象，返回数据对象(Item)或者新的请求对象(Request)
    """

    start_url = 'http://www.baidu.com'  # 默认初始请求地址

    # 这里以请求百度首页为例

    def start_requests(self):
        """构建初始请求对象并返回"""
        return Request(self.start_url)

    def parse(self, response):
        """解析请求
        并返回新的请求对象、或者数据对象
        """
        return Item(response.body)  # 返回item对象
