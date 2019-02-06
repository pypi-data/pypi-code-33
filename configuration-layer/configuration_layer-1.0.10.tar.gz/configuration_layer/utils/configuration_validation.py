import json
import os
from messaging_middleware.utils.logger import Logger

base_schema = {"service_name": "",
               "start_environment": "",
               "datacentre": "",
               "external_rest_services": {},
               "credentials": {},
               "persistence_conf": {}
               }


def validate_service_configuration(**kwargs):
    ssl = kwargs.get('ssl',0)
    if ssl:
        logger = Logger(ssl=1)
    else:
        logger = Logger()
    try:
        service_configuration = json.load(
            open(os.environ.get('service_configuration_directory', 'configuration') + '/service_configuration.json'))
        for key in service_configuration.keys():
            value = service_configuration[key]
            if key not in base_schema:
                logger.logmsg('error', "[validate_service_configuration] key Not found:", key)
                return False
            else:
                if base_schema[key] != value:
                    continue
                    # todo: see how can I validate values
                    # print("for key %s values are different" % key)
        return True

    except FileNotFoundError as e:
        logger.logmsg('error', "[validate_service_configuration] ERROR:", e)
