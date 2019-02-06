import logging
import logging.config

import cherrypy

from ingredients_http.tools.model import model_in, model_out, model_out_pagination
from ingredients_http.tools.param_validation import model_params


class HTTPApplication(object):
    def __init__(self, logging_config, debug=False):
        self.logger = logging.getLogger("%s.%s" % (self.__module__, self.__class__.__name__))
        self.logging_config = logging_config
        self.debug = debug

        self.database = None
        self.__mounts = []

    def register_mount(self, mount):
        self.__mounts.append(mount)

    def __setup_logging(self):
        if self.logging_config is not None:
            logging.config.dictConfig(self.logging_config)

    def __setup_mounts(self):
        config = {}

        for mount in self.__mounts:
            mount.setup()
            config[mount.mount_point] = mount.mount_config()

        cherrypy.tree.mount(None, config=config)

    def __setup_tools(self):
        cherrypy.tools.model_params = cherrypy.Tool('before_request_body', model_params, priority=10)
        cherrypy.tools.model_in = cherrypy.Tool('before_request_body', model_in, priority=20)

        cherrypy.tools.model_out = cherrypy.Tool('before_handler', model_out)
        cherrypy.tools.model_out_pagination = cherrypy.Tool('before_handler', model_out_pagination)

    def setup(self):
        # setup basic logging
        self.__setup_logging()

        if self.debug:
            self.logger.warning("==================================================================")
            self.logger.warning("RUNNING IN DEBUG MODE. DO NOT DO THIS WHILE RUNNING IN PRODUCTION.")
            self.logger.warning("==================================================================")

        # setup tools
        self.__setup_tools()

        # setup mount points
        self.__setup_mounts()

    @property
    def wsgi_application(self):

        return cherrypy.tree
