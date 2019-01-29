from rest_framework import serializers

from ccc.campaigns.models import ISMS, Campaign, MappedKeywords


class CampaignSerializer(serializers.ModelSerializer):
    logo_url = serializers.SerializerMethodField()
    voice_greeting = serializers.SerializerMethodField()

    class Meta:
        model = Campaign
        exclude = ('voice_greeting_original', 'voice_greeting_converted', 'logo', 'user')

    def get_logo_url(self, obj):
        if obj.logo:
            return self.context['request'].build_absolute_uri(obj.logo.url)

    def get_voice_greeting(self, obj):
        if obj.voice_greeting:
            return self.context['request'].build_absolute_uri(obj.voice_greeting.url)


class CampaignAppSerializer(serializers.ModelSerializer):

    """
    Purpose: A serializer that deals with Details instances and
    querysets.
    """

    class Meta(object):
        model = Campaign
        fields = '__all__'


class CampaignNameSerializer(serializers.ModelSerializer):

    """
    Purpose: A serializer that deals with Details instances and
    querysets.
    """

    class Meta(object):
        model = Campaign
        fields = ("name", "id")


class CampaignKeywordSerializer(serializers.ModelSerializer):
    mapped_keywords = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    phone_number = serializers.SerializerMethodField()
    initity_id = serializers.SerializerMethodField()

    class Meta:
        model = Campaign
        fields = '__all__'
        include = ['mapped_keywords', 'name', 'phone_number', 'initity_id']

    def get_phone_number(self, obj):
        return str(obj.phone)

    def get_initity_id(self, obj):
        return obj.id

    def get_name(self, obj):
        return obj.name

    def get_mapped_keywords(self, obj):
        mapped_keywords = MappedKeywords.objects.filter(
            campaign=obj.id,
            is_active=True).values_list('keyword', flat=True)
        mapped_keywords = ", ".join([str(x) for x in mapped_keywords])
        return mapped_keywords


class ISMSSerializer(serializers.ModelSerializer):

    """
    Purpose: A serializer that deals with Details instances and
    querysets.
    """
    campaign = serializers.SerializerMethodField()

    def get_campaign_name(self, obj):
        if obj.campaign:
            return obj.campaign.name
        return ''

    class Meta(object):
        model = ISMS
        fields = '__all__'
