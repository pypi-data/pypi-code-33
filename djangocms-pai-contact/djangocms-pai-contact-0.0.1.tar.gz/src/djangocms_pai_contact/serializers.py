from rest_framework import serializers

from .models import Contact


class ContactSerializer(serializers.ModelSerializer):
    email = serializers.EmailField()

    class Meta:
        model = Contact
        read_only_fields = ('id', 'created_at')
        fields = read_only_fields + ('name', 'email', 'message')
