
# coding: utf-8

import traceback
import json
import html

import requests
from bs4 import BeautifulSoup as bs

import logging

def baidu(keyword):
    next_url = "http://www.baidu.com/s?ie=utf-8&wd=%s" % keyword
    stop = False

    retry = 0
    while not stop:    
        logging.info("search: %s" % next_url)

        try:
            r = requests.get(next_url)
        except:
            logging.info(traceback.format_exc())
            retry += 1

            if retry > 10:
                break
            continue

        resp = r.text
        soup = bs(resp, "html.parser")

        items = soup.find_all("div", class_="f13")

        for item in items:
            if item["class"] != ["f13"]:
                continue
            try:
                link = item.contents[0]["href"]

                resp = requests.head(link)
                link = resp.headers["location"]

                logging.info("link: %s" % link)

                yield link
            except:
                logging.info("error in: %s" % str(item))
                logging.info(traceback.format_exc())

        try:
            foot = soup.find_all(id="page")[0]
            last_link = foot.find_all("a")[-1]

            if last_link.text.find(u"\u4e0b\u4e00\u9875") > -1:
                next_url = "http://www.baidu.com" + last_link["href"]
            else:
                logging.info("stop")
                stop = True
        except:
            logging.info("error in: %s" % str(foot))
            logging.info(traceback.format_exc())
            stop = True

def baidu_verified(keyword):
    for link in baidu(keyword):
        try:
            r = requests.get(link)
            if r.text.find(keyword) > -1:
                yield link
        except:
            logging.info(traceback.format_exc())

if __name__ == "__main__":
    for link in baidu_verified('myvyang'):
        print(link)
