from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(required=False, read_only=True)
    password = serializers.CharField(required=True)
    username = serializers.CharField(required=True)
    email = serializers.EmailField(required=False)
    first_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=False)

    class Meta:
        model = User
        fields = ('id', 'username', 'password', 'email', 'first_name', 'last_name')


class ProfileImageSerializer(serializers.ModelSerializer):
    file = serializers.ImageField(required=True)

    class Meta:
        model = User
        fields = ('file',)


class UpdatePasswordSerializer(serializers.ModelSerializer):
    password = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ('password',)


class ResetSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)

    class Meta:
        model = User
        fields = ('email',)


class ConfirmSerializer(serializers.Serializer):
    reset_token = serializers.CharField(required=True)
    password = serializers.CharField(required=True)


class RefreshSerializer(serializers.Serializer):
    refresh_token = serializers.CharField(required=True)
