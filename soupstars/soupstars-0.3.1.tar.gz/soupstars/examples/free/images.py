from soupstars import HttpParser, parse, FilesystemCache


class FreeImagesParser(HttpParser):

    cache = FilesystemCache
    HOST = "https://www.pexels.com"
    ROUTE = "/photo/sunset-beach-ocean-panorama-68342/"

    @parse
    def title(soup):
        """
        >>> expected()
        'Body of Water Under Gray Clouds during Sunset'
        """
        return soup.find('h1').text

    @parse
    def url(soup):
        """
        >>> expected()
        'https://images.pexels.com/photos/68342/pexels-photo-68342.jpeg'
        """
        tag = soup.find('picture').find('img')
        src = tag['src']
        if '?' in src:
            src = src.split('?')[0]
        return src

    @parse
    def imgs(soup):
        """
        """

        imgs = soup.find_all('img')
        srcs = [t['src'] for t in imgs if '/photos/' in t['src']]
        return [s.split('?')[0] for s in srcs]

    @parse
    def id(soup):
        """
        >>> expected()
        68342
        """

        p = __class__.url(soup)
        return p.split('/')[-2]

    @parse
    def related(soup):
        results = []
        articles = soup.find_all('article')
        for art in articles:
            a = art.find('a')
            r = {'route': a.get('href')}
            results.append(r)
        return results
