from typing import AsyncGenerator, List

import aiohttp
import bs4

TAGS_PER_META = 48
IMAGES_PER_TAG = 24
HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:64.0) '
                         'Gecko/20100101 Firefox/64.0'}


async def get(query, **kwargs) -> bs4.BeautifulSoup:
    kwargs = '?'.join([f'{k}={v}' for k, v in kwargs.items()])
    url = f'https://www.zerochan.net/{"+".join(query.split())}?{kwargs}'
    async with aiohttp.ClientSession(headers=HEADERS) as session:
        async with session.get(url) as response:
            return bs4.BeautifulSoup(await response.text(), features='lxml')


def get_list(soup, lid, error=ValueError) -> List[bs4.element.Tag]:
    try:
        sub = soup.find('ul', {'id': lid}).findAll('li')
    except AttributeError:
        raise error
    if not sub:
        raise StopAsyncIteration
    return sub


async def meta(query: str, p: int) -> AsyncGenerator[dict, None]:
    soup = await get(query, p=p)
    sub = get_list(soup, 'children', ValueError('Meta not found.'))
    c = 0
    for x in sub:
        c += 1
        submeta, count = x.span.text.rsplit(' ', 1)
        yield {'name': x.h3.a.text, 'meta': submeta,
               'count': int(count.replace(',', ''))}

    if c >= TAGS_PER_META:
        async for x in meta(query, p=p+1):
            yield x


async def search(query: str, p: int) -> AsyncGenerator[dict, None]:
    soup = await get(query, p=p)
    sub = get_list(soup, 'thumbs2', ValueError('Image not found.'))
    c = 0
    for x in sub:
        c += 1
        res, size = x.a.img['title'].split()
        yield {'id': x.a['href'][1:], 'thumb': x.a.img['src'],
               'res': res, 'size': size}

    if c >= IMAGES_PER_TAG:
        async for x in search(query, p=p+1):
            yield x


async def image(image_id: str) -> dict:
    soup = await get(image_id)
    tags = get_list(soup, 'tags', ValueError('Image not found.'))
    im = soup.find('a', {'class': 'preview'})['href']
    tags = [{'name': x.a.text, 'meta': x.text.replace(x.a.text, '', 1)[1:]}
            for x in tags]
    try:
        comments = [{'user': x.div.p.a.text, 'date': x.div.span.text,
                    'comment': x.findAll('div')[1].p.text}
                    for x in soup.find('div', {'id': 'posts'}).ul.findAll('li')
                    if x.div]
    except AttributeError:
        comments = []
    return {'url': im, 'tags': tags, 'comments': comments}


async def info(query: str) -> str:
    soup = await get(query)
    try:
        return soup.find('div', {'id': 'menu'}).findAll('p')[1].text
    except AttributeError:
        raise ValueError('Tag not Found')
