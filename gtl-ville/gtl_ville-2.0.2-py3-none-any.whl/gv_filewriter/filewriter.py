#!/usr/bin/env python3

import asyncio
import bz2
import functools
import os

import aiofiles
import gv_protobuf.data_pb2 as gv_pb_data
from gv_utils import datetime
from gv_utils.enums import DataStructure, Source

DATA_PATH_STRUCT = '%Y/%m/%d/%H-%M.pb.bz2'


async def async_write_cluster_data(basepath, clusterdata):
    basepath = os.path.join(basepath, Source.CLUSTERS.name)
    loop = asyncio.get_event_loop()
    pbdata, datatimestamp = await loop.run_in_executor(None,
                                                       functools.partial(__cluster_data_to_pb, clusterdata))
    await __async_write_pb_data(basepath, pbdata, datatimestamp)


async def async_write_tomtomfcd_data(basepath, cpdata):
    await async_write_cp_data(basepath, Source.TOMTOMFCD.name, cpdata)


async def async_write_metropme_data(basepath, cpdata):
    await async_write_cp_data(basepath, Source.METROPME.name, cpdata)


async def async_write_cp_data(basepath, sourcedir, cpdata):
    basepath = os.path.join(basepath, sourcedir)
    loop = asyncio.get_event_loop()
    pbdata, datatimestamp = await loop.run_in_executor(None,
                                                       functools.partial(__cp_data_to_pb, cpdata))
    await __async_write_pb_data(basepath, pbdata, datatimestamp)


async def async_write_section_data(basepath, sectiondata):
    basepath = os.path.join(basepath, Source.SECTIONS.name)
    loop = asyncio.get_event_loop()
    pbdata, datatimestamp = await loop.run_in_executor(None,
                                                       functools.partial(__section_data_to_pb, sectiondata))
    await __async_write_pb_data(basepath, pbdata, datatimestamp)


async def async_write_zone_data(basepath, zonedata):
    basepath = os.path.join(basepath, Source.ZONES.name)
    loop = asyncio.get_event_loop()
    pbdata, datatimestamp = await loop.run_in_executor(None,
                                                       functools.partial(__zone_data_to_pb, zonedata))
    await __async_write_pb_data(basepath, pbdata, datatimestamp)


def write_cluster_data(basepath, clusterdata):
    basepath = os.path.join(basepath, Source.CLUSTERS.name)
    __write_pb_data(basepath, *__cluster_data_to_pb(clusterdata))


def write_tomtomfcd_data(basepath, cpdata):
    write_cp_data(basepath, Source.TOMTOMFCD.name, cpdata)


def write_metropme_data(basepath, cpdata):
    write_cp_data(basepath, Source.METROPME.name, cpdata)


def write_cp_data(basepath, sourcedir, cpdata):
    basepath = os.path.join(basepath, sourcedir)
    __write_pb_data(basepath, *__cp_data_to_pb(cpdata))


def write_section_data(basepath, sectiondata):
    basepath = os.path.join(basepath, Source.SECTIONS.name)
    __write_pb_data(basepath, *__section_data_to_pb(sectiondata))


def write_zone_data(basepath, zonedata):
    basepath = os.path.join(basepath, Source.ZONES.name)
    __write_pb_data(basepath, *__zone_data_to_pb(zonedata))


async def __async_write_pb_data(basepath, pbdata, datatimestamp):
    loop = asyncio.get_event_loop()
    data = await loop.run_in_executor(None, pbdata.SerializeToString)
    await __async_write_bytes(__get_full_path(basepath, datetime.from_timestamp(datatimestamp, roundtominute=True)),
                              data)


def __write_pb_data(basepath, pbdata, datatimestamp):
    write_bytes(__get_full_path(basepath, datetime.from_timestamp(datatimestamp, roundtominute=True)),
                pbdata.SerializeToString())


