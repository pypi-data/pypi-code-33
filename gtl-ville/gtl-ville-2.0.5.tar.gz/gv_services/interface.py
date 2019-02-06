#!/usr/bin/env python3

import asyncio

from gv_services.proto.common_pb2 import ack
from gv_services.proto.interface_grpc import InterfaceBase
from gv_services.archivist import Archivist
from gv_services.broadcaster import Broadcaster
from gv_services.geographer import Geographer


class Interface(InterfaceBase):

    def __init__(self, logger, basedatapath):
        super().__init__()
        self.logger = logger
        self.archivist = Archivist(logger, basedatapath)
        self.broadcaster = Broadcaster(logger)
        self.geographer = Geographer(logger)

    async def async_init(self):
        await self.geographer.async_init()

    async def publish(self, stream):
        message = await stream.recv_message()
        status = await asyncio.gather(self.archivist.store_data(message), self.broadcaster.publish(message))
        await stream.send_message(ack(success=bool(int(sum(status)/len(status)))))

    async def subscribe(self, stream):
        await self.broadcaster.subscribe(stream)

    async def get_data(self, stream):
        await self.archivist.get_data(stream)

    async def get_data_points(self, stream):
        await self.geographer.get_data_points(stream)

    async def get_roads(self, stream):
        await self.geographer.get_roads(stream)

    async def get_zones(self, stream):
        await self.geographer.get_zones(stream)

    async def get_mapping_roads_data_points(self, stream):
        await self.geographer.get_mapping_roads_data_points(stream)

    async def get_mapping_zones_roads(self, stream):
        await self.geographer.get_mapping_zones_roads(stream)

    async def update_roads_freeflow_speed(self, stream):
        await self.geographer.update_roads_freeflow_speed(stream)

    async def update_zones_freeflow_speed(self, stream):
        await self.geographer.update_zones_freeflow_speed(stream)
