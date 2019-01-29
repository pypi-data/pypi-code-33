from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.shortcuts import redirect
from django.urls import reverse
from django.views import View
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated

from ccc.social_media.facebook.api.utils import (GraphAPI,
                                                 PaginatedResponseNode,
                                                 SMMFacebookRequestNode)
from ccc.social_media.facebook.models import AccessToken, FacebookProfile
from ccc.social_media.facebook.serializers import FacebookProfileSerializer
from ccc.social_media.facebook.utils import add_query_param_to_url


class SMMFacebookConnectedAccounts(ListAPIView):
    def get_queryset(self):
        return FacebookProfile.objects.filter(access_token__user=self.request.user)

    serializer_class = FacebookProfileSerializer
    permission_classes = (IsAuthenticated,)


class SMMFacebookGetProfile(SMMFacebookRequestNode):
    """
    Retrieve user profile: Can carry query params of the fields required all separated by comma or space.
    E.g ?fields=name,birthday,about.
    """
    endpoint = 'me'

    def get(self, request, *args, **kwargs):
        fields = request.query_params.get('fields', None)
        if fields is not None:
            self.url = add_query_param_to_url(self.url, {'fields': fields})
        response = self.get_ep(endpoint=self.endpoint)
        return response


class SMMFacebookGetFriends(SMMFacebookRequestNode):
    """Retrieve the current user friends"""
    endpoint = 'me/friends'


class SMMFacebookFeeds(PaginatedResponseNode):
    endpoint = '{}/feed'

    def get(self, request, *args, **kwargs):
        self.endpoint = self.endpoint.format(kwargs['id'])
        self.url = add_query_param_to_url(self.url,
                                          {'fields': 'id,caption,from,picture,place,shares,icon,message,'
                                                     'name,scheduled_publish_time,likes.summary(true).limit(0),'
                                                     'comments.summary(total_count),created_time'})
        return super(SMMFacebookFeeds, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """
        Create a new status, if no 'id' is passed to the URL as query param, then create the status on the user's
        personal wall. The 'id' can either be the user's id or a page_id
        """
        page_id_or_user_id = self.request.query_params.get('id', None)
        if page_id_or_user_id is not None:
            self.endpoint = self.endpoint.format(page_id_or_user_id)
        else:
            self.endpoint = self.endpoint.format('me')
        self.url = add_query_param_to_url(self.url, {'message': self.request.data.get('message', '')}, True)
        return super(SMMFacebookFeeds, self).post(request, *args, **kwargs)


class SMMFacebookGeneric(SMMFacebookRequestNode):
    endpoint = '{}'

    def get(self, request, *args, **kwargs):
        requested_endpoint = self.kwargs.get('endpoint', None)
        if requested_endpoint is None:
            raise Http404('This endpoint does not exist')
        self.endpoint = self.endpoint.format(requested_endpoint)
        self.url = add_query_param_to_url(self.url, self.request.query_params)
        return super(SMMFacebookGeneric, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        requested_endpoint = self.kwargs.get('endpoint', None)
        if requested_endpoint is None:
            raise Http404('This endpoint does not exist')
        self.endpoint = self.endpoint.format(requested_endpoint)
        self.url = add_query_param_to_url(self.url, self.request.query_params)
        return super(SMMFacebookGeneric, self).post(request, *args, **kwargs)


class SMMFacebookGetPages(PaginatedResponseNode):
    endpoint = 'me/accounts'

    def get(self, request, *args, **kwargs):
        self.url = add_query_param_to_url(self.url, {'fields': 'id,about,access_token,business,category,'
                                                               'company_overview,picture, '
                                                               'description,engagement,is_published,link,location,name,'
                                                               'new_like_count,rating_count'})
        return super(SMMFacebookGetPages, self).get(request, *args, **kwargs)


class SMMFacebookGetGroups(PaginatedResponseNode):
    endpoint = 'me/groups'

    def get(self, request, *args, **kwargs):
        self.url = add_query_param_to_url(self.url, {'fields': 'id,email,business,picture,name,category,cover,'
                                                               'permissions,description',
                                                     'limit': '50'})
        return super(SMMFacebookGetGroups, self).get(request, *args, **kwargs)


class SMMFacebookGetPlaces(SMMFacebookRequestNode):
    endpoint = 'search'

    def get(self, request, *args, **kwargs):
        query = self.request.GET.get('q', None)
        lat = self.request.GET.get('lat', None)
        lng = self.request.GET.get('lng', None)
        self.url = add_query_param_to_url(self.url, {'type': 'place', 'fields': 'name,picture', 'q': query})
        if lat and lng:
            self.url = add_query_param_to_url(self.url, {'center': lat+','+lng, 'distance': '2000'})
        return super(SMMFacebookGetPlaces, self).get(request, *args, **kwargs)


class FacebookLogout(LoginRequiredMixin, View):
    def get(self, request):
        facebook_uid = request.GET.get('facebook_uid', None)
        if facebook_uid:
            access = AccessToken.objects.filter(facebook_uid=facebook_uid)
        else:
            access = AccessToken.objects.filter(user=request.user)
        for acc in access:
            # Revoke permissions
            graph = GraphAPI(acc.token)
            response = graph.get_ep(endpoint='{}/permissions'.format(acc.facebook_uid), method='DELETE')
        access.delete()
        return redirect(reverse('srm:social:social-home'))
