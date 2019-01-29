from rest_framework import serializers

from ccc.beacons.models import Beacon


class BeaconSerializer(serializers.ModelSerializer):

    """
    Purpose: A serializer that deals with Beacon instances and
    querysets.
    """
    class Meta(object):
        model = Beacon
        fields = ('id', 'name', 'uid', 'url', )
