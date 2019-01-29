import requests
from django.conf import settings
from django.shortcuts import get_object_or_404

from gcloud_tasks.decorators import task

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from ccc.social_media.facebook.models import AccessToken
from ccc.social_media.facebook.utils import add_query_param_to_url


class GraphAPI(object):
    url = 'https://graph.facebook.com/v' + settings.SMM_FACEBOOK_API_VERSION + '/{}'
    access_token = None

    def __init__(self, access_token=None):
        if access_token is not None:
            self.access_token = access_token
            self.url = add_query_param_to_url(self.url, {'access_token': access_token})

    def construct_url_with_endpoint(self, endpoint):
        self.url = self.url.format(endpoint)

    def get_ep(self, endpoint=None, method='GET', data=None, files=None, json=None):
        if files is None:
            files = {}
        if data is None:
            data = {}
        self.construct_url_with_endpoint(endpoint)
        response = self.__send_request(self.url, method, data, files, json)
        if response.get('error', None) is None:
            # If response does not contain any error
            return Response(response, status=status.HTTP_200_OK)
        else:
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

    def get_ep_later(self, trigger_date, **kwargs):
        return self.get_ep_task(access_token=self.access_token, **kwargs).execute(trigger_date=trigger_date)

    @staticmethod
    @task(queue=settings.GOOGLE_TASK_QUEUE_DEFAULT)
    def get_ep_task(request, access_token=None, endpoint=None, method='GET', data=None, files=None, json=None):
        return GraphAPI(access_token).get_ep(endpoint, method, data, files, json)

    @staticmethod
    def __send_request(url, method='GET', data=None, files=None, json=None):
        if files is None:
            files = {}
        if data is None:
            data = {}
        try:
            if method == 'GET':
                response = requests.get(url)
            elif method == 'DELETE':
                response = requests.delete(url)
            else:
                response = requests.post(url, data=data, files=files, json=json)
        except requests.exceptions.ConnectionError:
            return {'error': 'Gateway Error!', 'message': 'Facebook could not be reached'}
        return response.json()


class RetrieveEndpoint(APIView, GraphAPI):
    permission_classes = (IsAuthenticated,)
    url = 'https://graph.facebook.com/v' + settings.SMM_FACEBOOK_API_VERSION + '/{}'

    def dispatch(self, request, *args, **kwargs):
        target_account_user_id = request.GET.get('facebook_user_id', None)
        if target_account_user_id is None:
            # If the user id is not provided, the pick the first connected account of the user
            access_token_object = AccessToken.objects.filter(user=request.user).first()
        else:
            access_token_object = get_object_or_404(AccessToken, user=request.user, facebook_uid=target_account_user_id)
        if access_token_object is not None:
            self.url = add_query_param_to_url(self.url, {'access_token': access_token_object.token})
        return super(RetrieveEndpoint, self).dispatch(request, *args, **kwargs)


class SMMFacebookRequestNode(RetrieveEndpoint):
    endpoint = None

    def get(self, request, *args, **kwargs):
        response = self.get_ep(endpoint=self.endpoint)
        return response

    def post(self, request, *args, **kwargs):
        response = self.get_ep(endpoint=self.endpoint, method='POST')
        return response


class PaginatedResponseNode(SMMFacebookRequestNode):
    page_size = 50

    def offset_paginate(self, response, next_page, previous_page):
        current_url = self.request.build_absolute_uri().split('?')[0]
        page_size = self.request.query_params.get('page_size', self.page_size)
        page = self.request.query_params.get('page', 1)
        new_response = response.copy()
        new_response['next'] = add_query_param_to_url(current_url, {'page': page + 1, 'page_size': page_size}) \
            if previous_page else None
        new_response['previous'] = add_query_param_to_url(current_url, {'page': page - 1, 'page_size': page_size}) \
            if next_page else None
        return new_response

    def cursor_paginate(self, facebook_response, response_data):
        current_url = self.request.build_absolute_uri().split('?')[0]
        new_response = response_data.copy()
        new_response['next'] = add_query_param_to_url(current_url,
                                                      {'after': facebook_response.data['paging']['cursors']['before']})
        new_response['previous'] = add_query_param_to_url(current_url,
                                                          {'before': facebook_response.data['paging']['cursors'][
                                                              'after']})
        return new_response

    def get(self, request, *args, **kwargs):
        # Pagination
        after = self.request.query_params.get('after', None)
        before = self.request.query_params.get('before', None)
        page_size = self.request.query_params.get('page_size', None)
        page = self.request.query_params.get('page', None)

        if after is not None:
            self.url = add_query_param_to_url(self.url, {'after': after})
        if before is not None:
            self.url = add_query_param_to_url(self.url, {'before': before})
        if page_size is not None and int(page_size):
            # If the page size exceeds 100, change it to 100, facebook does not allow more than 100
            self.page_size = int(page_size) if int(page_size) <= 100 else 100
        if page is not None:
            self.url = add_query_param_to_url(self.url, {'offset': self.page_size * (int(page) - 1)})

        self.url = add_query_param_to_url(self.url, {'limit': self.page_size})

        response = super(PaginatedResponseNode, self).get(request, *args, **kwargs)
        new_response = dict()
        # Our data here is in response.data because what is produced here is not Response type from requests but django
        new_response['data'] = response.data.get('data', None)
        error = response.data.get('error', None)
        if error is not None:
            return Response(response.data, status=status.HTTP_400_BAD_REQUEST)

        else:
            if len(response.data['data']) != 0:
                paging = response.data.get('paging')
                if paging.get('cursors'):
                    new_response = self.cursor_paginate(response, new_response)
                else:
                    new_response = self.offset_paginate(new_response, paging.get('next'), paging.get('previous'))
            return Response(new_response, status=status.HTTP_200_OK)

