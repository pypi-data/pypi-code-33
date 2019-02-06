from . import DataFetcher


class Sensor:
    host = None
    port = None
    database = None
    id = None
    sensor_id = None
    current_values = {}
    last_updated_time = None
    time_offset = 9

    @staticmethod
    def parse(host, port, database, json):
        return Sensor(host, port, database,
                      json["_id"], json["sensorId"], json["currentValues"], json["lastUpdatedTime"])

    def __init__(self, host, port, database, mongo_id, sensor_id, current_values, last_updated_time):
        self.host = host
        self.port = port
        self.database = database
        self.id = mongo_id
        self.sensor_id = sensor_id
        self.current_values = current_values
        self.last_updated_time = last_updated_time

    def __str__(self) -> str:
        return self.__repr__()

    def __repr__(self) -> str:
        return "{ Sensor: id = %s, sensor_id = %s, current_values = %s, last_updated_time = %s }" % \
               (self.id, self.sensor_id, self.current_values, self.last_updated_time)

    def get_daily_summary_fetcher(self):
        return DataFetcher.create_daily_summary_fetcher(self.host, self.port, self.database,
                                                        self.sensor_id,
                                                        self.time_offset)

    def get_raw_data_fetcher(self):
        return DataFetcher.create_raw_data_fetcher(self.host, self.port, self.database,
                                                   self.sensor_id,
                                                   self.time_offset)
