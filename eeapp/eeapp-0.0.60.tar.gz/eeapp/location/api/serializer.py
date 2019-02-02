#coding=utf-8
__author__ = 'zhuxietong'

from django.contrib.auth import authenticate
from rest_framework import serializers
# from rest_framework_expiring_authtoken.models import ExpiringToken


from django.utils.translation import ugettext_lazy as _

from rest_framework.exceptions import APIException
try:
    from ...location.models import *
except:
    from location.models import *

class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(style={'input_type': 'password'})

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        if username and password:
            user = authenticate(username=username, password=password)

            if user:
                if not user.is_active:
                    msg = _('User base is disabled.')
                    raise APIException('User base is disabled.')
            else:
                msg = _('Unable to log in with provided credentials.')
                raise APIException('Unable to log in with provided credentials.')
        else:
            msg = _('Must include "username" and "password".')
            raise APIException('Must include "username" and "password".')

        attrs['user'] = user.account.seller
        return attrs


# class GoodsImageSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = GoodsImage
#         fields = ('image','thumbnail','type')

# class GoodsBookSerializer(serializers.ModelSerializer):
#     # fine-uploader = serializers.SerializerMethodField()
#     #
#     # def get_images(self,instance):
#     #     return GoodsImageSerializer(many=True,data=instance.fine-uploader).data
#     fine-uploader = GoodsImageSerializer(many=True)
#     class Meta:
#         model = Goods
#         depth = 1
#         fields = ('name','description','price','fine-uploader')

class ProvinceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Province
        depth = 1
        fields = ('province','province_id',)

class CitySerializer(serializers.ModelSerializer):
    province = serializers.SerializerMethodField()
    province_id = serializers.SerializerMethodField()

    class Meta:
        model = City
        fields = ('city','city_id','province','province_id',)
    def get_province(self,instance):
        return instance.father.province

    def get_province_id(self,instance):
        return instance.father.province_id

class AreaSerializer(serializers.ModelSerializer):
    city = serializers.SerializerMethodField()
    city_id = serializers.SerializerMethodField()
    class Meta:
        model = Area
        fields = ('area','area_id','city','city_id',)

    def get_city(self,instance):
        return instance.father.city

    def get_city_id(self,instance):
        return instance.father.city_id

