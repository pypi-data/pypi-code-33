from rest_framework import serializers

from ccc.digital_assets.models import DigitalImage


class DigitalImageSerializer(serializers.ModelSerializer):
    """Image Serializer"""

    class Meta:
        model = DigitalImage
        fields = '__all__'
