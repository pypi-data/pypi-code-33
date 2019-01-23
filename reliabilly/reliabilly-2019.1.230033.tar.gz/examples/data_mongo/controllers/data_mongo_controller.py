from reliabilly.components.controllers.data_controller import DataController
from reliabilly.settings import Settings


class DataMongoController(DataController):
    name = Settings.SERVICE_NAME
