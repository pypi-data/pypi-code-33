import time
from urllib.parse import urljoin

import requests
import dateparser
from pyatom import AtomFeed
from bs4 import BeautifulSoup


def get_striplist(circuit_breaker=5):
    if circuit_breaker <= 0:
        raise ValueError('Can\'t parse index page!')

    resp = requests.get('http://www.blastwave-comic.com')
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text)

    select_tags = soup.find_all('select', attrs={'name': 'nro'})
    if not select_tags:
        time.sleep(15)
        return get_striplist(circuit_breaker - 1)

    options = select_tags[0].find_all('option')

    episode_pairs = [
        (int(option['value']), option.text)
        for option in options
        if option.get('value', '').isdigit()
    ]

    return episode_pairs


def image_link_from_comic_number(comic_number):
    resp = requests.get('http://www.blastwave-comic.com/index.php?p=comic&nro=%d' % comic_number)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text)

    images = [
        img for img in soup.find_all("img")
        if 'comics/' in img.get('src', '')
    ]

    if not images:
        raise ValueError('No image found for comic number %d!' % comic_number)

    return urljoin('http://www.blastwave-comic.com', images[0]['src'])


def get_date_from_image(img_url):
    resp = requests.head(img_url)

    date_str = resp.headers['Last-Modified']

    return dateparser.parse(date_str)


def generate_atom_feed():
    striplist = sorted(get_striplist())

    last_five_strips = reversed(striplist[-5:])

    feed = AtomFeed(
        title="Gone with the Blastwave",
        subtitle="Unofficial feed for the GWTB comics.",
        feed_url="https://github.com/Bystroushaak/gwtb_atom_generator",
        url="http://www.blastwave-comic.com/",
        author="Bystroushaak"
    )

    for comic_id, title in last_five_strips:
        image_link = image_link_from_comic_number(comic_id)
        date = get_date_from_image(image_link)

        feed.add(
            title=title,
            # content="Body of my post",
            # content_type="text",
            author='GWTB',
            url='http://www.blastwave-comic.com/index.php?p=comic&nro=%d' % comic_id,
            updated=date
        )

    return feed.to_string()


def main():
    print(generate_atom_feed())
