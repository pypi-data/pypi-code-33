#!/usr/bin/env python3

import ujson

import gv_services.storage.dbstorage.dbmapping as dbmapping
from gv_utils import datetime, enums
import gv_utils.geometry as geometry


ATT = enums.AttId.att
DATAPOINTEID = enums.AttId.datapointeid
DATATYPEEID = enums.AttId.datatypeeid
EID = enums.AttId.eid
GEOM = enums.AttId.geom
ROADEID = enums.AttId.roadeid
VALIDFROM = enums.AttId.validfrom
WEBATT = enums.AttId.webatt
ZONEEID = enums.AttId.zoneeid


async def insert_data_type(dbpool, datatypes):
    await _run_copy_request(dbpool, 'data_type', [(dt,) for dt in datatypes], ('eid',))
    return datatypes


async def insert_data_point(dbpool, datapoints):
    query = 'INSERT INTO data_point (eid, data_type, geom) VALUES ' \
            '($1, (SELECT id FROM data_type WHERE data_type.eid=$2), $3);'
    await _run_executemany_request(dbpool, query, [(dp[EID], dp[DATATYPEEID], dp[GEOM]) for dp in datapoints],
                                   codecs=('geometry',))
    return datapoints


async def insert_road(dbpool, roads):
    await _run_copy_request(dbpool, 'road', [(rd[EID], rd[GEOM], rd.get(WEBATT), rd.get(ATT)) for rd in roads],
                            ('eid', 'geom', 'web_att', 'att'), codecs=('geometry', 'json'))
    return roads


async def insert_zone(dbpool, zones):
    await _run_copy_request(dbpool, 'zone', [(zn[EID], zn[GEOM], zn.get(WEBATT), zn.get(ATT)) for zn in zones],
                            ('eid', 'geom', 'web_att', 'att'), codecs=('geometry', 'json'))
    return zones


async def insert_road_data_point(dbpool, roaddatapoints):
    query = 'INSERT INTO road_data_point (road, data_point, valid_from) VALUES ' \
            '((SELECT id FROM road WHERE road.eid=$1), (SELECT id FROM data_point WHERE data_point.eid=$2), $3);'
    await _run_executemany_request(dbpool, query,
                                   [(rdp[ROADEID], rdp[DATAPOINTEID], rdp.get(VALIDFROM, datetime.now()))
                                    for rdp in roaddatapoints])
    return roaddatapoints


async def insert_zone_road(dbpool, zoneroads):
    query = 'INSERT INTO zone_road (zone, road, valid_from) VALUES ' \
            '((SELECT id FROM zone WHERE zone.eid=$1), (SELECT id FROM road WHERE road.eid=$2), $3);'
    await _run_executemany_request(dbpool, query,
                                   [(zr[ZONEEID], zr[ROADEID], zr.get(VALIDFROM, datetime.now())) for zr in zoneroads])
    return zoneroads


async def update_road(dbpool, roads, fields):
    await _run_executemany_request(dbpool, _build_update_query('road', fields), [v + [k, ] for k, v in roads.items()])


async def update_zone(dbpool, zones, fields):
    await _run_executemany_request(dbpool, _build_update_query('zone', fields), [v + [k, ] for k, v in zones.items()])


def _build_update_query(tablename, fields):
    setquery = ''
    i = 1
    for field in fields:
        setquery += field + ' = ' + '$' + str(i) + ', '
        i += 1
    setquery = setquery[:-2]
    return 'UPDATE '+ tablename + ' SET ' + setquery + ' WHERE eid = $' + str(i) + ';'


async def get_data_points(dbpool, eid=None, eids=None):
    query = 'SELECT data_point.*, data_type.eid AS data_type_eid ' \
            'FROM data_point INNER JOIN data_type ON data_point.data_type = data_type.id '
    wherequery, whereparams = _where_eids(eid, eids, 'data_point.eid')
    return _run_cursor_request(dbpool, query + wherequery, whereparams, dbmapping.DataPoint, codecs=('geometry',))


