# __main__.py

from configparser import ConfigParser
from importlib import resources  # Python 3.7+
import sys

from reader import feed
from reader import viewer

def main():
    """Read the Real Python article feed"""
    # Read URL of the Real Python feed from config file
    cfg = ConfigParser()
    cfg.read_string(resources.read_text("reader", "config.txt"))
    url = cfg.get("feed", "url")

    # If an article ID is given, show the article
    if len(sys.argv) > 1:
        article = feed.get_article(url, sys.argv[1])
        viewer.show(article)

    # If no ID is given, show a list of all articles
    else:
        site = feed.get_site(url)
        titles = feed.get_titles(url)
        viewer.show_list(site, titles)

if __name__ == "__main__":
    main()
    