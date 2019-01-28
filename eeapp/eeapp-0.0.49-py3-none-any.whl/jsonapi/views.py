from rest_framework.exceptions import APIException
from rest_framework import viewsets,generics


from rest_framework.decorators import list_route

from .response import ApiResponse,ApiState
from .crawl import param_crawl,save



from django.http import Http404
from django.shortcuts import get_object_or_404 as _get_object_or_404


from rest_framework.response import Response

def get_object_or_404(queryset, *filter_args, **filter_kwargs):
    """
    Same as Django's standard shortcut, but make sure to also raise 404
    if the filter_kwargs don't match the required types.
    """
    try:
        return _get_object_or_404(queryset, *filter_args, **filter_kwargs)
    except (TypeError, ValueError):
        raise Http404


class ModelView(viewsets.ModelViewSet):
    @list_route(methods=['post','get'])
    @param_crawl(checker={
        'id':{'n':True},
    })
    def delete(self,request):
        print(request.api_params['id'])
        try:
            self.serializer_class.Meta.model.objects.get(pk=request.api_params['id'])
        except Exception as e:
            raise APIException(e)
        return ApiResponse(detail='delete ok')

    @list_route(methods=['post','get'])
    def new(self, request, *args, **kwargs):
        return super(ModelView,self).create(request,*args, **kwargs)

    @list_route(methods=['post','get'])
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)


    def get_object(self):

        queryset = self.filter_queryset(self.get_queryset())

        filter_kwargs = {'pk':self.request.data['id']}
        obj = get_object_or_404(queryset, **filter_kwargs)

        self.check_object_permissions(self.request, obj)

        return obj



from rest_framework import generics, mixins, views


class ModelEditView(mixins.CreateModelMixin,
                   mixins.RetrieveModelMixin,
                   mixins.UpdateModelMixin,
                   mixins.DestroyModelMixin,
                   viewsets.GenericViewSet):

    @list_route(methods=['post','get'])
    @param_crawl(checker={
        'id':{'n':True},
    })
    def delete(self,request):
        print(request.api_params['id'])
        try:
            self.serializer_class.Meta.model.objects.get(pk=request.api_params['id'])
        except Exception as e:
            raise APIException(e)
        return ApiResponse(detail='delete ok')

    @list_route(methods=['post','get'])
    def new(self, request, *args, **kwargs):
        return super(ModelEditView,self).create(request,*args, **kwargs)

    @list_route(methods=['post','get'])
    def change(self, request, *args, **kwargs):
        return super(ModelEditView,self).update(request,*args, **kwargs)

    @list_route(methods=['post','get'])
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)


    def get_object(self):

        queryset = self.filter_queryset(self.get_queryset())

        filter_kwargs = {'pk':self.request.data['id']}
        obj = get_object_or_404(queryset, **filter_kwargs)

        self.check_object_permissions(self.request, obj)

        return obj