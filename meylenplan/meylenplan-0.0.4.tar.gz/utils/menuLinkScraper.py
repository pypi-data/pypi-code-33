from bs4 import BeautifulSoup
from urllib.request import Request, urlopen

def get_menu_link():
    req = Request("http://schlemmermeyle.de/speisen/?restaurant=1")
    html_page = urlopen(req)

    soup = BeautifulSoup(html_page, "lxml")

    menu_link = []

    for link in soup.findAll('a'):
        if 'Tageskarte' in link.text:
            menu_link = link.get('href')

    return menu_link
