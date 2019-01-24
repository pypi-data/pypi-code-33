"Provides logger for FluidDevOps and uses colorlog if available." ""
try:
    import colorlog as logging

    handler = logging.StreamHandler()
    handler.setFormatter(
        logging.ColoredFormatter(
            "%(log_color)s%(levelname)s:%(name)s: %(message)s"
        )
    )
except ImportError:
    import logging

    handler = logging.StreamHandler()


logger = logging.getLogger("fluiddevops")
logger.addHandler(handler)
logger.setLevel(20)
