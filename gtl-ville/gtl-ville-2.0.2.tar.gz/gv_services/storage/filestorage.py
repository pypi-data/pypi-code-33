#!/usr/bin/env python3

import asyncio
import bz2
from concurrent.futures import ProcessPoolExecutor

from gv_utils import filesystem


DATA_FILE_STRUCT = '%H-%M.csv.bz2'


async def write_data(basepath, data, datatype, datadate):
    loop = asyncio.get_event_loop()
    with ProcessPoolExecutor() as pool:
        data = await loop.run_in_executor(pool, bz2.compress, *(data,))
    await filesystem.write_data(basepath, DATA_FILE_STRUCT, data, datatype, datadate)


async def get_data(basepath, datatype, datadate):
    loop = asyncio.get_event_loop()
    data = await filesystem.read_data(basepath, DATA_FILE_STRUCT, datatype, datadate)
    with ProcessPoolExecutor() as pool:
        data = await loop.run_in_executor(pool, bz2.decompress, *(data,))
    return data
