from nameko.runners import ServiceRunner
from .controllers.jjb_controller import JjbController
from .settings import Constants


RUNNER = ServiceRunner(config=Constants.NAMEKO_CONFIG)
RUNNER.add_service(JjbController)
