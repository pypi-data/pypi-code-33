# coding=utf-8
from __future__ import print_function

import collections
import functools
import json

import cv2
import imageio
import numpy as np
import pandas as pd

from suanpan import asyncio, convert, path
from suanpan.log import logger


def loadFromCsv(filepath, **kwargs):
    kwargs.setdefault("index_col", 0)
    return pd.read_csv(filepath, **kwargs)


def saveAsCsv(filepath, data, **kwargs):
    path.safeMkdirsForFile(filepath)
    data.to_csv(filepath, **kwargs)
    return filepath


def loadFromNpy(filepath, **kwargs):
    kwargs.setdefault("encoding", "latin1")
    return np.load(filepath, **kwargs)


def saveAsNpy(filepath, data, **kwargs):
    path.safeMkdirsForFile(filepath)
    kwargs.setdefault("fix_imports", True)
    np.save(filepath, data, **kwargs)
    return filepath


def loadFromJson(filepath, **kwargs):
    encoding = kwargs.pop("encoding", "utf-8")
    with open(filepath, "r", encoding=encoding) as file:
        return json.load(file, **kwargs)


def saveAsJson(filepath, data, **kwargs):
    path.safeMkdirsForFile(filepath)
    encoding = kwargs.pop("encoding", "utf-8")
    with open(filepath, "w", encoding=encoding) as file:
        json.dump(data, file, **kwargs)
    return filepath


def saveImage(filepath, image):
    path.safeMkdirsForFile(filepath)
    cv2.imwrite(filepath, image)  # pylint: disable-msg=e1101
    return filepath


def saveAsFlatImage(filepath, data):
    image = convert.flatAsImage(data)
    return saveImage(filepath, image)


def saveAsAnimatedGif(filepath, data):
    image3D = convert.to3D(data)
    path.safeMkdirsForFile(filepath)
    imageio.mimsave(filepath, image3D)
    return filepath


def saveAsImage(filepath, data, flag=None):
    mapping = {None: saveImage, "flat": saveAsFlatImage, "animated": saveAsAnimatedGif}
    func = mapping.get(flag)
    if not func:
        raise Exception("Unknow flag: {}".format(flag))
    return func(filepath, data)


def saveAsImages(filepathPrefix, images, workers=None):
    counts = len(images)
    n = len(str(counts))
    workers = workers or min(counts, asyncio.WORKERS)
    with asyncio.multiThread(workers) as pool:
        for index, image in enumerate(images):
            pool.apply_async(
                saveAsImage,
                args=("{}_{}.png".format(filepathPrefix, str(index).zfill(n)), image),
            )
    return filepathPrefix


def saveAllAsImages(filepathPrefix, data, workers=None, pool=None):
    def _save(filepathPrefix, image3D, pool):
        layers = len(image3D)
        n = len(str(layers))
        for index, image in enumerate(image3D):
            pool.apply_async(
                saveImage,
                args=("{}_{}.png".format(filepathPrefix, str(index).zfill(n)), image),
            )
        pool.apply_async(
            saveAsFlatImage, args=("{}.png".format(filepathPrefix), image3D)
        )
        pool.apply_async(
            saveAsAnimatedGif, args=("{}.gif".format(filepathPrefix), image3D)
        )

    image3D = convert.to3D(data)
    if pool:
        _save(filepathPrefix, image3D, pool)
    else:
        layers = len(image3D)
        workers = workers or min(layers + 2, asyncio.WORKERS)
        with asyncio.multiThread(workers) as pool:
            _save(filepathPrefix, image3D, pool)
    return filepathPrefix


def merge(*dicts):
    def _merge(result, item):
        result.update(item)
        return result

    return functools.reduce(_merge, dicts, {})


def count(iterable):
    if hasattr(iterable, "__len__"):
        return len(iterable)

    d = collections.deque(enumerate(iterable, 1), maxlen=1)
    return d[0][0] if d else 0
