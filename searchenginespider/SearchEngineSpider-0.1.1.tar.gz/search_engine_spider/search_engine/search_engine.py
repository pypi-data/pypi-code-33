# -*- coding:utf-8 -*-

import os
import abc
import six
from pyquery import PyQuery as pq
from . import quote_plus, urlparse, parse_qs


SEARCH_ENGINE_DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

@six.add_metaclass(abc.ABCMeta)
class SearchEngine():
    def __init__(self):
        pass

    def init(self):
        self.temp_data_dir = os.path.join(os.path.dirname(__file__), "temp_data")
        if not os.path.exists(self.temp_data_dir):
            os.mkdir(self.temp_data_dir)

        basename = os.path.basename(self.get_domain_file)

    def pq_html(self, content):
        """
        Parsing HTML by pyquery
        :param content: HTML content
        :return:
        """
        return pq(content)

    def get_domain_file(self, dir_path=SEARCH_ENGINE_DATA_DIR):
        """
        return: domain_file
        可以在SEARCH_ENGINE_DATA_DIR下面放入{engine_name}.txt的文件，每一行是一个域名
        """
        domain_file = os.path.join(dir_path, self.get_name()) + ".txt"
        if os.path.exists(domain_file):
            return domain_file
        return ''

    def get_query(self, url):
        """
        从url逆推出query
        """
        u = urlparse(url)
        return parse_qs(u.query)["q"][0]

    @abc.abstractmethod
    def get_name(self):
        """
        return: 搜索引擎名字(string)
        """
        pass

    @abc.abstractmethod
    def get_domain(self):
        """
        return: 搜索引擎默认域名(string)
        """
        pass

    @abc.abstractmethod
    def get_url(self, query, **kargs):
        """
        功能: 根据参数构造url
        必须:
        query: 要查询的词条(string)
        domain: 指定domain(默认提供)
        可选:
        start: 起始词条索引(默认0)，不同搜索引擎会根据自身情况适当修改
        num: 要查询的结果个数(int)，google有效
        return: url(string)
        """
        pass

    @abc.abstractmethod
    def content2items(self, content):
        """
        功能: 解析html源码生成搜索结果构建的数组
        content: html源码(string)
        return: 搜索结果(list[{
            "title": "",
            "url": "",
            "text": ""
        }])
        """
        pass