async def get_roads(dbpool, eid=None, eids=None):
    query = 'SELECT * FROM road '
    wherequery, whereparams = _where_eids(eid, eids)
    return _run_cursor_request(dbpool, query + wherequery, whereparams, dbmapping.Road, codecs=('geometry', 'json'))


async def get_zones(dbpool, eid=None, eids=None):
    query = 'SELECT * FROM zone '
    wherequery, whereparams = _where_eids(eid, eids)
    return _run_cursor_request(dbpool, query + wherequery, whereparams, dbmapping.Zone, codecs=('geometry', 'json'))


def _where_eids(eid, eids, fieldname='eid'):
    wherequery = ''
    whereparams = ()
    if eid is not None:
        wherequery = 'WHERE ' + fieldname + '=$1'
        whereparams = (eid,)
    if eids is not None:
        wherequery = 'WHERE ' + fieldname + '=any($1::varchar[])'
        whereparams = (eids,)
    return wherequery, whereparams


async def get_roads_data_points(dbpool, validfrom=None, validto=None, validat=None):
    query = 'SELECT road_data_point.*, road.eid AS road_eid, data_point.eid AS data_point_eid ' \
            'FROM road_data_point ' \
            'INNER JOIN road ON road_data_point.road = road.id ' \
            'INNER JOIN data_point ON road_data_point.data_point = data_point.id '
    wherequery, whereparams = _where_valid(validfrom, validto, validat)
    return _run_cursor_request(dbpool, query + wherequery, whereparams, dbmapping.RoadDataPoint)


async def get_zones_roads(dbpool, validfrom=None, validto=None, validat=None):
    query = 'SELECT zone_road.*, zone.eid AS zone_eid, road.eid AS road_eid ' \
            'FROM zone_road ' \
            'INNER JOIN zone ON zone_road.zone = zone.id ' \
            'INNER JOIN road ON zone_road.road = road.id '
    wherequery, whereparams = _where_valid(validfrom, validto, validat)
    return _run_cursor_request(dbpool, query + wherequery, whereparams, dbmapping.ZoneRoad)


def _where_valid(validfrom, validto, validat):
    wherequery = 'WHERE valid_to IS NULL'
    whereparams = ()
    if validfrom is not None:
        wherequery = 'WHERE valid_from=$1'
        whereparams = (validfrom,)
    if validto is not None:
        wherequery = 'WHERE valid_to=$1'
        whereparams = (validto,)
    if validat is not None:
        wherequery = 'WHERE valid_from>=$1 AND valid_to<$2'
        whereparams = validat, validat
    return wherequery, whereparams


async def _run_copy_request(dbpool, tablename, records, columns, codecs=()):
    async with dbpool.acquire() as conn:
        await _set_codecs(conn, codecs)
        async with conn.transaction():
            await conn.copy_records_to_table(tablename, records=records, columns=columns)


async def _run_executemany_request(dbpool, query, params, codecs=()):
    async with dbpool.acquire() as conn:
        await _set_codecs(conn, codecs)
        async with conn.transaction():
            await conn.executemany(query, params)


async def _run_cursor_request(dbpool, query, params, mappingtype, codecs=()):
    async with dbpool.acquire() as conn:
        await _set_codecs(conn, codecs)
        async with conn.transaction():
            async for record in conn.cursor(query, *params):
                yield dbmapping.from_db(mappingtype, record)


async def _set_codecs(conn, codecs):
    for codec in codecs:
        if codec == 'geometry':
            await _set_geom_codec(conn)
        elif codec == 'json':
            await _set_json_codec(conn)


async def _set_geom_codec(conn):
    await conn.set_type_codec(
        'geometry',
        encoder=geometry.encode_geometry,
        decoder=geometry.decode_geometry,
        format='binary',
    )


async def _set_json_codec(conn):
    await conn.set_type_codec(
        'jsonb',
        encoder=lambda value: b'\x01' + ujson.dumps(value).encode('utf-8'),
        decoder=lambda value: ujson.loads(value[1:].decode('utf-8')),
        schema='pg_catalog',
        format='binary'
    )
