import mimetypes
from enum import Enum
from logging import getLogger
from pathlib import Path
from time import sleep
from typing import Optional, TypeVar

import requests
from PIL import Image
from requests.utils import get_encodings_from_content
from selenium import webdriver

T = TypeVar("T")
logger = getLogger(__name__)


def default(value: Optional[T], default_value: T) -> T:
    return value if value is not None else default_value


class EpisodeField(Enum):
    title = "title"
    episode = "episode"
    aired = "aired"
    content_rating = "content_rating"
    summary = "summary"
    directors = "directors"
    writers = "writers"
    rating = "rating"


def load_page(url: str,
              use_selenium: bool = False,
              encoding: Optional[str] = None) -> str:
    if use_selenium:
        driver = webdriver.Firefox()
        driver.get(url)
        sleep(1)
        return driver.page_source

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/60.0.3112.113 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    if encoding is not None:
        response.encoding = encoding
    elif "charset" not in response.headers["content-type"]:
        encodings = get_encodings_from_content(response.text)
        if encodings:
            response.encoding = encodings[0]
        else:
            response.encoding = "utf-8"
    return response.text


def download_image(thumbnail: str, path: Path):
    """
    Download image to given path with given url.

    :param thumbnail: Image url to be downloaded
    :type thumbnail: str
    :param path: Image saving path
    :type path: Path
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/66.0.3359.170 Safari/537.36",
        "Connection": "close"
    }
    response = requests.get(thumbnail, stream=True, headers=headers)
    if response.status_code == 200:
        content_type = response.headers.get("content-type")
        ext = None
        if content_type is not None:
            ext = mimetypes.guess_extension(content_type)
            if ext in [".jpe", ".jpeg"]:
                ext = ".jpg"
        if ext is None:
            ext = ".png"
        thumbnail_path = path.with_suffix(ext)
        response.raw.decode_content = True
        try:
            image: Image = Image.open(response.raw)
            image.save(thumbnail_path)
        except IOError:
            logger.exception("Fail to save image\nThumbnail: %s\nPath: %s",
                             thumbnail, path)
    else:
        logger.error("Fail to load image (%d)", response.status_code)
