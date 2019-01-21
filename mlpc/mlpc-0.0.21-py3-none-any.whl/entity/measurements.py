from mlpc.entity.base_entities import BaseEntity


class Measurements(BaseEntity):
    def __init__(self, storage):
        super().__init__(storage)

    def save(self, measurement_name, measurement):
        assert isinstance(measurement, float) or isinstance(measurement, int)
        self._storage.save_to_file("measurement", measurement_name, str(measurement), "txt")
