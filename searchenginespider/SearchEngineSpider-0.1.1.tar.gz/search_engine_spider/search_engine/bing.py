from .search_engine import SearchEngine, urlparse, parse_qs, quote_plus

from pyquery import PyQuery as pq
from bs4 import BeautifulSoup


class Bing(SearchEngine):
    def __init__(self):
        super(SearchEngine, self).__init__()
        self.URL = "https://{domain}/search?q={query}&first={start}"

    def content2items(self, content):
        soup = BeautifulSoup(content,"html.parser")
        results = soup.find(id="b_results")

        for li in results.children:
            if li.name != "li":
                continue
            h2 = li.find("h2")
            if not h2:
                continue
            url = li.a["href"]
            if not url.startswith("http://") and not url.startswith("https://"):
                continue
            title = h2.get_text()
            d = {
                "url": url,
                "title": title,
                'text': '',
            }
            yield d

    def get_name(self):
        return 'bing'

    def get_domain(self):
        return "www.bing.com"

    def get_url(self, query, **kwargs):
        query = quote_plus(query)
        start = kwargs.get("start", 1)
        domain = kwargs.get("domain", self.get_domain())
        url=self.URL.format(domain=domain, query=query, start=start)
        return url

    def filter_link(self, link):
        """
        Returns None if the link doesn't yield a valid result.
        Token from https://github.com/MarioVilas/google
        :return: a valid result
        """
        try:
            # Valid results are absolute URLs not pointing to a Google domain
            # like images.google.com or googleusercontent.com
            o = urlparse(link, 'http')
            if o.netloc:
                return link
            # Decode hidden URLs.
            if link.startswith('/url?'):
                link = parse_qs(o.query)['q'][0]
                # Valid results are absolute URLs not pointing to a Google domain
                # like images.google.com or googleusercontent.com
                o = urlparse(link, 'http')
                if o.netloc:
                    return link
        # Otherwise, or on error, return None.
        except Exception as e:
            raise e

LoadSearchEngine=Bing
