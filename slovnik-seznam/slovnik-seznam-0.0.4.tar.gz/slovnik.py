#!/usr/bin/python3

import logging
import re
import sys
try:
    from urllib import urlencode
    from urllib2 import urlopen, URLError
except ImportError:
    from urllib.request import urlopen  # pylint: disable=E0611,F0401
    from urllib.parse import urlencode  # pylint: disable=E0611,F0401
    from urllib.error import URLError  # pylint: disable=E0611,F0401

import html2text
from bs4 import BeautifulSoup


def preview(word):
    baseUrl = "http://slovnik.seznam.cz/"
    fromLanguage = "cz"
    toLanguage = "en"
    out = ''

    if fromLanguage == toLanguage:
        return word
    else:
        query = urlencode({'q': word})
        url = baseUrl + "/%s-%s/word/?" % (fromLanguage, toLanguage) + query
        try:
            inf = urlopen(url)
        except URLError:
            logging.error('url %s cannot be opened', url)
        else:
            result = inf.read()
            inf.close()
            bs = BeautifulSoup(result, 'lxml')
            our_div = bs.find(id='fastTrans')
            if our_div is not None:
                for br in our_div.find_all('br'):
                    br.replace_with('$#$#$#')
                out = html2text.HTML2Text().handle(our_div.get_text())
                out = out.replace('\n', ' ').replace(' , ', ', ')
                out = re.sub(r'\s*\$#\$#\$#\s*', '\n', out)
                out = re.sub(r'var sklikData = {[^}]+};', '', out).strip()
                out = re.sub(r'sssp.getAds\({[^}]+}\);', '', out).strip()
            return out


def main():
    strout = '\n' + preview(' '.join(sys.argv[1:]))
    print(strout)


if __name__ == "__main__":
    main()
