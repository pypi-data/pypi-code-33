#!/usr/bin/env python3


import asyncio

import asyncpg

import gv_services.storage.dbstorage.dbrequest as dbrequest
import gv_services.storage.dbstorage.dbmapping as dbmapping
from gv_utils import enums


DATAPOINTEID = enums.AttId.datapointeid
DATATYPEEID = enums.AttId.datatypeeid
EID = enums.AttId.eid
ROADEID = enums.AttId.roadeid
ZONEEID = enums.AttId.zoneeid


class DbStorage:

    def __init__(self):
        self.dbpool = None
        self.datapoints = {}
        self.roads = {}
        self.zones = {}
        self.roadsdatapoints = {}
        self.zonesroads = {}

    def __del__(self):
        try:
            self.dbpool.terminate()
        except:
            pass

    async def async_init(self, dsn='postgres://gtlville:gtlville@localhost:5432/gtlville'):
        self.dbpool = await asyncpg.create_pool(dsn=dsn)
        await self._init_cache()

    async def _init_cache(self):
        roadtask = asyncio.create_task(self._init_roads())

        async def _init_road_dp_map():
            await asyncio.gather(roadtask, self._init_data_points())
            await self._init_roads_data_points()

        async def _init_zone_road_map():
            await asyncio.gather(self._init_zones(), roadtask)
            await self._init_zones_roads()

        await asyncio.gather(_init_road_dp_map(), _init_zone_road_map())

    async def _init_data_points(self):
        async for datapoint in await dbrequest.get_data_points(self.dbpool):
            self._add_data_point(datapoint)

    async def _init_roads(self):
        async for road in await dbrequest.get_roads(self.dbpool):
            self._add_road(road)

    async def _init_zones(self):
        async for zone in await dbrequest.get_zones(self.dbpool):
            self._add_zone(zone)

    async def _init_roads_data_points(self):
        async for roaddatapoint in await dbrequest.get_roads_data_points(self.dbpool):
            self._add_road_data_point(roaddatapoint)

    async def _init_zones_roads(self):
        async for zoneroad in await dbrequest.get_zones_roads(self.dbpool):
            self._add_zone_road(zoneroad)

    def _add_data_point(self, datapoint):
        datatypeeid = datapoint[DATATYPEEID]
        if datatypeeid not in self.datapoints:
            self.datapoints[datatypeeid] = {}
        eid = datapoint[EID]
        self.datapoints[datatypeeid][eid] = datapoint

    def _add_road(self, road):
        eid = road[EID]
        self.roads[eid] = road

    def _add_zone(self, zone):
        eid = zone[EID]
        self.zones[eid] = zone

    def _add_road_data_point(self, roaddatapoint):
        roadeid = roaddatapoint[ROADEID]
        if roadeid not in self.roadsdatapoints:
            self.roadsdatapoints[roadeid] = set()
        self.roadsdatapoints[roadeid].add(roaddatapoint[DATAPOINTEID])

    def _add_zone_road(self, zoneroad):
        zoneeid = zoneroad[ZONEEID]
        if zoneeid not in self.zonesroads:
            self.zonesroads[zoneeid] = set()
        self.zonesroads[zoneeid].add(zoneroad[ROADEID])

    async def insert_data_point(self, datapoints):
        if isinstance(datapoints, dict):
            datapoints = [datapoints, ]

        newdatatypes = set()
        newdatapoints = list()
        for i in range(len(datapoints)):
            datapoint = datapoints[i]
            datatypeeid = datapoint[DATATYPEEID]
            eid = datapoint[EID]
            if datatypeeid not in self.datapoints:
                newdatatypes.add(datatypeeid)
            if eid not in self.datapoints.get(datatypeeid, {}):
                newdatapoints.append(datapoint)
            else:
                datapoints[i] = self.datapoints[datatypeeid][eid]

        await dbrequest.insert_data_type(self.dbpool, newdatatypes)
        for datapoint in await dbrequest.insert_data_point(self.dbpool, newdatapoints):
            self._add_data_point(datapoint)
        return datapoints

    async def insert_road(self, roads):
        if isinstance(roads, dict):
            roads = [roads, ]

        newroads = list()
        for i in range(len(roads)):
            road = roads[i]
            eid = road[EID]
            if eid not in self.roads:
                newroads.append(road)
            else:
                roads[i] = self.roads[eid]

        for road in await dbrequest.insert_road(self.dbpool, newroads):
            self._add_road(road)
        return roads

    async def insert_zone(self, zones):
        if isinstance(zones, dict):
            zones = [zones, ]

        newzones = list()
        for i in range(len(zones)):
            road = zones[i]
            eid = road[EID]
            if eid not in self.zones:
                newzones.append(road)
            else:
                zones[i] = self.zones[eid]

        for zone in await dbrequest.insert_zone(self.dbpool, newzones):
            self._add_zone(zone)
        return zones

    async def insert_road_data_point(self, roaddatapoints):
        if isinstance(roaddatapoints, dict):
            roaddatapoints = [roaddatapoints, ]

        newroaddatapoints = list()
        for roaddatapoint in roaddatapoints:
            roadeid = roaddatapoint[ROADEID]
            if roadeid not in self.roadsdatapoints or roaddatapoint[DATAPOINTEID] not in self.roadsdatapoints[roadeid]:
                newroaddatapoints.append(roaddatapoint)

        for roaddatapoint in await dbrequest.insert_road_data_point(self.dbpool, newroaddatapoints):
            self._add_road_data_point(roaddatapoint)
        return roaddatapoints

    async def insert_zone_road(self, zoneroads):
        if isinstance(zoneroads, dict):
            zoneroads = [zoneroads, ]

        newzoneroads = list()
        for zoneroad in zoneroads:
            zoneeid = zoneroad[ZONEEID]
            if zoneeid not in self.zonesroads or zoneroad[ROADEID] not in self.zonesroads[zoneeid]:
                newzoneroads.append(zoneroad)

        for zoneroad in await dbrequest.insert_zone_road(self.dbpool, newzoneroads):
            self._add_zone_road(zoneroad)
        return zoneroads

    async def update_road(self, roads, fields):
        if isinstance(roads, dict):
            roads = [roads, ]
        if isinstance(fields, str):
            fields = [fields, ]

        modifiedroads = dict()
        for road in roads:
            eid = road[EID]
            if eid in self.roads:
                values = list()
                for field in fields:
                    value = road.get(field, self.roads[eid][field])
                    self.roads[eid][field] = value
                    values.append(value)
                modifiedroads[eid] = values

        await dbrequest.update_road(self.dbpool, modifiedroads, [dbmapping.Road.invmapping[field] for field in fields])

    async def update_zone(self, zones, fields):
        if isinstance(zones, dict):
            zones = [zones, ]
        if isinstance(fields, str):
            fields = [fields, ]

        modifiedzones = dict()
        for zone in zones:
            eid = zone[EID]
            if eid in self.zones:
                values = list()
                for field in fields:
                    value = zone.get(field, self.zones[eid][field])
                    self.zones[eid][field] = value
                    values.append(value)
                modifiedzones[eid] = values

        await dbrequest.update_zone(self.dbpool, modifiedzones, [dbmapping.Zone.invmapping[field] for field in fields])

    async def get_data_points(self, eids=None, datatypes=None):
        if datatypes is not None:
            datapoints = {datatype: self.datapoints[datatype] for datatype in datatypes if datatype in self.datapoints}
        else:
            datapoints = self.datapoints
        if eids is not None:
            datapointsfiltered = dict()
            for datatype, v in datapoints.items():
                value = {eid: v[eid] for eid in eids if eid in v}
                if value:
                    datapoints[datatype] = value
            datapoints = datapointsfiltered
        return datapoints

    async def get_roads(self, eids=None):
        if eids is not None:
            roads = {eid: self.roads[eid] for eid in eids if eid in self.roads}
        else:
            roads = self.roads
        return roads

    async def get_zones(self, eids=None):
        if eids is not None:
            zones = {eid: self.zones[eid] for eid in eids if eid in self.zones}
        else:
            zones = self.zones
        return zones

    async def get_mapping_roads_data_points(self, roadeids=None, dpeids=None, validat=None):
        if roadeids is not None:
            roadsdatapoints = {eid: self.roadsdatapoints[eid] for eid in roadeids if eid in self.roadsdatapoints}
        elif dpeids is not None:
            roadsdatapoints = {}
            for k, v in self.roadsdatapoints.items():
                value = {eid for eid in v if eid in dpeids}
                if value:
                    roadsdatapoints[k] = value
        else:
            roadsdatapoints = self.roadsdatapoints
        return roadsdatapoints

    async def get_mapping_zones_roads(self, zoneids=None, roadeids=None, validat=None):
        if zoneids is not None:
            zonesroads = {eid: self.zonesroads[eid] for eid in zoneids if eid in self.zonesroads}
        elif roadeids is not None:
            zonesroads = {}
            for k, v in self.zonesroads.items():
                value = {eid for eid in v if eid in roadeids}
                if value:
                    zonesroads[k] = value
        else:
            zonesroads = self.zonesroads
        return zonesroads
