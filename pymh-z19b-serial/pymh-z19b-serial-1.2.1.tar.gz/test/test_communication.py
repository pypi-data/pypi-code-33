import binascii

from mh_z19b.async import Sensor, ReadMetricResponse


def test_checksum():
    payload = binascii.unhexlify('ff01860000000000')

    assert Sensor._checksum(payload) == b'\x79'


def test_parse_read_metric_response():
    payload = binascii.unhexlify('ff86028541000000b2')

    sensor = Sensor()
    result = sensor.parse_response(payload)

    assert isinstance(result, ReadMetricResponse)
    assert 645 == result.co2
    assert 25 == result.temperature
    # assert "co2: 645, temperature: 25" == repr(result)
