from rest_framework.exceptions import APIException

from rest_framework import viewsets
from rest_framework.viewsets import ViewSet
from rest_framework.decorators import action
from .auth import AdminTokenAuth


from meapp.location import models
from meapp.api.response import ApiResp,ApiState
from meapp.api import response
from meapp.api.view.authView import ApiAuthView

#

from . import serializer


class AdminAuthView(ApiAuthView):
    Token = models.AdminToken
    def loginResponse(self,user,token):
        data = serializer.AdminSerializer(user.manager).data
        data['token'] = token
        # ManagerSerializer(user.manager)
        return data

    def registResponse(self,user,token):
        return {'userid': user.id, 'token': token}

class AdminView(ViewSet):

    @action(methods=['post','get','options'], detail=False,authentication_classes=[AdminTokenAuth])
    def test(self, request):
        print(request.user)
        return ApiResp(ApiState.failed, "上传失败", '')




class ProvinceListView(viewsets.ModelViewSet):
    queryset = models.Province.objects.all()
    serializer_class = serializer.ProvinceSerializer
    pagination_class = response.OnePagination


class CityListView(viewsets.ModelViewSet):
    serializer_class = serializer.CitySerializer
    pagination_class = response.OnePagination

    def get_queryset(self):
        try:
            province_id = self.request.GET['province_id']
        except:
            raise APIException('lost province_id')
        try:
            province = models.Province.objects.get(pk=province_id)
        except:
            raise APIException('error province_id')
        # cities = province.cities
        # print(cities)
        return province.cities.all()


class AreaListView(viewsets.ModelViewSet):
    serializer_class = serializer.AreaSerializer
    pagination_class = response.OnePagination
    def get_queryset(self):
        try:
            city_id = self.request.GET['city_id']
        except:
            raise APIException('lost city_id')
        try:
            city = models.City.objects.get(pk=city_id)
        except:
            raise APIException('error city_id')
        return city.areas.all()