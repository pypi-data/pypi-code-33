#!/usr/bin/env python3

from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
import os
import re
import traceback

import psycopg2.extras as psycopg2_extra
from psycopg2.pool import ThreadedConnectionPool

from gv_utils.enums import DataStructure
from gv_utils import datetime


class CustomJson(psycopg2_extra.Json):

    def __init__(self, adapted):
        super().__init__(adapted)

    def dumps(self, obj):
        return super().dumps(self.__replace_int_float_by_string(obj))

    @staticmethod
    def __replace_int_float_by_string(obj):
        if isinstance(obj, int):
            return str(obj)
        if isinstance(obj, float):
            return str(obj)
        if isinstance(obj, (list, tuple)):
            return [CustomJson.__replace_int_float_by_string(item) for item in obj]
        if isinstance(obj, dict):
            return {
                CustomJson.__replace_int_float_by_string(key):
                    CustomJson.__replace_int_float_by_string(value) for key, value in obj.items()
            }
        return obj


class DBWriter:

    def __init__(self, dbhost, dbport, dbuser, dbpass, dbname, logger):
        self.logger = logger
        self.dbpool = ThreadedConnectionPool(5, 50,
                                             dbname=dbname, user=dbuser, password=dbpass, host=dbhost, port=dbport)
        self.sourcemap = {}
        self.cpmap = {}
        self.sectionmap = {}
        self.zonemap = {}

    def close(self):
        self.dbpool.closeall()

    @contextmanager
    def transaction(self, name='transaction'):
        conn = self.dbpool.getconn()
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            self.logger.error("{} error: {}".format(name, e))
        finally:
            conn.reset()
            self.dbpool.putconn(conn)

    def add_sections_cps(self, sectionscps):
        if type(sectionscps) is not dict:
            self.logger.error('type(sectionscps) is not dict')
            self.logger.error(traceback.format_exc())
            return 0

        sections = sectionscps.get(DataStructure.SECTIONS.value, [])
        validfrom = sectionscps.get(DataStructure.VALIDFROM.value, datetime.now(roundtominute=True))
        self.__fast_insert(lambda sectioncps: self.__add_section_cps(sectioncps, validfrom), sections,
                           """INSERT INTO section_cp (section_id, cp_id, valid_from) VALUES %s ON CONFLICT DO NOTHING;""",
                           flat=True)

    def add_zones_sections(self, zonessections):
        if type(zonessections) is not dict:
            self.logger.error('type(zonessections) is not dict')
            self.logger.error(traceback.format_exc())
            return 0

        zones = zonessections.get(DataStructure.ZONES.value, [])
        validfrom = zonessections.get(DataStructure.VALIDFROM.value, datetime.now(roundtominute=True))
        self.__fast_insert(lambda zonesections: self.__add_zone_sections(zonesections, validfrom), zones,
                           """INSERT INTO zone_section (zone_id, section_id, valid_from) VALUES %s ON CONFLICT DO NOTHING;""",
                           flat=True)

    def add_cp_data(self, cpdata):
        if type(cpdata) is not dict:
            self.logger.error('type(cpdata) is not dict')
            self.logger.error(traceback.format_exc())
            return 0

        data = cpdata.get(DataStructure.DATA.value, [])
        datatimestamp = cpdata.get(DataStructure.DATATIMESTAMP.value, datetime.now(roundtominute=True).timestamp())
        datadatetime = datetime.from_timestamp(datatimestamp)
        self.__fast_insert(lambda sample: self.__add_cp_sample(sample, datadatetime), data,
                           """INSERT INTO cp_data (cp_id, data_timestamp, data) VALUES %s;""")

    def add_cluster_data(self, clusterdata):
        if type(clusterdata) is not dict:
            self.logger.error('type(clusterdata) is not dict')
            self.logger.error(traceback.format_exc())
            return 0

        data = clusterdata.get(DataStructure.DATA.value, [])
        datatimestamp = clusterdata.get(DataStructure.DATATIMESTAMP.value, datetime.now(roundtominute=True).timestamp())
        datadatetime = datetime.from_timestamp(datatimestamp)
        self.__fast_insert(lambda sample: self.__add_cluster_sample(sample, datadatetime), data,
                           """INSERT INTO cluster_data (section_ids, geom, data_timestamp, data) VALUES %s;""")

    def __fast_insert(self, func, data, sqlcommand, flat=False):
        cpu = os.cpu_count()
        with ThreadPoolExecutor(cpu) as executor:
            sqlvalues = executor.map(func, data)
        if flat:
            sqlvalues = [sqlvalue for sqlsubvalues in sqlvalues for sqlvalue in sqlsubvalues]
        with self.transaction('_fast_insert') as conn:
            with conn.cursor() as cur:
                    psycopg2_extra.execute_values(cur, sqlcommand, filter(None, sqlvalues))

    # DB METHODS
    def __add_cp(self, cp):
        cpeid = cp.get(DataStructure.EID.value)
        cpid = None
        if cpeid is not None:
            with self.transaction('__add_cp') as conn:
                with conn.cursor() as cur:
                    sourcename = cp.get(DataStructure.SOURCE.value, {}).get(DataStructure.NAME.value)
                    if sourcename is not None:
                        sourceid = self.sourcemap.get(sourcename) if sourcename in self.sourcemap \
                            else self.__insert_source(cur, sourcename)
                        if sourceid is not None:
                            cpmap = self.cpmap.get(sourceid, {})
                            cpid = cpmap.get(cpeid) if cpeid in cpmap else self.__insert_cp(cur, cpeid, sourceid)
                            if cpid is not None:
                                cpgeom = cp.get(DataStructure.GEOM.value)
                                if bool(cpgeom):
                                    self.__insert_cp_geom(cur, cpid, cpgeom)
                                cpatt = cp.get(DataStructure.ATT.value)
                                if bool(cpatt):
                                    self.__insert_cp_att(cur, cpid, cpatt)
        return cpid

    def __add_section(self, section):
        sectioneid = section.get(DataStructure.EID.value)
        sectionid = None
        if sectioneid is not None:
            with self.transaction('__add_section') as conn:
                with conn.cursor() as cur:
                    sectioneid = re.sub("['\s+]", "", str(sectioneid))
                    sectionid = self.sectionmap.get(sectioneid) if sectioneid in self.sectionmap \
                        else self.__insert_section(cur, sectioneid)
                    if sectionid is not None:
                        sectiongeom = section.get(DataStructure.GEOM.value)
                        if sectiongeom is not None:
                            self.__instert_section_geom(cur, sectionid, sectiongeom)
                        sectionatt = section.get(DataStructure.ATT.value)
                        if bool(sectionatt):
                            self.__insert_section_att(cur, sectionid, sectionatt)
        return sectionid

    def __add_section_cps(self, sectioncps, validfrom):
        section = sectioncps.get(DataStructure.SECTION.value, {})
        sectioneid = section.get(DataStructure.EID.value)
        sqlsubvalues = []
        if sectioneid is not None:
            sectioneid = re.sub("['\s+]", "", str(sectioneid))
            sectionid = self.sectionmap.get(sectioneid) if sectioneid in self.sectionmap \
                else self.__add_section(section)
            if sectionid is not None:
                with self.transaction('__add_section_cps') as conn:
                    with conn.cursor() as cur:
                        for sourcename, cpeids in sectioncps.get(DataStructure.CPIDS.value, {}).items():
                            sourceid = self.sourcemap.get(sourcename) if sourcename in self.sourcemap \
                                else self.__get_source_id(cur, sourcename)
                            if sourceid is not None:
                                cpmap = self.cpmap.get(sourceid, {})
                                for cpeid in cpeids:
                                    cpid = cpmap.get(cpeid) if cpeid in cpmap else self.__get_cp_id(cur, sourceid,
                                                                                                    cpeid)
                                    if cpid is not None:
                                        sqlsubvalues.append((sectionid, cpid, validfrom))
        return sqlsubvalues

    def __add_zone(self, zone):
        zoneeid = zone.get(DataStructure.EID.value)
        zoneid = None
        if zoneeid is not None:
            with self.transaction('__add_zone') as conn:
                with conn.cursor() as cur:
                    zonemap = self.zonemap
                    zoneid = zonemap.get(zoneeid) if zoneeid in zonemap else self.__insert_zone(cur, zoneeid)
                    if zoneid is not None:
                        zonegeom = zone.get(DataStructure.GEOM.value)
                        if zonegeom is not None:
                            self.__instert_zone_geom(cur, zoneid, zonegeom)
                        zoneatt = zone.get(DataStructure.ATT.value)
                        if bool(zoneatt):
                            self.__insert_zone_att(cur, zoneid, zoneatt)
        return zoneid

    def __add_zone_sections(self, zonesections, validfrom):
        zone = zonesections.get(DataStructure.ZONE.value, {})
        zoneeid = zone.get(DataStructure.EID.value)
        if zoneeid is not None:
            zonemap = self.zonemap
            zoneid = zonemap.get(zoneeid) if zoneeid in zonemap else self.__add_zone(zone)
            if zoneid is not None:
                sqlsubvalues = []
                for sectioneid in zonesections.get(DataStructure.SECTIONIDS.value, []):
                    sectioneid = re.sub("['\s+]", "", str(sectioneid))
                    sectionid = self.sectionmap.get(sectioneid)
                    if sectionid is not None:
                        sqlsubvalues.append((zoneid, sectionid, validfrom))
                if bool(sqlsubvalues):
                    return sqlsubvalues
        return []

    def __add_cp_sample(self, cpsample, datadatetime):
        data = cpsample.get(DataStructure.DATA.value)
        if bool(data):
            cp = cpsample.get(DataStructure.CP.value, {})
            cpeid = cp.get(DataStructure.EID.value)
            if cpeid is not None:
                sourcename = cp.get(DataStructure.SOURCE.value, {}).get(DataStructure.NAME.value)
                cpmap = self.cpmap.get(self.sourcemap.get(sourcename), {})
                cpid = cpmap.get(cpeid) if cpeid in cpmap else self.__add_cp(cp)
                if cpid is not None:
                    return cpid, datadatetime, CustomJson(data)

    def __add_cluster_sample(self, clustersample, datadatetime):
        data = clustersample.get(DataStructure.DATA.value)
        if bool(data):
            cluster = clustersample.get(DataStructure.CLUSTER.value, [])
            sectioneids = cluster.get(DataStructure.SECTIONIDS.value, [])
            if bool(sectioneids):
                sectionids = []
                for sectioneid in sectioneids:
                    sectionid = self.sectionmap.get(sectioneid)
                    if sectionid is not None:
                        sectionids.append(sectionid)
                if bool(sectionids):
                    return (sectionids, self.__add_srid(cluster.get(DataStructure.GEOM.value)), datadatetime,
                            CustomJson(data))

    def __insert_source(self, cur, sourcename):
        sql = """INSERT INTO source (name) VALUES (%s) ON CONFLICT (name) DO UPDATE SET name=EXCLUDED.name RETURNING id;"""
        sourceid = None
        try:
            cur.execute(sql, (sourcename, ))
            sourceid = cur.fetchone()[0]
        except (TypeError, IndexError):
            pass
        except:
            self.logger.error('Error while persisting source')
            self.logger.error(traceback.format_exc())
        if sourceid is not None:
            self.__add_source_id(sourcename, sourceid)
        return sourceid

    def __get_source_id(self, cur, sourcename):
        sql = """SELECT id FROM source WHERE name = %s;"""
        sourceid = None
        try:
            cur.execute(sql, (sourcename,))
            sourceid = cur.fetchone()[0]
        except (TypeError, IndexError):
            pass
        except:
            self.logger.error('Error while retriving source')
            self.logger.error(traceback.format_exc())
        if sourceid is not None:
            self.__add_source_id(sourcename, sourceid)
        return sourceid

    def __add_source_id(self, sourcename, sourceid):
        self.sourcemap[sourcename] = sourceid

    def __insert_cp(self, cur, cpeid, sourceid):
        sql = """INSERT INTO collection_point (eid, source_id) VALUES (%s, %s) ON CONFLICT (eid, source_id) DO UPDATE SET eid=EXCLUDED.eid RETURNING id;"""
        cpid = None
        try:
            cur.execute(sql, (cpeid, sourceid))
            cpid = cur.fetchone()[0]
        except (TypeError, IndexError):
            pass
        except:
            self.logger.error('Error while persisting cp')
            self.logger.error(traceback.format_exc())
        if cpid is not None:
            self.__add_cp_id(sourceid, cpeid, cpid)
        return cpid

    def __get_cp_id(self, cur, sourceid, cpeid):
        sql = """SELECT id FROM collection_point WHERE source_id = %s AND eid = %s;"""
        cpid = None
        try:
            cur.execute(sql, (sourceid, cpeid))
            cpid = cur.fetchone()[0]
        except (TypeError, IndexError):
            pass
        except:
            self.logger.error('Error while retriving cp')
            self.logger.error(traceback.format_exc())
        if cpid is not None:
            self.__add_cp_id(sourceid, cpeid, cpid)
        return cpid

    def __add_cp_id(self, sourceid, cpeid, cpid):
        if sourceid in self.cpmap:
            self.cpmap[sourceid][cpeid] = cpid
        else:
            self.cpmap[sourceid] = {cpeid: cpid}

    def __insert_cp_geom(self, cur, cpid, cpgeom):
        sql = """INSERT INTO cp_geom (cp_id, geom) VALUES (%s, %s) ON CONFLICT DO NOTHING;"""
        try:
            cur.execute(sql, (cpid, self.__add_srid(cpgeom)))
        except:
            self.logger.error('Error while persisting cp geom')
            self.logger.error(traceback.format_exc())

    def __insert_cp_att(self, cur, cpid, cpatt):
        sql = """INSERT INTO cp_att (cp_id, att) VALUES (%s, %s) ON CONFLICT DO NOTHING;"""
        try:
            cur.execute(sql, (cpid, CustomJson(cpatt)))
        except:
            self.logger.error('Error while persisting cp att')
            self.logger.error(traceback.format_exc())

    def __insert_section(self, cur, sectioneid):
        sql = """INSERT INTO section (eid) VALUES (%s) ON CONFLICT (eid) DO UPDATE SET eid=EXCLUDED.eid RETURNING id;"""
        sectionid = None
        try:
            cur.execute(sql, (sectioneid, ))
            sectionid = cur.fetchone()[0]
        except (TypeError, IndexError):
            pass
        except:
            self.logger.error('Error while persisting section')
            self.logger.error(traceback.format_exc())
        if sectionid is not None:
            self.sectionmap[sectioneid] = sectionid
        return sectionid

    def __instert_section_geom(self, cur, sectionid, sectiongeom):
        sql = """INSERT INTO section_geom (section_id, geom) VALUES (%s, %s) ON CONFLICT DO NOTHING;"""
        try:
            cur.execute(sql, (sectionid, self.__add_srid(sectiongeom)))
        except:
            self.logger.error('Error while persisting section geom')
            self.logger.error(traceback.format_exc())

    def __insert_section_att(self, cur, sectionid, sectionatt):
        sql = """INSERT INTO section_att (section_id, att) VALUES (%s, %s) ON CONFLICT DO NOTHING;"""
        try:
            cur.execute(sql, (sectionid, CustomJson(sectionatt)))
        except:
            self.logger.error('Error while persisting section att')
            self.logger.error(traceback.format_exc())

    def __insert_zone(self, cur, zoneeid):
        sql = """INSERT INTO zone (eid) VALUES (%s) ON CONFLICT (eid) DO UPDATE SET eid=EXCLUDED.eid RETURNING id;"""
        zoneid = None
        try:
            cur.execute(sql, (zoneeid,))
            zoneid = cur.fetchone()[0]
        except (TypeError, IndexError):
            pass
        except:
            self.logger.error('Error while persisting zone')
            self.logger.error(traceback.format_exc())
        if zoneid is not None:
            self.zonemap[zoneeid] = zoneid
        return zoneid

    def __instert_zone_geom(self, cur, zoneid, zonegeom):
        sql = """INSERT INTO zone_geom (zone_id, geom) VALUES (%s, %s) ON CONFLICT DO NOTHING;"""
        try:
            cur.execute(sql, (zoneid, self.__add_srid(zonegeom)))
        except:
            self.logger.error('Error while persisting zone geom')
            self.logger.error(traceback.format_exc())

    def __insert_zone_att(self, cur, zoneid, zoneatt):
        sql = """INSERT INTO zone_att (zone_id, att) VALUES (%s, %s) ON CONFLICT DO NOTHING;"""
        try:
            cur.execute(sql, (zoneid, CustomJson(zoneatt)))
        except:
            self.logger.error('Error while persisting zone att')
            self.logger.error(traceback.format_exc())

    @staticmethod
    def __add_srid(wkt):
        if 'SRID' not in wkt:
            wkt = 'SRID=4326;' + wkt
        return wkt
