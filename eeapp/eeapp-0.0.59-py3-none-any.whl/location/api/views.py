from rest_framework import viewsets
from rest_framework.exceptions import APIException


try:
    from location import models
    from rest import response
except:
    from ...location import models
    from ...rest import response

from . import serializer


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