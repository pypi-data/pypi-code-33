#!/usr/bin/env python3

import os

import aiofiles

from gv_utils import datetime


DATA_PATH_STRUCT = '%Y/%m/%d/'


async def write_data(basepath, datafilestruct, data, datatype, datadate):
    fullpath = os.path.join(_get_path(basepath, datatype, datadate), _get_file_name(datadate, datafilestruct))
    await _write_bytes(fullpath, data)
    return fullpath


async def read_data(basepath, datafilestruct, datatype, datadate):
    return await _read_bytes(_get_file_path(basepath, datafilestruct, datatype, datadate))


def _get_path(basepath, datatype, datadate):
    return mkdir_if_not_exist(os.path.join(basepath, _get_datatype_dir(datatype),
                                           datetime.to_string(datadate, DATA_PATH_STRUCT)))


def _get_file_name(datadate, datafilestruct):
    return datetime.to_string(datadate, datafilestruct)


def _get_datatype_dir(datatype):
    return datatype.upper()


def _get_file_path(basepath, datafilestruct, datatype, datadate):
    return os.path.join(basepath,
                        _get_datatype_dir(datatype),
                        datetime.to_string(datadate, DATA_PATH_STRUCT + datafilestruct))


async def _write_bytes(path, b):
    async with aiofiles.open(path, 'wb') as file:
        await file.write(b)


async def _read_bytes(path):
    async with aiofiles.open(path, 'rb') as file:
        b = await file.read()
    return b


def join_if_not_abs(root, path):
    if not os.path.isabs(path):
        path = os.path.join(root, path)
    return path


def mkdir_if_not_exist(path):
    if not os.path.exists(path):
        os.makedirs(path)
    return path
