# encoding=utf-8
# date: 2018/7/17
__Author__ = "Masako"

import json
import time
import codecs
import threading
from queue import Queue


class Crawler(object):
    """
    simple crawler
    input from file or start page
    save as json file
    """
    def __init__(self, spider):
        self.thd_num = 5
        self.file_type = 'json'
        self.start_page_list = [1]
        self.input_que = Queue()
        self.out_que = Queue()
        self.input_file = ''
        self.out_file = ''
        self.crawl_func = self.crawl  # must be rewrite
        self.spider = spider

    def input_from_file(self):
        with codecs.open(self.input_file, 'r', 'utf-8') as f:
            line = f.readline().strip()
            while line:
                if self.file_type == 'json':
                    data = json.loads(line)
                else:
                    data = line
                self.input_que.put(data)
                line = f.readline().strip()

    def save(self):
        while True:
            try:
                data = self.out_que.get(timeout=0.2)
                data_str = json.dumps(data, ensure_ascii=False)
            except Exception as e:
                # print(e)
                time.sleep(1)
                continue

            with codecs.open(self.out_file, 'a', 'utf-8') as r:
                r.write(data_str)
                r.write('\n')
            self.out_que.task_done()

    def crawl_list(self):
        while True:
            try:
                page = self.input_que.get(timeout=0.2)
            except Exception as e:
                time.sleep(1)
                continue

            result_data = self.spider.get_list(page)
            data = result_data.get('data', {})
            code = result_data.get('code')
            if code != 0:
                self.input_que.put(page)

            # deal next page
            data_list = data.get('list', [])
            for d in data_list:
                self.out_que.put(d)

            total_page = data.get('total_page', 0)
            if page < total_page:
                self.input_que.put(page + 1)

            self.input_que.task_done()
            time.sleep(1)

    def crawl(self):
        while True:
            try:
                params = self.input_que.get(timeout=0.2)
            except Exception as e:
                time.sleep(1)
                continue

            result_data = self.spider.get_detail(params)
            data = result_data.get('data', {})
            code = result_data.get('code')
            if code != 0:
                self.input_que.put(params)

            self.out_que.put(data)
            self.input_que.task_done()
            time.sleep(1)

    def run(self):
        if self.input_file:
            input_thd = threading.Thread(target=self.input_from_file, args=())
            input_thd.daemon = True
            input_thd.start()
            time.sleep(5)
        else:
            for page in self.start_page_list:
                self.input_que.put(page)

        for i in range(self.thd_num):
            crawl_thd = threading.Thread(target=self.crawl_func, args=())
            crawl_thd.daemon = True
            crawl_thd.start()

        output_thd = threading.Thread(target=self.save, args=())
        output_thd.daemon = True
        output_thd.start()

        self.input_que.join()
        self.out_que.join()
