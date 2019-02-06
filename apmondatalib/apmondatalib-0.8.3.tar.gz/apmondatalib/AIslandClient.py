from .Sensor import Sensor
from .DBConnection import create_mongodb_connection


COLLECTION_SENSOR = "sensors"


def create_client(host, port, database):
    return AIslandClient(host, port, database)


class AIslandClient:
    host = None
    port = None
    database = None
    connection = None
    db = None

    def __init__(self, host, port, database):
        self.host = host
        self.port = port
        self.database = database
        self.connection = create_mongodb_connection(host, port)
        self.db = self.connection[database]

    def get_sensors(self):
        result = []
        for x in self.db[COLLECTION_SENSOR].find():
            result.append(Sensor.parse(self.host, self.port, self.database, x))
        return result

    def get_sensor(self, sensor_id):
        json = self.db[COLLECTION_SENSOR].find_one({"sensorId": sensor_id})
        if json is None:
            return None

        return Sensor.parse(self.host, self.port, self.database, json)


