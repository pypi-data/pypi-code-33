# pylama:ignore=R0903,W0613,R0201
from rest_framework import status
from rest_framework.response import Response


class ListResourceMixin:
    def list(self, request, *args, **kwargs):
        resource = self.get_queryset()
        serializer = self.get_serializer(resource.list(), many=True)
        return Response(serializer.data)


class CreateResourceMixin:
    def create(self, request, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            # These kwargs will be passed in as extra validated data to create in the Resource
            serializer.save(**kwargs)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RetrieveResourceMixin:
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance.retrieve())
        return Response(serializer.data)


class UpdateResourceMixin:
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        # Need to pass along the same keyword arguments for perform update
        # So that it will feed into the serializer, but more importantly the resource
        serializer.save(**kwargs)
        return Response(serializer.data)

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True


class PartialUpdateResourceMixin:
    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        # Need to pass along the same keyword arguments for perform update
        # So that it will feed into the serializer, but more importantly the resource
        serializer.save(**kwargs)
        return Response(serializer.data)


class DestroyResourceMixin:
    def destroy(self, request, **kwargs):
        resource = self.get_object()
        resource.destroy(**kwargs)
        return Response(status=status.HTTP_204_NO_CONTENT)
