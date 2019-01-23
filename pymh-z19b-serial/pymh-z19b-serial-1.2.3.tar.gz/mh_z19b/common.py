import typing


class ReadMetricResponse:
    def __init__(self, payload):
        self.co2 = (payload[2] << 8) + payload[3]
        self.temperature = payload[4] - 40

    def __repr__(self):
        return "co2: %d, temperature: %d" % (self.co2, self.temperature)

class SensorMixin(object):
    READ_METRIC          = b'\xFF\x01\x86\x00\x00\x00\x00\x00'
    START_CALIBRATION    = b'\xFF\x01\x87\x00\x00\x00\x00\x00'
    SET_AUTO_CALIBRATION = b'\xFF\x01\x79%c\x00\x00\x00\x00'  # on or off
    SET_DETECTION_RANGE  = b'\xFF\x01\x99\x00\x00\x00%c%c'    # 2000 or 5000

    def __init__(self, serial):
        self.serial = serial

    def _prepare_request(self, payload, *args):
        assert len(payload) == 8, "Wrong payload length"
        assert isinstance(payload, typing.ByteString), "Wrong payload type"
        payload = payload % tuple(*args)

        csum = self._checksum(payload)
        data = payload + csum
        assert len(data) == 9

        return data

    @staticmethod
    def _checksum(payload):
        checksum = sum(bytearray(payload[0:8]))
        checksum = 0xff - checksum & 0xff

        return bytes([checksum])

    def parse_response(self, payload):
        assert len(payload) == 9, "Wrong payload length"
        assert ord(self._checksum(payload)) == payload[8], "CRC error"
        if payload[0] == 0xff:
            if payload[1] == 0x86:  # Read command
                return ReadMetricResponse(payload)
            elif payload[1] == 0x99:  # detection range set
                return True
            elif payload[1] == 0x79:  # auto calibration mode set
                return True
            elif payload[1] == 0x87:  # calibration started
                return True
            elif payload[1] == 0x88:  # span calibration started
                return True
        return False
