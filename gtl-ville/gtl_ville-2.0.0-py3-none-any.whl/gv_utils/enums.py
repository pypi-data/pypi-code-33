#!/usr/bin/env python3

from enum import Enum, unique
from itertools import chain


class CsvData:
    samples = 'samples'
    timestamp = 'timestamp'

    confidence = 'confidence'
    flow = 'flow'
    occupancy = 'occupancy'
    speed = 'speed'
    status = 'status'
    traveltime = 'traveltime'


class DataTypeId:
    clusters = 'clusters'
    metropme = 'metropme'
    sections = 'sections'
    tomtomfcd = 'tomtomfcd'
    zones = 'zones'


class AttId:
    att = 'att'
    bear = 'bear'
    datatypeeid = 'datatypeeid'
    eid = 'eid'
    ffspeed = 'ffspeed'
    fow = 'fow'
    frc = 'frc'
    fromno = 'fromno'
    geom = 'geom'
    lat = 'lat'
    length = 'length'
    lon = 'lon'
    maxspeed = 'maxspeed'
    name = 'name'
    nol = 'nol'
    tono = 'tono'
    webatt = 'webatt'
    x = 'x'
    y = 'y'

    datapointeid = 'datapointeid'
    roadeid = 'roadeid'
    validfrom = 'validfrom'
    validto = 'validto'
    zoneeid = 'zoneeid'


class NetworkObjId:
    datapointsroadsmap = 'datapointsroadsmap'
    frcroadsmap = 'frcroadsmap'
    latlonnodesmatrix = 'latlonnodesmatrix'
    omiteddatapoints = 'omiteddatapoints'
