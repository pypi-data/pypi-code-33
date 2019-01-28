from drongo_utils.endpoint import APIEndpoint


class ContainerCreate(APIEndpoint):
    __url__ = '/admin/containers'
    __http_methods__ = 'POST'

    def init(self):
        self.media = self.ctx.modules.media
        self.obj = self.ctx.request.json

    def validate(self):
        if not self.obj.get('name'):
            self.error(group='name', message='Container Name is required.')
            return False

        return True

    def call(self):
        self.media.services.ContainerCreateService(
            name=self.obj.get('name'),
            description=self.obj.get('description')
        ).call()


class ContainerGet(APIEndpoint):
    __url__ = '/admin/containers/{name}'

    def init(self):
        self.media = self.ctx.modules.media

    def call(self):
        return self.media.services.ContainerGetService(
            name=self.name).call().json()


class ContainerUpdate(APIEndpoint):
    __url__ = '/admin/containers/{name}'
    __http_methods__ = 'PUT'

    def init(self):
        self.media = self.ctx.modules.media
        self.obj = self.ctx.request.json

    def call(self):
        self.media.services.ContainerUpdateService(
            name=self.name,
            description=self.obj.get('description')
        ).call()


class ContainerDelete(APIEndpoint):
    __url__ = '/admin/containers/{name}'
    __http_methods__ = 'DELETE'

    def init(self):
        self.media = self.ctx.modules.media

    def call(self):
        self.media.services.ContainerDeleteService(
            name=self.name
        ).call()


class ContainerList(APIEndpoint):
    __url__ = '/admin/containers'

    def init(self):
        self.media = self.ctx.modules.media

    def call(self):
        return list(map(
            lambda item: item.json(),
            self.media.services.ContainerListService().call()
        ))


class MediaUpload(APIEndpoint):
    __url__ = '/admin/containers/{container}/upload'
    __http_methods__ = 'POST'

    def init(self):
        self.media = self.ctx.modules.media

    def call(self):
        result = []
        for f in self.ctx.request.query['file']:
            key = self.media.services.SaveMediaService(
                container=self.container,
                uploaded_file=f
            ).call()
            result.append(key)
        return result


class MediaList(APIEndpoint):
    __url__ = '/admin/containers/{container}/media'

    def init(self):
        self.media = self.ctx.modules.media

    def call(self):
        return list(map(
            lambda item: item.json(),
            self.media.services.MediaListService(
                container=self.container).call()
        ))


class MediaGet(APIEndpoint):
    __url__ = '/admin/containers/{container}/media/{key}'

    def init(self):
        self.media = self.ctx.modules.media

    def call(self):
        return self.media.services.MediaGetService(
            container=self.container,
            key=self.key
        ).call().json()


class UpdateMediaInfo(APIEndpoint):
    __url__ = '/admin/containers/{container}/{key}'
    __http_methods__ = 'PUT'

    def call(self):
        pass


class MediaDelete(APIEndpoint):
    __url__ = '/admin/containers/{container}/media/{key}'
    __http_methods__ = 'DELETE'

    def init(self):
        self.media = self.ctx.modules.media

    def call(self):
        self.media.services.MediaDeleteService(
            container=self.container,
            key=self.key
        ).call()


AVAILABLE_API = [
    ContainerCreate,
    ContainerUpdate,
    ContainerDelete,
    ContainerGet,
    ContainerList,
    MediaUpload,
    MediaList,
    MediaGet,
    UpdateMediaInfo,
    MediaDelete
]
