from rest_framework import views
from rest_framework import viewsets

from t3.drf_adapters import mixins


class ResourceViewSetBase(viewsets.ViewSetMixin, views.APIView):
    resource_class = None
    serializer_class = None

    lookup_field = 'pk'
    lookup_url_kwarg = None

    def get_queryset(self):
        return self.get_resource(**self.kwargs)

    def get_object(self):
        # TODO: Add filter
        # TODO: Add permissions
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        assert lookup_url_kwarg in self.kwargs, (
            'Expected view %s to be called with a URL keyword argument '
            'named "%s". Fix your URL conf, or set the `.lookup_field` '
            'attribute on the view correctly.' %
            (self.__class__.__name__, lookup_url_kwarg)
        )
        # resource = self.get_resource_class()
        key = self.kwargs[lookup_url_kwarg]
        return self.get_resource(key, **self.kwargs)

    def get_resource_class(self):
        assert self.resource_class is not None, '`resource_class` missing'
        return self.resource_class
        # return resource().retrieve(key)

    def get_resource(self, *args, **kwargs):
        # assert self.resource_class is not None, '`resource_class` missing'
        resource_class = self.get_resource_class()
        kwargs['request'] = self.request
        return resource_class(*args, **kwargs)  # noqa

    def get_serializer_class(self):
        assert self.serializer_class is not None, '`serializer_class` missing'
        return self.serializer_class

    def get_serializer(self, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        kwargs['context'] = self.get_serializer_context()
        return serializer_class(*args, **kwargs)  # noqa

    def get_serializer_context(self):
        return {
            'request': self.request,
            'format': self.format_kwarg,
            'view': self
        }


class ResourceViewSet(ResourceViewSetBase):
    @classmethod
    def factory(cls, resource_class, serializer_class):
        # Add mixins based on available resource verbs
        bases = [cls, ]

        if hasattr(resource_class, 'list'):
            bases.append(mixins.ListResourceMixin)
        if hasattr(resource_class, 'create'):
            bases.append(mixins.CreateResourceMixin)
        if hasattr(resource_class, 'retrieve'):
            bases.append(mixins.RetrieveResourceMixin)
        if hasattr(resource_class, 'update'):
            bases.append(mixins.UpdateResourceMixin)
        if hasattr(resource_class, 'partial_update'):
            bases.append(mixins.PartialUpdateResourceMixin)
        if hasattr(resource_class, 'destroy'):
            bases.append(mixins.DestroyResourceMixin)

        # Create a new class so we can set the resource and serializer
        # without changing the primary class
        bases = tuple(bases)
        new_cls = type(cls.__name__, bases, {})

        new_cls.resource_class = resource_class
        # Create a new serializer class so we can set the
        # resource on it and not effect the primary serializer
        new_serializer_class = type(serializer_class.__name__, (serializer_class, ), {})
        new_serializer_class.resource_class = resource_class
        new_cls.serializer_class = new_serializer_class

        return new_cls
