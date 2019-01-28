from rest_framework import serializers

from ..models import TestModel,OptionsModel

class TestModelSerializer(serializers.ModelSerializer):
    images = serializers.SerializerMethodField()

    class Meta:
        model = TestModel
        fields = ('name','email','covers','sex','images','hobbies','time')

    def get_images(self,instance):
        return instance.covers


class OptionModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = OptionsModel
        fields = ('name','value','id')
