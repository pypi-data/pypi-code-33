from django.contrib.auth.models import User
from rest_framework.serializers import ModelSerializer

from .profile import ProfileSerializer


class UserSerializer(ModelSerializer):
    profile = ProfileSerializer()

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "is_staff",
            "is_active",
            "profile",
        )
