__author__ = 'zhuxietong'
from rest_framework import pagination
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer


from enum import Enum, unique
import json
from .crossdomain import crossdomain,crossappend

from django.conf import settings

ApiCode = 'status'
ApiData = 'data'
ApiMessage = 'message'

ApiPageSizeKey = 'pagesize'
ApiPageKey = 'page'

try:
    if settings.ApiCode is not None:
        ApiCode = settings.ApiCode
except Exception as e:
    pass
try:
    if settings.ApiData is not None:
        ApiData = settings.ApiData
except Exception as e:
    pass

try:
    if settings.ApiMessage is not None:
        ApiMessage = settings.ApiMessage
except Exception as e:
    pass

try:
    if settings.ApiPageSizeKey is not None:
        ApiPageSizeKey = settings.ApiPageSizeKey
except Exception as e:
    pass

try:
    if settings.ApiPageKey is not None:
        ApiPageKey = settings.ApiPageKey
except Exception as e:
    pass




class ApiState(Enum):
    failed = 0
    success = 1
    unknown = 2
    exception = 3
    invalid_wx_auth = 31

@crossdomain('')
def ApiResponse(state=ApiState.success, detail='', data=None):
    response = Response({ApiCode: state.value, ApiMessage: detail, ApiData: data})
    return response

@crossdomain('')
def ApiResp(state, detail, data):
    response = Response({ApiCode: state.value, ApiMessage: detail, ApiData: data})
    return response

from rest_framework.exceptions import APIException
from rest_framework.response import Response



from django.http import JsonResponse
from rest_framework import status

@crossdomain('')
def Api404(request, exception, *args, **kwargs):

    data = {
        'detail': 'Bad Request (404)',
        'status':ApiState.failed.value,
        'data':{}
    }
    response = JsonResponse(data, status=status.HTTP_404_NOT_FOUND)
    return response


def isRootData(data):
    validNum = 0
    if not ApiCode in data:
        return False
    if not ApiMessage in data:
        return False
    if not  ApiData in data:
        return False
    return  True


class ApiJSONRenderer(JSONRenderer):
    def render(self, data, accepted_media_type=None, renderer_context=None):
        # state = 200


        isRoot = isRootData(data)
        if not isRoot:
            data = {
                ApiCode:ApiState.success.value,
                ApiData:data,
                ApiMessage:'succss'
            }

        # if ApiCode in data:
        #     state = data[ApiCode]
        #     if state == ApiState.exception.value:
        #         err = True
        #     if state == ApiState.failed.value:
        #         err = True
        # else:
        #     data = {
        #         ApiMessage: 'success',
        #         ApiCode: ApiState.success.value,
        #         ApiData: data
        #     }
        #
        # if err:
        #
        #     detail = 'error'
        #     if isinstance(data,str):
        #         detail = data
        #     elif isinstance(data,dict):
        #         infos = []
        #         for key,value in data.items():
        #             if key != ApiCode:
        #                 infos.append(json.dumps(value))
        #
        #         detail = ';'.join(infos)
        #     else:
        #         detail = json.dumps(data)
        #     err_data = {ApiCode: 0}
        #     err_data[ApiMessage] = detail
        #     err_data[ApiData] = ''
        #     data = err_data
        #
        # else:
        #     detail = 'success'
        #
        #     obj = data
        #     if ApiData in data:
        #         obj = data[ApiData]
        #     if ApiMessage in data:
        #         detail = data[ApiMessage]
        #     data = {
        #         ApiData: obj,
        #         ApiCode: 1,
        #         ApiMessage: detail
        #     }
        # # print(renderer_context)
        # crossappend(renderer_context["response"])
        # print("=======DDD---DD",data)
        return super(ApiJSONRenderer, self).render(data=data, accepted_media_type=accepted_media_type, renderer_context=renderer_context)


class ListPagination(pagination.PageNumberPagination):
    page_size = 10
    page_size_query_param = ApiPageSizeKey
    page_query_param = ApiPageKey

    max_page_size = 1000

    @crossdomain('')
    def get_paginated_response(self, data):

        content_data = {
            'list': data,
            'total': self.page.paginator.count,
            # 'links':{
            #    'next': self.get_next_link(),
            #    'previous': self.get_previous_link()
            # },
        }
        return  ApiResponse(state=ApiState.success,detail='success',data=content_data)


class TablePagination(pagination.PageNumberPagination):
    page_size = 10
    page_size_query_param = 'length'
    max_page_size = 1000
    page_query_param = 'start'

    @crossdomain('')
    def get_paginated_response(self, data):
        # print('page:%s'%self.page.paginator.num_pages)

        print(self.request.query_params)
        page_size = self.get_page_size(self.request)
        p_number = self.request.query_params.get(self.page_query_param, 1)
        page_number = int(p_number)+1

        draw = 0
        try:
            draw = self.request.GET['draw']
            draw = int(draw)
        except Exception as e:
            print(e)

        content_data = {
            'list': data,
            'total': self.page.paginator.count,
            'size': int(page_size),
            'start': page_number,
            'draw': draw
            # 'links':{
            #    'next': self.get_next_link(),
            #    'previous': self.get_previous_link()
            # },
        }

        # response = Response(content_data)
        # return response
        return  ApiResponse(state=ApiState.success,detail='success',data=content_data)



    def paginate_queryset(self, queryset, request, view=None):
        """
        Paginate a queryset if required, either returning a
        page object, or `None` if pagination is not configured for this view.
        """
        page_size = self.get_page_size(request)
        if not page_size:
            return None

        import six
        from django.core.paginator import InvalidPage
        from rest_framework.exceptions import NotFound
        paginator = self.django_paginator_class(queryset, page_size)
        p_number = request.query_params.get(self.page_query_param, 1)

        pg_number = int(p_number)/page_size
        # step = int(1)
        page_number = pg_number + 1
        if page_number in self.last_page_strings:
            page_number = paginator.num_pages

        try:
            self.page = paginator.page(page_number)
        except InvalidPage as exc:
            msg = self.invalid_page_message.format(
                page_number=page_number, message=six.text_type(exc)
            )
            raise NotFound(msg)

        if paginator.num_pages > 1 and self.template is not None:
            # The browsable API should display pagination controls.
            self.display_page_controls = True

        self.request = request
        return list(self.page)


class OnePagination(pagination.PageNumberPagination):
    page_size = 10000
    page_size_query_param = 'page_size'
    max_page_size = 10000

    def get_paginated_response(self, data):
        content_data = {
            'list': data,
            'total': self.page.paginator.count,
            # 'links':{
            #    'next': self.get_next_link(),
            #    'previous': self.get_previous_link()
            # },
        }
        return  ApiResponse(state=ApiState.success,detail='success',data=content_data)
