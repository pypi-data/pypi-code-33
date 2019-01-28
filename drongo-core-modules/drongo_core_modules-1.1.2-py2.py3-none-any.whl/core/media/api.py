from drongo_utils.endpoint import ViewEndpoint

from drongo_utils.helpers import URLHelper

from .admin.api import AVAILABLE_API as AVAILABLE_ADMIN_API


class MediaServe(ViewEndpoint):
    __url__ = '/{container}/{key}'

    def init(self):
        self.media = self.ctx.modules.media
        self.token = self.ctx.request.query.get('token', [None])[0]

    def call(self):
        self.init()  # TODO: Fix this

        self.media.services.MediaServeService(
            container=self.container,
            key=self.key,
            query=self.ctx.request.query,
            response=self.ctx.response,
            token=self.token
        ).call()


AVAILABLE_API = [
    MediaServe
]


class MediaAPI(object):
    def __init__(self, app, module, base_url='/api/media'):
        self.app = app
        self.module = module
        self.base_url = base_url

        for api in AVAILABLE_API + AVAILABLE_ADMIN_API:
            URLHelper.endpoint(
                app=self.app,
                klass=api,
                base_url=base_url
            )
