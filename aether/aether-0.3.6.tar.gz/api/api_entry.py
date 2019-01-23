import argparse
import logging
import bjoern
from aether_shared.api_global_objects import api_global_objects
from aether import GlobalConfig

from flask import Flask
from flask_cors import CORS
from flask_restful import Api
from flask_caching import Cache

from api.processes.DynamicTilerResource import DynamicTilerResource
from api.processes.AppSupportResource import AppSupportResource
from api.processes.CloudGatewayResource import CloudGatewayResource
from api.processes.DataModelResource import DataModelResource
from api.processes.EndpointConsumerResource import EndpointConsumerResource
from api.processes.ClipAndShipResource import ClipAndShipResource
from api.processes.SkyApplicationResource import SkyApplicationResource
from api.processes.UserAdminResource import UserAdminResource
from api.resources.CroplandDataLayerResource import CroplandDataLayerResource
from api.resources.LandSatResource import LandSatResource
from api.resources.SentinelResource import SentinelResource

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def api_app():
    app = Flask(__name__)
    app.config['CACHE_TYPE'] = 'simple'
    app.cache = Cache(app)


    CORS(app)
    api = Api(app)

    global_objects = api_global_objects()

    api.add_resource(DynamicTilerResource, '/api/v1.0/tiler/dynamic_tiler/',
                     resource_class_kwargs={'global_objects': global_objects})

    api.add_resource(CroplandDataLayerResource, '/api/v1.0/search/cropland_data_layer/',
                     resource_class_kwargs={'global_objects': global_objects})
    api.add_resource(LandSatResource, '/api/v1.0/search/landsat/',
                     resource_class_kwargs={'global_objects': global_objects})
    api.add_resource(SentinelResource, '/api/v1.0/search/sentinel/',
                     resource_class_kwargs={'global_objects': global_objects})

    api.add_resource(ClipAndShipResource, '/api/v1.0/sky/clip_and_ship/',
                     resource_class_kwargs={'global_objects': global_objects})
    api.add_resource(CloudGatewayResource, '/api/v1.0/sky/download/',
                     resource_class_kwargs={'global_objects': global_objects})

    api.add_resource(SkyApplicationResource, '/api/v1.0/sky/application/',
                     resource_class_kwargs={'global_objects': global_objects})
    api.add_resource(EndpointConsumerResource, '/api/v1.0/sky/<uuid>/application/<application_id>/',
                     resource_class_kwargs={'global_objects': global_objects})

    api.add_resource(AppSupportResource, '/api/v1.0/sky/app_support/',
                     resource_class_kwargs={'global_objects': global_objects})
    api.add_resource(UserAdminResource, '/api/v1.0/sky/user_admin/',
                     resource_class_kwargs={'global_objects': global_objects})

    api.add_resource(DataModelResource, '/api/v1.0/datamodel/data/',
                     resource_class_kwargs={'global_objects': global_objects})

    return app


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--port', default=5002, type=int, help='port for api. Default is 5002.')
    parser.add_argument('--host', default="0.0.0.0", type=str, help='localhost for api relative to docker container. Default is 0.0.0.0.')
    parser.add_argument('--aether_host', default="data.runsonaether.com", type=str, help='host for api. Default is data.runsonaether.com')
    parser.add_argument('--is_local', default=False, type=bool, help='Is the server running on localhost? True/False')
    args = parser.parse_args()

    app = api_app()

    aether_host = args.aether_host
    if args.is_local:
        logger.warn("##################################################")
        logger.warn("")
        logger.warn("RUNNING LOCAL DEV SERVER. IS THIS WHAT YOU INTEND?")
        logger.warn("")
        logger.warn("##################################################")
        GlobalConfig._switch_service_locality(to_local=args.is_local)
        aether_host = "127.0.0.1"

    GlobalConfig.hostport = "{}:{}".format(aether_host, args.port)
    logger.info("Initiating Data API Service with args: {}".format(args))
    app.run(port=args.port, host=args.host, debug=True, threaded=True, use_reloader=False)
    bjoern.run(app, host=args.host, port=args.port)
