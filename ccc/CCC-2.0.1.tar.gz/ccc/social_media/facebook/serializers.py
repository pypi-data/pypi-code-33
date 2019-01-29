from rest_framework import serializers

from ccc.social_media.facebook.models import FacebookProfile


class FacebookProfileSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source='access_token.facebook_uid')

    class Meta:
        model = FacebookProfile
        fields = (
            'id',
            'first_name',
            'picture',
            'last_name',
            'middle_name',
            'about',
            'link',
            'name',
        )
