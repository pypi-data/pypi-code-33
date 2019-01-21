from datapunt_api.rest import HALSerializer
from rest_framework import serializers

from tests import models


class WeatherStationSerializer(HALSerializer):
    class Meta:
        model = models.WeatherStation
        fields = '__all__'


class WeatherDetailStationSerializer(HALSerializer):

    detailed = serializers.SerializerMethodField()

    class Meta:
        model = models.WeatherStation
        fields = [
            '_links',
            'number',
            'detailed'
        ]

    def get_detailed(self, obj):
        return 'I am detailed'


class TemperatureRecordSerializer(HALSerializer):
    class Meta:
        model = models.TemperatureRecord
        fields = '__all__'
