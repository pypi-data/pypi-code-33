
from .decorators import decoratormethod

class HTTPMethodsMixIn():
    """convenience methods for .route()"""

    @decoratormethod
    def get(self, *args, **kwargs):
        return self.route(*args,  methods=['GET'], **kwargs)

    @decoratormethod
    def post(self, *args, **kwargs):
        return self.route(*args, methods=['POST'], **kwargs)

    @decoratormethod
    def put(self, *args, **kwargs):
        return self.route(*args, methods=['PUT'], **kwargs)

    @decoratormethod
    def delete(self, *args, **kwargs):
        return self.route(*args, methods=['DELETE'], **kwargs)

    @decoratormethod
    def patch(self, *args, **kwargs):
        return self.route(*args, methods=['PATCH'], **kwargs)

    @decoratormethod
    def options(self, *args, **kwargs):
        return self.route(*args, methods=['OPTIONS'], **kwargs)


class RESTFulRoutesMixIn(HTTPMethodsMixIn):
    """convenience methods for .route()

    https://medium.com/@shubhangirajagrawal/the-7-restful-routes-a8e84201f206
    https://gist.github.com/alexpchin/09939db6f81d654af06b
    """

    resource_id = '<int:id>'

    @decoratormethod
    def index(self, endpoint, *paths, **kwargs):
        "display a list of this resource"
        for path in paths or ['']:
            self.get(endpoint, f'{path}', **kwargs)
        return endpoint

    @decoratormethod
    def new(self, endpoint, *paths, **kwargs):
        "show a form to create this resource"
        for path in paths or ['']:
            self.get(endpoint, f'new{path}', **kwargs)
        return endpoint

    @decoratormethod
    def create(self, endpoint, *paths, **kwargs):
        "add a new resource to database, then redirect"
        for path in paths or ['']:
            self.post(endpoint, path, **kwargs)
        return endpoint

    @decoratormethod
    def show(self, endpoint, *paths, **kwargs):
        "show info about one resource"
        for path in paths or ['']:
            self.get(endpoint, f'/<int:id>{path}', **kwargs)
        return endpoint

    @decoratormethod
    def edit(self, endpoint, *paths, **kwargs):
        "show a form to edit one resource"
        for path in paths or ['']:
            self.get(endpoint, f'/<int:id>/edit{path}', **kwargs)
        return endpoint

    @decoratormethod
    def update(self, endpoint, *paths, **kwargs):
        "update a particular resource, then redirect"
        for path in paths or ['']:
             self.put(endpoint, f'/<int:id>{path}', **kwargs)
        return endpoint

    @decoratormethod
    def destroy(self, endpoint, *paths, **kwargs):
        "delete a particular resource, then redirect"
        for path in paths or ['']:
             self.delete(endpoint, f'/<int:id>{path}', **kwargs)
        return endpoint
