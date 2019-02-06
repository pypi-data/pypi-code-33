#!/usr/bin/env python3


from gv_utils import enums


ATT = enums.AttId.att
DATATYPEEID = enums.AttId.datatypeeid
EID = enums.AttId.eid
GEOM = enums.AttId.geom
WEBATT = enums.AttId.webatt

DATAPOINTEID = enums.AttId.datapointeid
ROADEID = enums.AttId.roadeid
VALIDFROM = enums.AttId.validfrom
VALIDTO = enums.AttId.validto
ZONEEID = enums.AttId.zoneeid


def from_db(self, dbrecord):
    obj = {}
    for k, v in dbrecord.items():
        if k in self.mapping:
            obj[self.mapping[k]] = v
    return obj


def to_db(self, obj):
    dbrecord = {}
    for k, v in obj.items():
        if k in self.invmapping:
            dbrecord[self.invmapping[k]] = v
    return dbrecord


class DataPoint:
    mapping = {
        'data_type_eid': DATATYPEEID,
        'eid': EID,
        'geom': GEOM
    }
    invmapping = {v: k for k, v in mapping.items()}


class Road:
    mapping = {
        'eid': EID,
        'geom': GEOM,
        'web_att': WEBATT,
        'att': ATT
    }
    invmapping = {v: k for k, v in mapping.items()}


class Zone:
    mapping = {
        'eid': EID,
        'geom': GEOM,
        'web_att': WEBATT,
        'att': ATT
    }
    invmapping = {v: k for k, v in mapping.items()}


class RoadDataPoint:
    mapping = {
        'road_eid': ROADEID,
        'data_point_eid': DATAPOINTEID,
        'valid_from': VALIDFROM,
        'valid_to': VALIDTO
    }
    invmapping = {v: k for k, v in mapping.items()}


class ZoneRoad:
    mapping = {
        'zone_eid': ZONEEID,
        'road_eid': ROADEID,
        'valid_from': VALIDFROM,
        'valid_to': VALIDTO
    }
    invmapping = {v: k for k, v in mapping.items()}
