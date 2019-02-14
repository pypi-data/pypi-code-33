# coding=utf-8
from __future__ import print_function

import contextlib
import functools
import multiprocessing
from multiprocessing import Pool as ProcessPool
from multiprocessing import current_process as currentProcess
from multiprocessing.dummy import Pool as ThreadPool
from multiprocessing.dummy import current_process as currentThread

import tqdm

from suanpan import utils

WORKERS = multiprocessing.cpu_count()
DEFAULT_PBAR_FORMAT = "{desc}: {n_fmt}/{total_fmt} |{bar}"
DEFAULT_PBAR_CONFIG = {"bar_format": DEFAULT_PBAR_FORMAT}


@contextlib.contextmanager
def multiThread(workers=None):
    workers = workers or WORKERS
    pool = ThreadPool(processes=workers)
    yield pool
    pool.close()
    pool.join()


@contextlib.contextmanager
def multiProcess(workers=None):
    workers = workers or WORKERS
    pool = ProcessPool(processes=workers)
    yield pool
    pool.close()
    pool.join()


def parsePbarConfig(pbar):
    if pbar is True:
        return utils.merge({}, DEFAULT_PBAR_CONFIG, {"desc": "Processing"})
    elif isinstance(pbar, str):
        return utils.merge({}, DEFAULT_PBAR_CONFIG, {"desc": pbar})
    elif pbar in (False, None):
        return utils.merge({}, DEFAULT_PBAR_CONFIG, {"disable": True})
    elif isinstance(pbar, dict):
        return utils.merge({}, DEFAULT_PBAR_CONFIG, pbar)
    else:
        raise Exception("Invalid pbar config: bool | str | dict. but {}".format(pbar))


def pbarRunner(pbar, quantity=1):
    def _dec(runner):
        @functools.wraps(runner)
        def _runner(*args, **kwargs):
            result = runner(*args, **kwargs)
            pbar.update(quantity)
            return result

        return _runner

    return _dec


def _map(
    func, iterable, chunksize=None, workers=None, pbar=None, thread=False, mapFunc="map"
):
    items = list(iterable)
    pbarConfig = parsePbarConfig(pbar)
    pbarConfig.update(total=len(items))
    poolClass = multiThread if thread else multiProcess
    with poolClass(workers) as pool:
        with tqdm.tqdm(**pbarConfig) as pbar:
            run = pbarRunner(pbar)(func)
            mapFunc = getattr(pool, mapFunc)
            results = mapFunc(run, items, chunksize)
    return results


map = functools.partial(_map, mapFunc="map")
starmap = functools.partial(_map, mapFunc="starmap")
imap = functools.partial(_map, mapFunc="imap")
