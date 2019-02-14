from django.contrib.auth.models import Group
from rest_framework import serializers

from .models import Consumer


class ConsumerSerializer(serializers.ModelSerializer):
    groups = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field='name')

    class Meta:
        model = Consumer
        fields = ('kong_consumer_id', 'created_at', 'updated_at', 'groups')

class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ('id', 'name')
