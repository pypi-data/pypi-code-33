import random

from . import scrap


async def search(query: str, page=random.randint(0, 100)):
    results = scrap.search(query, p=page)
    images = []
    for i in range(scrap.IMAGES_PER_TAG):
        images.append(await results.__anext__())
    return images


async def image(image_id: str):
    images: dict = await scrap.image(image_id)
    return images


async def info(query: str):
    information = await scrap.info(query)
    return information


async def meta(query: str, page=random.randint(0, 10)):
    meta_tags = scrap.meta(query, p=page)
    results = []
    for i in range(scrap.TAGS_PER_META):
        results.append(await meta_tags.__anext__())
    return results