def read_cluster_data(basepath, date):
    pbdata = gv_pb_data.ClusterData()
    pbdata.ParseFromString(__read_pb_data(basepath, Source.CLUSTERS.name, date))
    samples = []
    for pbsample in pbdata.sample:
        samples.append({
            DataStructure.CLUSTER.value: {
                DataStructure.SECTIONIDS.value: [],
                DataStructure.GEOM.value: pbsample.cluster.geom,
                DataStructure.ATT.value: dict()
            },
            DataStructure.DATA.value: dict([(str(metric), float(pbsample.data[metric])) for metric in pbsample.data])
        })
    return {
        DataStructure.DATATIMESTAMP.value: int(pbdata.timestamp.ToSeconds()),
        DataStructure.DATA.value: samples
    }


def read_tomtomfcd_data(basepath=None, date=None, fullpath=None):
    return read_cp_data(basepath, Source.TOMTOMFCD.name, date, fullpath)


def read_metropme_data(basepath, date):
    return read_cp_data(basepath, Source.METROPME.name, date)


def read_cp_data(basepath, sourcedir, date, fullpath=None):
    pbdata = gv_pb_data.CpData()
    pbdata.ParseFromString(__read_pb_data(basepath, sourcedir, date, fullpath))
    samples = []
    for pbsample in pbdata.sample:
        samples.append({
            DataStructure.CP.value: {
                DataStructure.EID.value: str(pbsample.cp.eid),
                DataStructure.GEOM.value: pbsample.cp.geom,
                DataStructure.ATT.value: dict(),
                DataStructure.SOURCE.value: {
                    DataStructure.NAME.value: str(pbsample.cp.sourcename)
                }
            },
            DataStructure.DATA.value: dict([(str(metric), float(pbsample.data[metric])) for metric in pbsample.data])
        })
    return {
        DataStructure.DATATIMESTAMP.value: int(pbdata.timestamp.ToSeconds()),
        DataStructure.DATA.value: samples
    }


def read_section_data(basepath, date):
    pbdata = gv_pb_data.SectionData()
    pbdata.ParseFromString(__read_pb_data(basepath, Source.SECTIONS.name, date))
    samples = []
    for pbsample in pbdata.sample:
        samples.append({
            DataStructure.SECTION.value: {
                DataStructure.EID.value: str(pbsample.section.eid),
                DataStructure.GEOM.value: pbsample.section.geom,
                DataStructure.ATT.value: dict()
            },
            DataStructure.DATA.value: dict([(str(metric), float(pbsample.data[metric])) for metric in pbsample.data])
        })
    return {
        DataStructure.DATATIMESTAMP.value: int(pbdata.timestamp.ToSeconds()),
        DataStructure.DATA.value: samples
    }


def read_zone_data(basepath, date):
    pbdata = gv_pb_data.ZoneData()
    pbdata.ParseFromString(__read_pb_data(basepath, Source.ZONES.name, date))
    samples = []
    for pbsample in pbdata.sample:
        samples.append({
            DataStructure.ZONE.value: {
                DataStructure.SECTIONIDS.value: [],
                DataStructure.GEOM.value: pbsample.zone.geom,
                DataStructure.ATT.value: dict()
            },
            DataStructure.DATA.value: dict([(str(metric), float(pbsample.data[metric])) for metric in pbsample.data])
        })
    return {
        DataStructure.DATATIMESTAMP.value: int(pbdata.timestamp.ToSeconds()),
        DataStructure.DATA.value: samples
    }


def __read_pb_data(basepath, sourcedir, date, fullpath=None):
    if fullpath is None:
        fullpath = __get_full_path(os.path.join(basepath, sourcedir), date, False)
    return read_bytes(fullpath)


def __cluster_data_to_pb(clusterdata):
    clustersamples, datatimestamp = __get_samples_timestamp(clusterdata)

    pbdata = gv_pb_data.ClusterData()

    for sample in clustersamples:
        pbsample = pbdata.sample.add()
        pbsample.cluster.geom = sample.get(DataStructure.CLUSTER.value, {}).get(DataStructure.GEOM.value)
        __add_sample_metrics(pbsample, sample.get(DataStructure.DATA.value, {}))

    pbdata.timestamp.FromSeconds(datatimestamp)
    return pbdata, datatimestamp


