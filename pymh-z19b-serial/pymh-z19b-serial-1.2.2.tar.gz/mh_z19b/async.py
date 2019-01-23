import asyncio
import binascii
import logging
import typing

import serial_asyncio

from mh_z19b.common import SensorMixin, ReadMetricResponse

logger = logging.getLogger('mh-z19b').getChild(__name__)


class Sensor(SensorMixin):
    def __init__(self, ioloop=None):
        if ioloop is not None:
            self.loop = ioloop
        else:
            self.loop = asyncio.get_event_loop()

    async def open_serial(self, **kwargs):
        (self.reader, self.writer) = await serial_asyncio.open_serial_connection(loop=self.loop, **kwargs)

    async def send_request(self, payload, *args):
        data = self._prepare_request(payload, *args)
        self.writer.write(data)
        logger.debug('Sent: %s' % binascii.hexlify(data))
        await self.writer.drain()

    async def send_receive(self, command, *args):
        while True:
            await self.send_request(command, *args)
            buf = await asyncio.wait_for(self.reader.readexactly(9), timeout=3)
            logger.debug('Received: %s' % binascii.hexlify(buf))

            result = self.parse_response(buf)
            if result is not None:
                return result
            else:
                await asyncio.sleep(1)

    async def read_metric(self) -> typing.Optional[ReadMetricResponse]:
        result = await self.send_receive(self.READ_METRIC)
        if result:
            logger.info("Metrics: %r" % result)
        else:
            logger.error("Failed to fetch metrics")
        return result

    async def set_detection_range(self, detection_range):
        assert detection_range in [2000, 5000], "Only 2000 and 5000 ranges are supported"
        result = await self.send_receive(
            self.SET_DETECTION_RANGE % (detection_range >> 8 & 0xff, detection_range & 0xff))
        if result:
            logger.info("Detection range set to: %d" % detection_range)
        else:
            logger.error("Failed to set detection range")
        return result

    async def set_auto_calibration(self, on):
        on_off_byte = 0xA0 if on else 0x00
        result = await self.send_receive(self.SET_AUTO_CALIBRATION % on_off_byte)
        if result:
            logger.info("Auto calibration set to: %s" % "ON" if on else "OFF")
        else:
            logger.error("Failed to set auto calibration setting")
        return result

    async def start_calibration(self):
        result = await self.send_receive(self.START_CALIBRATION)
        if result:
            logger.info("Auto calibration started")
        else:
            logger.error("Failed to start auto calibration")
        return result
