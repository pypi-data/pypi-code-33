
# coding: utf-8

import traceback
import json
import html

import requests
from bs4 import BeautifulSoup as bs

from search_engine.util import headers

import logging

def bing(keyword):
    start = 0

    stored = set()

    s = requests.Session()
    while True:
        next_url = "https://www4.bing.com/search?q=%s&first=%d&rdr=1" % (keyword, start)
        start += 10

        logging.info("search: %s" % next_url)

        try:
            r = s.get(next_url, headers=headers)
        except:
            logging.info("search_url: %s fail" % next_url)
            logging.info(traceback.format_exc())
            continue

        resp = r.text

        if resp.find(u"没有与此相关的结果:") > -1:
            logging.info("search fail(no result): %s" % next_url)
            break

        soup = bs(resp, "html.parser")
        items = soup.find_all("li", class_="b_algo")
        logging.info("item: %d" % len(items))

        repeat_count = 0
        for item in items:
            try:
                link = item.contents[0].find("a")["href"]

                if link in stored:
                    repeat_count += 1

                logging.info("link: %s" % link)
                stored.add(link)

                yield link
            except:
                logging.info("error in: %s" % str(item))
                logging.info(traceback.format_exc())
        if repeat_count == len(items):
            break

def bing_verified(keyword):
    for link in bing(keyword):
        try:
            r = requests.get(link)
            if r.text.find(keyword) > -1:
                yield link
        except:
            logging.info(traceback.format_exc())

if __name__ == "__main__":
    for link in bing('"@autonavi.com"'):
        print(link)
