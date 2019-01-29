__author__ = 'zhuxietong'
from rest_framework import pagination
from rest_framework.response import Response

from rest_framework.renderers import JSONRenderer

from enum import Enum, unique
import json
status_key = 'status'

class ApiState(Enum):
    failed = 0
    success = 1
    unknown = 2
    exception = 3


def ApiResponse(state=ApiState.success, detail='', data=None):
    response = Response({'state': state.value, 'detail': detail, 'data': data})

    response["Access-Control-Allow-Origin"] = "*"
    response["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
    response["Access-Control-Max-Age"] = "1000"
    response["Access-Control-Allow-Headers"] = "*"
    return response
    # return Response({'state':state.value,'detail':detail,'data':data})
    # if state == ApiState.success:
    #     return Response({'state':state.value,'detail':detail,'data':data})
    # elif state == ApiState.exception:
    #     return Response({'state':state.value,'detail':detail,'data':data})
    # else:
    #     return Response({'state':state.value,'detail':detail,'data':data})


class ApiJSONRenderer(JSONRenderer):
    def render(self, data, accepted_media_type=None, renderer_context=None):

        # state = 200

        err = False
        if status_key in data:
            state = data[status_key]
            if state == ApiState.exception.value:
                err = True

        if err:
            detail = 'error'
            if isinstance(data,str):
                detail = data
            elif isinstance(data,dict):
                infos = []
                for key,value in data.items():
                    if key != status_key:
                        infos.append(json.dumps(value))

                detail = ';'.join(infos)
            else:
                detail = json.dumps(data)
            err_data = {status_key: 0}
            err_data['detail'] = detail
            err_data['data'] = ''
            data = err_data

        else:
            detail = 'success'

            obj = data
            if 'data' in data:
                obj = data['data']
            if 'detail' in data:
                detail = data['detail']
            data = {
                'data': obj,
                status_key: 1,
                'detail': detail
            }
        # print(renderer_context)
        # print(renderer_context["response"].status_code)
        renderer_context
        return super(ApiJSONRenderer, self).render(data=data, accepted_media_type=accepted_media_type, renderer_context=renderer_context)


class ListPagination(pagination.PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 1000

    def get_paginated_response(self, data):
        content_data = {
            'list': data,
            'count': self.page.paginator.count,
            # 'links':{
            #    'next': self.get_next_link(),
            #    'previous': self.get_previous_link()
            # },
        }
        return Response(content_data)


class TablePagination(pagination.PageNumberPagination):
    page_size = 10
    page_size_query_param = 'length'
    max_page_size = 1000
    page_query_param = 'start'

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
            'count': self.page.paginator.count,
            'size': int(page_size),
            'start': page_number,
            'draw': draw
            # 'links':{
            #    'next': self.get_next_link(),
            #    'previous': self.get_previous_link()
            # },
        }

        response = Response(content_data)
        response["Access - Control - Allow - Origin"] = " * "
        response["Access - Control - Allow - Methods"] = "POST, GET, OPTIONS"
        response["Access - Control - Max - Age"] = "1000"
        response["Access-Control-Allow-Origin"] = " * "
        # print('------------sstogn', response)
        return response

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
            'count': self.page.paginator.count,
            # 'links':{
            #    'next': self.get_next_link(),
            #    'previous': self.get_previous_link()
            # },
        }
        return Response(content_data)
