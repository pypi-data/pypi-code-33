import six
from six.moves.urllib.request import urlretrieve

import os
import sys
import logging
import argparse
from hashlib import sha1
from gzip import GzipFile
from struct import unpack_from
import numpy as np


LABEL_MAGIC = 2049
IMAGE_MAGIC = 2051


def get_log_level(ll):
    return getattr(logging, ll.upper(), logging.ERROR)


logging.basicConfig(
    format="[MNIST] %(message)s",
    level=get_log_level(os.getenv('MNIST_LOG_LEVEL', 'INFO'))
)


class MNIST:
    URL=u"http://yann.lecun.com/exdb/mnist"
    TRAIN=u"{}/train-images-idx3-ubyte.gz".format(URL)
    TRAIN_LABELS=u"{}/train-labels-idx1-ubyte.gz".format(URL)
    TEST=u"{}/t10k-images-idx3-ubyte.gz".format(URL)
    TEST_LABELS=u"{}/t10k-labels-idx1-ubyte.gz".format(URL)


class FashionMNIST:
    URL=u"http://fashion-mnist.s3-website.eu-central-1.amazonaws.com"
    TRAIN=u"{}/train-images-idx2-ubyte.gz".format(URL)
    TRAIN_LABELS=u"{}/train-labels-idx1-ubyte.gz".format(URL)
    TEST=u"{}/t10k-images-idx3-ubyte.gz".format(URL)
    TEST_LABELS=u"{}/t10k-labels-idx1-ubyte.gz".format(URL)


def read_labels(data):
    """Read label data format explained here http://yann.lecun.com/exdb/mnist/"""
    magic, examples = unpack_from(">2i", data)
    assert magic == LABEL_MAGIC
    labels = unpack_from(">{}B".format(examples), data[8:])
    return np.frombuffer(data[8:], dtype=np.uint8).astype(np.int32)


def read_images(data):
    """Read image data format explained here http://yann.lecun.com/exdb/mnist/"""
    magic, number, rows, cols = unpack_from(">4i", data)
    assert magic == IMAGE_MAGIC
    images = np.frombuffer(data[16:], dtype=np.uint8).astype(np.float32)
    images = np.reshape(images, (number, rows, cols))
    return images


def get_cache_path(url, cache):
    """Get the path to the cache location for this url.

    :param url: `str` The url the file is coming from.
    :param cache: `str` The cache directory.

    :returns: `str` The path to the cache location.
    """
    if cache is None:
        return None
    if not os.path.exists(cache):
        os.makedirs(cache)
    url = url if six.PY2 else url.encode("utf-8")
    h = sha1(url).hexdigest()
    return os.path.join(cache, h)


def check_cache(cache_path):
    """Check if this file is in the cache.

    :param cache_path: `str` The file to check in the cache

    :returns: `bool` True if in the cache, False otherwise.
    """
    return False if cache_path is None else os.path.exists(cache_path)


def clear_cache(cache, url):
    """Remove an entry from the cache.

    :param cache: `str` The cache directory
    :param url: `str` The url the data was retrieved from
    """
    path = get_cache_path(url, cache)
    if check_cache(path):
        os.remove(path)


def get_data(url, cache=None):
    """Get data from the internet or cache.

    Note:
        If the file is downloaded and a cache is provided it is saved into the cache.

    :param url: `str` The url of the data
    :param cache: `str` The cache directory

    :returns: `bytes` The data requested
    """
    path = get_cache_path(url, cache)
    if not check_cache(path):
        logging.info("Downloading {}".format(url))
        path, _ = urlretrieve(url, path)
    else:
        logging.info("Found {} in cache.".format(url))
    with GzipFile(path) as f:
        return f.read()


def fetch_data(parse, url, cache):
    """Get data with error handling.

    Note:
        If there is an error when getting a file it makes sure the cache for
        that entry is removed. If the error is from a missing magic number it
        warns about that specifically.

    :param parse: `callable` The function to read the data.
    :param url: `str` The url to get the data from.
    :param cache: `str` The cache directory.

    :returns: `np.ndarray` The data
    """
    try:
        data = parse(get_data(url, cache))
    except Exception as e:
        try:
            raise e
        except AssertionError:
            logging.critical("Magic Number mismatch for {}".format(url))
        finally:
            clear_cache(cache, url)


def get_mnist(
        cache=None,
        train_url=MNIST.TRAIN,
        train_label_url=MNIST.TRAIN_LABELS,
        test_url=MNIST.TEST,
        test_label_url=MNIST.TEST_LABELS,
):
    """Download the original MNIST data."""
    x_train = fetch_data(read_images, train_url, cache)
    x_test = fetch_data(read_images, test_url, cache)
    y_train = fetch_data(read_labels, train_label_url, cache)
    y_test = fetch_data(read_labels, test_label_url, cache)
    return x_train, y_train, x_test, y_test


def get_fashion_mnist(
        cache=None,
        train_url=FashionMNIST.TRAIN,
        train_label_url=FashionMNIST.TRAIN_LABELS,
        test_url=FashionMNIST.TEST,
        test_label_url=FashionMNIST.TEST_LABELS,
):
    """Download the drop-in replacement `FashionMNIST` data."""
    return get_mnist(
        cache,
        train_url, train_label_url,
        test_url, test_label_url
    )


def main():
    parser = argparse.ArgumentParser(description="Download MNIST dataset")
    parser.add_argument(
        "--data", default="mnist",
        choices=["mnist", "fashion"],
        help="Which dataset to download."
    )
    parser.add_argument(
        "--cache", default="MNIST",
        help="Directory to save data in"
    )
    args = parser.parse_args()

    if args.data.lower() == "mnist":
        get_mnist(args.cache)
    else:
        get_fashion_mnist(args.cache)


if __name__ == "__main__":
    main()
