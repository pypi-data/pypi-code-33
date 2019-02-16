from rest_framework.exceptions import APIException

from rest_framework import viewsets
from rest_framework.viewsets import ViewSet
from rest_framework.decorators import action
from .auth import AdminTokenAuth


from meapp.location import models
from meapp.api.response import ApiResp,ApiState
from meapp.api import response
from meapp.api.view.authView import ApiAuthView
from meapp.api.crawl import param_crawl

from ..models import Admin,AdminToken
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
        # print(request.user)
        return ApiResp(ApiState.failed, "上传失败", '')

    @action(methods=['post', 'options'], detail=False)
    @param_crawl(checker={
        'username':{'n':True},
    })
    def get(self, request):
        try:
            username = request.api_params.get('username','')

            u,isnew = Admin.objects.get_or_create(username=username)
            token,created = AdminToken.objects.get_or_create(user=u)

            resp = ApiResp(ApiState.success, "成功获取数据", {'id':u.id,'token':token.key,'username':username})
            return resp
        except Exception as e:
            return ApiResp(ApiState.failed, e.__str__(), '')

    @action(methods=['post', 'options'], detail=False, authentication_classes=[AdminTokenAuth])
    def avatar(self, request):
        admin = request.user
        admin.avatar = request.FILES.get('file')
        admin.save()
        resp = ApiResp(ApiState.success, "上传成功", admin.avatar.url)
        return resp





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