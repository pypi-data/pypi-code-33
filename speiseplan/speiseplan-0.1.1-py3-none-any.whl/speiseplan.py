import urllib.parse
import subprocess
import platform
import json

try:
    from requests_html import HTMLSession
except ImportError:
    from pip._internal import main

    main(["install", "-q", "requests_html"])
    from requests_html import HTMLSession


session = HTMLSession()


def get_pct(url="https://www.die-karlotte.de/Cafeteria-PCT-Potsdam"):
    r = session.get(url)
    links = r.html.absolute_links
    pdf_link = next(x for x in links if ".pdf" in x)
    pdf_link = list(urllib.parse.urlparse(pdf_link))
    pdf_link[-1] = ""
    pdf_link[-2] = ""
    return urllib.parse.urlunparse(pdf_link)


def get_studentenwerk(
    url="https://www.studentenwerk-potsdam.de/essen/unsere-mensen-cafeterien",
    mensa_id=7,
):
    def is_my_mensa(link):
        query = urllib.parse.parse_qs(link.query)
        try:
            this_id = int(query["tx_ddfmensa_ddfmensa[mensa]"][0])
            return this_id == mensa_id
        except KeyError:
            return False

    r = session.get(url)
    links = map(urllib.parse.urlparse, r.html.absolute_links)
    mymensa = next(filter(is_my_mensa, links))
    return mymensa.geturl()


def main():
    open_cmd = "open" if platform.system() == "Darwin" else "xdg-open"

    for menu in [get_pct(), get_studentenwerk()]:
        subprocess.run([open_cmd, menu])


if __name__ == "__main__":
    main()
