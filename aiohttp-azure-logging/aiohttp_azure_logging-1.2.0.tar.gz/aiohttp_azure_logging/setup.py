import logging
import time
from .client import OMSLoggingClient
from .middleware import send_requests_to_oms
from .handler import OMSHandler

def log_to_azure(app, settings):
    app.middlewares.append(send_requests_to_oms)
    app['oms'] = OMSLoggingClient(settings)
    app_logger = logging.getLogger()
    oms_handler = OMSHandler(oms_client=app['oms'])
    oms_handler.setFormatter(logging.Formatter("%(asctime)s"))
    app_logger.addHandler(oms_handler)
    logging.Formatter.converter = time.gmtime