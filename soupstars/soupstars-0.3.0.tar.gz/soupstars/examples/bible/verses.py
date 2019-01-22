from soupstars import HttpParser, parse, FilesystemCache


class BibleVersesParser(HttpParser):

    cache = FilesystemCache
    HOST = "http://topverses.com/Bible"
    ROUTE = "/&pg=1&a=ajax"

    @parse
    def sections(soup):
        return [t.text.strip() for t in soup.find_all('h2')]

    @parse
    def ranks(soup):
        rank_texts = [t.text.strip() for t in soup.find_all('h5')]
        rank_nums = [t.split()[-1] for t in rank_texts]
        return [int(t) for t in rank_nums]

    @parse
    def quotes(soup):
        containers = soup.find_all('div', attrs={'class': 'container'})
        sections = [c.find('div', attrs={'class': 'slide section'}) for c in containers]
        texts = [s.find('div').text.replace('NIV', '') for s in sections]
        clean_texts = [s.strip() for s in texts]
        return [str(c) for c in clean_texts]

    @parse
    def related(soup):
        return [{"route": "/&pg={n}&a=ajax".format(n=n)} for n in range(1,11)]
