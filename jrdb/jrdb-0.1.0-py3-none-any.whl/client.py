import requests
from lxml import html
from urllib.parse import urljoin


class JRDBClient():
    def __init__(self, auth):
        self.session = requests.Session()
        self.session.auth = auth

    def fetch_page(self, url):
        return self.session.get(url)

    def fetch_latest_urls(self):
        url = 'http://www.jrdb.com/member/data/'
        res = self.fetch_page(url)
        page = html.fromstring(res.content)
        urls = [urljoin(url, x) for x in page.xpath('//a/@href') if x.endswith('zip')]
        return urls
