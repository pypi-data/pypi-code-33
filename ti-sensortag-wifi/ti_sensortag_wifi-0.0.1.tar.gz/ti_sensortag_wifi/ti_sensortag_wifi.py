from urllib.request import urlopen
from html.parser import HTMLParser
from typing import Tuple
import datetime


class SensorTagData:
    temperature: float
    ir_temperature: float
    humidity: float
    pressure: float
    accelerometer: Tuple[float, float, float]
    magnetometer: Tuple[float, float, float]
    gyroscope: Tuple[float, float, float]
    light: float
    key: int

    def __init__(self):
        self.time = {'time': datetime.datetime.now()}
        self.temperature = None
        self.ir_temperature = None

    def __str__(self):
        return str(self.__dict__)


class SensorTagParser(HTMLParser):
    def error(self, message):
        pass

    def __init__(self):
        HTMLParser.__init__(self)
        self.sensor_type = None
        self.sensor_data = SensorTagData()

    def handle_starttag(self, tag, attrs):
        if tag == "p":
            attrs = dict(attrs)
            if 'id' in attrs:
                self.sensor_type = attrs['id']

    def handle_data(self, data_string):
        if self.sensor_type is not None:
            data = data_string.split(' ')
            if self.sensor_type == 'tmp':
                self.sensor_data.temperature = data[2]
                self.sensor_data.ir_temperature = data[3]
            elif self.sensor_type == 'hum':
                self.sensor_data.humidity = data[3]
            elif self.sensor_type == 'bar':
                self.sensor_data.pressure = data[3]
            elif self.sensor_type == 'gyr':
                self.sensor_data.gyroscope = (data[3], data[4], data[5])
            elif self.sensor_type == 'acc':
                self.sensor_data.accelerometer = (data[3], data[4], data[5])
            elif self.sensor_type == 'opt':
                self.sensor_data.light = data[1]
            elif self.sensor_type == 'mag':
                self.sensor_data.magnetometer = (data[3], data[4], data[5])
            elif self.sensor_type == 'key':
                self.sensor_data.key = data[0]
            self.sensor_type = ""


class SensorTag:
    def __init__(self, ip_address):
        self.ip_address = ip_address

    def update(self):
        url = "http://" + self.ip_address + "/param_sensortag_poll.html"
        result = urlopen(url).read()
        parser = SensorTagParser()
        parser.feed(result.decode("utf-8"))
        return parser.sensor_data


if __name__ == "__main__":
    import sys
    import time

    args = sys.argv
    sensortag = SensorTag(args[1])

    while True:
        try:
            print(sensortag.update())
        except ValueError:
            print("failed")
        time.sleep(1)
