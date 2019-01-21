

import requests

from search_engine.baidu_search import baidu
from search_engine.bing_search import bing
from search_engine.google_search import google

def search(keyword):
    for link in baidu(keyword):
        yield link
    for link in bing(keyword):
        yield link
    for link in google(keyword):
        yield link

def search_as_list(keyword):
    links = set()
    for link in search(keyword):
        links.add(link)
    return list(links)

def search_callback(keyword, callback):
    for link in search(keyword):
        callback(link)
