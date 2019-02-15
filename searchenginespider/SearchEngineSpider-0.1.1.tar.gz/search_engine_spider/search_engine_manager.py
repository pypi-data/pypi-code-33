# -*- coding:utf-8 -*-

import os
import json
import random
import importlib
import itertools

from .config import DATA_DIR
from .config import file2list
from .config import SEARCH_ENGINE_SPIDER_DIR
from .search_engine import quote_plus, urlparse, parse_qs


class SearchEngineManager(object):
    def __init__(self):
        self.user_agents_file = os.path.join(DATA_DIR, "user_agents.txt")
        self.user_agents = file2list(self.user_agents_file)
        self.search_engine_dir_name = "search_engine"
        self.search_engine_dir = os.path.join(SEARCH_ENGINE_SPIDER_DIR,
                                              self.search_engine_dir_name)
        self.search_engine_dict = dict()
        self.load_search_engine()

    def load_search_engine(self):
        for file_name in os.listdir(self.search_engine_dir):
            module_name, ext = os.path.splitext(file_name)
            if ext != ".py" or not module_name:
                continue
            module = importlib.import_module(".".join((os.path.basename(SEARCH_ENGINE_SPIDER_DIR),
                    self.search_engine_dir_name, module_name)))
            search_engine_class = vars(module).get('LoadSearchEngine')
            if search_engine_class:
                search_engine = search_engine_class()
                self.search_engine_dict[search_engine.get_name()] = search_engine

    def random_user_agent(self):
        return random.choice(self.user_agents)

    def get_search_engine(self, name):
        return self.search_engine_dict.get(name)

    def must_get_search_engine(self, name):
        search_engine = self.get_search_engine(name)
        if search_engine:
            return search_engine
        print("没有该搜索引擎: " + name)
        exit(1)

    def print_search_engine(self):
        for search_engine_name in self.search_engine_dict:
            print(search_engine_name)

    def product_urls(self, engine_name, *url_file_list):
        assert len(url_file_list) >= 1
        search_engine = self.must_get_search_engine(engine_name)
        for words in itertools.product(*map(file2list, url_file_list)):
            query_word = " ".join(words)
            print(search_engine.get_url(query_word))

    def extract_text(self, search_engine, content, max_num, first_word=None, end_word=None):
        results = list()
        for index, item in enumerate(search_engine.content2items(content)):
            if index >= max_num:
                continue
            results.append(list(filter(None, (first_word, item['url'], index+1, end_word))))
        return results

    def extract_html(self, search_engine, html_path, max_num):
        with open(html_path) as f:
            return self.extract_text(search_engine, f.read(), max_num)

    def extract_json(self, search_engine, json_path, max_num):
        with open(json_path) as f:
            j = json.loads(f.read())
            url = j["url"]
            content = j["content"]
            query = search_engine.get_query(url)
            return self.extract_text(search_engine, content, max_num, first_word=query)

    def print_extract_html(self, engine_name, html_path, max_num=10000):
        max_num = int(max_num)
        search_engine = self.must_get_search_engine(engine_name)
        if os.path.isdir(html_path):
            for html_file in os.listdir(html_path):
                html_file = os.path.join(html_path, html_file)
                self.print_extract_html(engine_name, html_file, max_num)
        else:
            for item in self.extract_html(search_engine, html_path, max_num):
                print("\t".join(map(str, item)))

    def print_extract_json(self, engine_name, json_path, max_num=10000):
        max_num = int(max_num)
        search_engine = self.must_get_search_engine(engine_name)
        if os.path.isdir(json_path):
            for json_file in os.listdir(json_path):
                json_file = os.path.join(json_path, json_file)
                self.print_extract_json(engine_name, json_file, max_num)
        else:
            for item in self.extract_json(search_engine, json_path, max_num):
                print("\t".join(map(str, item)))

    def recovery_rate(self, local_site_file, json_result_file, max_num=10000):
        local_site_set = set()
        with open(local_site_file) as f:
            for line in f:
                local_site_set.add(line)
        search_site_dict = dict()
        with open(json_result_file) as f:
            for line in f:
                query, url, index = line.split("\t")
                if index > max_num:
                    continue
                parsed = urlparse(url)
                hostname = parsed.hostname
                search_site_dict[hostname] = search_site_dict.get(hostname, 0) + 1
        results = list()
        for site, times in search_site_dict.items:
            in_local = int(site in local_site_set)
            results.append([site, times, in_local])
        results.sort(key=lambda x:x[1], reverse=True)
        for result in results:
            print(" ".join(map(str, result)))
