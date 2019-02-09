from rest_framework import serializers
from tests.models import User


class UserSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(required=False, read_only=True)
    username = serializers.CharField(max_length=50, required=False, read_only=False)
    email = serializers.EmailField(required=False, read_only=False)
    first_name = serializers.CharField(max_length=50, required=False, read_only=False)
    last_name = serializers.CharField(max_length=50, required=False, read_only=False)
    validated_email = serializers.BooleanField(required=False, read_only=True)
    role = serializers.UUIDField(required=False, read_only=False)

    class Meta:
        model = User
        exclude = ('password', 'last_login', 'is_superuser', 'is_staff',
                   'is_active', 'date_joined', 'groups', 'user_permissions')
