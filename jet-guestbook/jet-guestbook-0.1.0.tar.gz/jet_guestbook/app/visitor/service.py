# -*- coding: utf-8 -*-

from geolite2 import geolite2

from jetfactory.service import DatabaseService
from .models import VisitorModel


class VisitorService(DatabaseService):
    __model__ = VisitorModel

    def __init__(self):
        self.geoip = geolite2.reader()

    async def ipaddr_location(self, value):
        def in_english(*locations):
            for loc in locations:
                yield loc['names']['en']

        geoip = await self.loop.run_in_executor(None, self.geoip.get, value)

        if value in ['127.0.0.1', '::1']:
            return 'Localhost', 'Localdomain'
        if not geoip:
            return 'Unknown City', 'Unknown Country'

        return in_english(geoip['city'], geoip['country'])
