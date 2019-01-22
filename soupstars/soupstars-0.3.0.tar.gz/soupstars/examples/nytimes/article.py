from soupstars import HttpParser, parse


class NytimesArticleParser(HttpParser):

    HOST = "http://www.nytimes.com"
    ROUTE = "/2019/01/07/us/politics/trump-address-border-visit.html"

    @parse
    def title(soup):
        """
        >>> expected()
        'Trump Will Make Broad-Based Public Appeal for Border Wall'
        """

        return soup.find('h1').text.replace("\"", "")

    @parse
    def authors(soup):
        """
        >>> expected()
        'By Michael Tackett and Nicholas Fandos'
        """

        return soup.find("p", attrs={"itemprop": "author creator"}).text.replace("\"", "")

    @parse
    def published_at(soup):
        """
        >>> expected()
        'Jan. 7, 2019'
        """

        return soup.find("time").text.replace("\"", "")
