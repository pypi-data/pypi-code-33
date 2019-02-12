"""
OdinWeb.Flask API
~~~~~~~~~~~~~~~~~

Flask implementation of the OdinWeb API interface.

The API integrates into Flask via Flasks blueprint features.

"""
from __future__ import absolute_import

from flask import request, session, Response

from odin.utils import lazy_property
from odinweb.containers import ApiInterfaceBase
from odinweb.constants import Type, Method
from odinweb.data_structures import MultiValueDict, BaseHttpRequest

# Type imports
from flask import Flask, Request  # noqa
from odinweb.data_structures import PathParam  # noqa


TYPE_MAP = {
    Type.Integer: 'int',
    Type.Long: 'int',
    Type.Float: 'number',
    Type.Double: 'number',
    Type.String: 'string',
    Type.Byte: '',
    Type.Binary: '',
    Type.Boolean: 'bool',
    Type.Date: 'string',
    Type.Time: 'string',
    Type.DateTime: 'string',
    Type.Password: 'string',
}


class RequestProxy(BaseHttpRequest):
    def __init__(self, r):
        # type: (Request) -> None
        self.request = r

    @lazy_property
    def environ(self):
        return self.request.environ

    @lazy_property
    def method(self):
        try:
            return Method(self.request.method)
        except KeyError:
            pass

    @lazy_property
    def scheme(self):
        return self.request.scheme

    @lazy_property
    def host(self):
        return self.request.host

    @lazy_property
    def path(self):
        return self.request.path

    @lazy_property
    def query(self):
        return MultiValueDict(self.request.args)

    @lazy_property
    def headers(self):
        return self.request.headers

    @lazy_property
    def cookies(self):
        return self.request.cookies

    @lazy_property
    def session(self):
        return session

    @lazy_property
    def body(self):
        return self.request.data

    @lazy_property
    def form(self):
        return MultiValueDict(self.request.form)

    @lazy_property
    def content_type(self):
        return self.request.content_type


class ApiBlueprint(ApiInterfaceBase):
    """
    A Flask Blueprint for an API::

        from flask import Flask
        from odinweb.flask.api import ApiBlueprint

        app = Flask(__name__)

        app.register_blueprint(
            ApiBlueprint(
                ApiVersion(
                    UserApi(),
                    version='v1
                )
            )
        )

    """
    def __init__(self, *containers, **options):
        self.subdomain = options.pop('subdomain', None)
        super(ApiBlueprint, self).__init__(*containers, **options)

    @staticmethod
    def node_formatter(path_node):
        # type: (PathParam) -> str
        """
        Format a node to be consumable by the `UrlPath.parse`.
        """
        if path_node.type:
            node_type = TYPE_MAP.get(path_node.type, 'str')
            return "<{}:{}>".format(node_type, path_node.name)
        return "<{}>".format(path_node.name)

    def _bound_callback(self, operation):
        def callback(**path_args):
            response = self.dispatch(operation, RequestProxy(request), **path_args)
            return Response(response.body, response.status, response.headers)
        callback.provide_automatic_options = False
        return callback

    def register(self, app, options, first_registration):
        # type: (Flask, dict, bool) -> None
        """
        Register interface

        :param app: Instance of flask.
        :param options: Options for blueprint
        :param first_registration: First registration of blueprint

        """
        for url_path, operation in self.op_paths():
            app.add_url_rule(
                url_path.format(self.node_formatter),
                '%s.%s' % (self.name, operation.operation_id),
                self._bound_callback(operation),
                methods=(m.value for m in operation.methods),
                **options
            )
