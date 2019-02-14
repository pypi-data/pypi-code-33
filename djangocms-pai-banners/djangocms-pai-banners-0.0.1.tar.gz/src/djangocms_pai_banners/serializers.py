from rest_framework import serializers

from .models import Banner


class BannerSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    def get_image(self, obj):
        if obj.image:
            return obj.image.url

    class Meta:
        model = Banner
        read_only_fields = ('id', 'created_at')
        fields = read_only_fields + ('starts_on', 'ends_on', 'name', 'image', 'code', 'value')
