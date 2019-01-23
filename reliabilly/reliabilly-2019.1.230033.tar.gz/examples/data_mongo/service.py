from nameko.runners import ServiceRunner
from .controllers.data_mongo_controller import DataMongoController
from .settings import Constants

RUNNER = ServiceRunner(config=Constants.NAMEKO_CONFIG)
RUNNER.add_service(DataMongoController)
