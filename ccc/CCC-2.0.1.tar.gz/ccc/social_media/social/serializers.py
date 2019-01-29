from django.contrib.auth import get_user_model
from rest_framework import serializers

from ccc.social_media.social.models import Post, PostedTo

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'first_name',
            'last_name',
        )


class PostedToSerializer(serializers.ModelSerializer):
    target = serializers.CharField(source='get_target_display')

    class Meta:
        model = PostedTo
        fields = (
            'target',
            'target_id',
            'target_link'
        )


class PostSerializer(serializers.ModelSerializer):
    targets = PostedToSerializer(source='postedto_set.all', many=True)
    user = UserSerializer()

    class Meta:
        model = Post
        fields = (
            'user',
            'location',
            'content',
            'media',
            'created',
            'schedule_date',
            'targets'
        )