def __cp_data_to_pb(cpdata):
    cpsamples, datatimestamp = __get_samples_timestamp(cpdata)

    pbdata = gv_pb_data.CpData()

    for sample in cpsamples:
        pbsample = pbdata.sample.add()
        cp = sample.get(DataStructure.CP.value, {})
        pbsample.cp.eid = cp.get(DataStructure.EID.value)
        pbsample.cp.sourcename = cp.get(DataStructure.SOURCE.value, {}).get(DataStructure.NAME.value)
        pbsample.cp.geom = cp.get(DataStructure.GEOM.value)
        __add_sample_metrics(pbsample, sample.get(DataStructure.DATA.value, {}))

    pbdata.timestamp.FromSeconds(datatimestamp)
    return pbdata, datatimestamp


def __section_data_to_pb(sectiondata):
    sectionsamples, datatimestamp = __get_samples_timestamp(sectiondata)

    pbdata = gv_pb_data.SectionData()

    for sample in sectionsamples:
        pbsample = pbdata.sample.add()
        section = sample.get(DataStructure.SECTION.value, {})
        pbsample.section.eid = section.get(DataStructure.EID.value)
        pbsample.section.geom = section.get(DataStructure.GEOM.value)
        __add_sample_metrics(pbsample, sample.get(DataStructure.DATA.value, {}))

    pbdata.timestamp.FromSeconds(datatimestamp)
    return pbdata, datatimestamp


def __zone_data_to_pb(zonedata):
    zonesamples, datatimestamp = __get_samples_timestamp(zonedata)

    pbdata = gv_pb_data.ZoneData()

    for sample in zonesamples:
        pbsample = pbdata.sample.add()
        pbsample.zone.geom = sample.get(DataStructure.ZONE.value, {}).get(DataStructure.GEOM.value)
        __add_sample_metrics(pbsample, sample.get(DataStructure.DATA.value, {}))

    pbdata.timestamp.FromSeconds(datatimestamp)
    return pbdata, datatimestamp


def __get_samples_timestamp(dictdata):
    if type(dictdata) is not dict:
        return [], int(datetime.now(roundtominute=True).timestamp())

    datatimestamp = dictdata.get(DataStructure.DATATIMESTAMP.value, datetime.now(roundtominute=True).timestamp())
    samples = dictdata.get(DataStructure.DATA.value, [])
    if type(samples) is not list:
        samples = []
    return samples, int(datatimestamp)


def __add_sample_metrics(sample, metrics):
    for metric, value in metrics.items():
        sample.data[metric] = float(value)


def __get_full_path(basepath, date, makedirs=True):
    fullpath = os.path.join(basepath, date.strftime(DATA_PATH_STRUCT))
    if makedirs:
        directorypath = os.path.dirname(fullpath)
        if not os.path.exists(directorypath):
            os.makedirs(directorypath)
    return fullpath


async def async_write_graph(path, graphasyaml):
    await __async_write_bytes(path, graphasyaml)


def write_graph(path, graphasyaml):
    write_bytes(path, graphasyaml)


async def __async_write_bytes(path, bytesdata):
    loop = asyncio.get_event_loop()
    compressdata = await loop.run_in_executor(None, functools.partial(bz2.compress, bytesdata))
    async with aiofiles.open(path, 'wb') as file:
        await file.write(compressdata)


def write_bytes(path, bytesdata):
    with open(path, 'wb') as file:
        file.write(bz2.compress(bytesdata))


async def async_read_graph(path):
    return await __async_read_bytes(path)


def read_graph(path):
    return read_bytes(path)


async def __async_read_bytes(path):
    loop = asyncio.get_event_loop()
    async with aiofiles.open(path, 'rb') as file:
        compressdata = await file.read()
    return await loop.run_in_executor(None, functools.partial(bz2.decompress, compressdata))


def read_bytes(path):
    with open(path, 'rb') as file:
        return bz2.decompress(file.read())
