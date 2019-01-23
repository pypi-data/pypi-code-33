import binascii
import logging
import typing

import serial

from mh_z19b.common import SensorMixin, ReadMetricResponse

logger = logging.getLogger('mh-z19b').getChild(__name__)


class Sensor(SensorMixin):
    def __init__(self, **kwargs):
        super(Sensor, self).__init__(serial.Serial(**kwargs))

    def send_request(self, payload, *args):
        data = self._prepare_request(payload, *args)

        result = self.serial.write(data)
        logger.debug('Sent: %s' % binascii.hexlify(data))
        return result

    def send_receive(self, command, *args):
        self.serial.read(self.serial.in_waiting)  # flush all data in input buffer
        self.send_request(command, *args)
        response = self.serial.read(9)
        logger.debug('Received: %s' % binascii.hexlify(response))
        return self.parse_response(response)

    def read_metric(self) -> typing.Optional[ReadMetricResponse]:
        result = self.send_receive(self.READ_METRIC)
        if result:
            logger.info("Metrics: %r" % result)
        else:
            logger.error("Failed to fetch metrics")
        return result

    def set_detection_range(self, detection_range):
        assert detection_range in [2000, 5000], "Only 2000 and 5000 ranges are supported"
        result = self.send_receive(self.SET_DETECTION_RANGE % (detection_range >> 8 & 0xff, detection_range & 0xff))
        if result:
            logger.info("Detection range set to: %d" % detection_range)
        else:
            logger.error("Failed to set detection range")
        return result

    def set_auto_calibration(self, on):
        on_off_byte = 0xA0 if on else 0x00
        result = self.send_receive(self.SET_AUTO_CALIBRATION % on_off_byte)
        if result:
            logger.info("Auto calibration set to: %s" % "ON" if on else "OFF")
        else:
            logger.error("Failed to set auto calibration setting")
        return result

    def start_calibration(self):
        result = self.send_receive(self.START_CALIBRATION)
        if result:
            logger.info("Auto calibration started")
        else:
            logger.error("Failed to start auto calibration")
        return result
