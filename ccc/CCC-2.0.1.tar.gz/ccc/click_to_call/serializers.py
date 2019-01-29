from rest_framework import serializers

from ccc.click_to_call.models import AssociateMasterList, AutoDialerList


class AutoDialerListSerializer(serializers.ModelSerializer):
    """
    Purpose: A serializer that deals with Details instances and
    querysets.
    """
    phone_status = serializers.CharField(source='get_phone_status_display')
    phone_type = serializers.CharField(source='get_phone_type_display')

    class Meta(object):
        model = AutoDialerList
        fields = '__all__'


class AutoDialerMasterListSerializer(serializers.ModelSerializer):
    """
    Purpose: A serializer that deals with Details instances and
    querysets.
    """
    created_at = serializers.DateTimeField(format="%b %d, %Y %I:%M %p")

    class Meta(object):
        model = AssociateMasterList
        fields = '__all__'
