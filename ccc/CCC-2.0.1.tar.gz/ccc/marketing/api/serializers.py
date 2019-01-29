from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import serializers

from ccc.campaigns.models import IVoiceCall, OVoiceCall, RedirectNumber
from ccc.packages.models import TwilioNumber
from ccc.teams.models import Team, TeamMember

UserProfile = get_user_model()


class TwilioNumberSerializer(serializers.ModelSerializer):
    """Listing Twilio phone numbers"""

    class Meta:
        model = TwilioNumber
        fields = ('id', 'friendly_name',)
        read_only_fields = ('id',)


class TwilioNumberFullSerializer(serializers.ModelSerializer):
    in_use_campaign = serializers.SerializerMethodField(read_only=True)
    in_use_survey = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = TwilioNumber
        fields = (
            'id',
            'friendly_name',
            'twilio_number',
            'sms_enabled',
            'mms_enabled',
            'voice_enabled',
            'date_created',
            'in_use_campaign',
            'in_use_survey'
        )

    def get_in_use_campaign(self, obj):
        if obj.campaign_set.count() > 0:
            campaign = obj.campaign_set.last()
            return {'name': campaign.name, 'id': campaign.id}
        else:
            return {'name': '', 'id': ''}

    def get_in_use_survey(self, obj):
        if obj.surveys.count() > 0:
            survey = obj.surveys.last()
            return {'name': survey.title, 'id': survey.id}
        else:
            return {'name': '', 'id': ''}


class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = '__all__'


class TeamUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = (
            'full_name',
            'profile_image',
        )


class TeamMemberSerializer(serializers.ModelSerializer):
    user = TeamUserSerializer()
    profile_image = serializers.SerializerMethodField()

    class Meta:
        model = TeamMember
        exclude = (
            'token',
        )

    def get_profile_image(self, obj):
        if obj.user:
            return obj.user.profile_image
        return settings.STATIC_URL + 'crm/images/no-image.png'


class TwilioPhoneSerializer(serializers.Serializer):
    number = serializers.CharField(required=False)
    num_type = serializers.ChoiceField(choices=(('international', 'International'), ('local', 'Local (US/Canada)'),
                                                ('toll_free', 'Toll Free')), initial='local')
    country = serializers.CharField(required=False, initial='US')
    area_code = serializers.CharField(required=False)


class BuyTwilioNumberSerializer(serializers.Serializer):
    numbers = serializers.ListField()


class RedirectNumberSerializer(serializers.ModelSerializer):
    twilio_number_object = TwilioNumberFullSerializer(source='from_no', read_only=True)
    campaign_name = serializers.CharField(source='from_no.campaign_set.first.name', read_only=True)

    class Meta:
        model = RedirectNumber
        fields = '__all__'
        extra_kwargs = {
            'user': {
                'required': False
            },
            'from_no': {
                'required': True,
                'allow_null': False,
            },
            'to_no': {
                'required': True,
                'allow_null': False,
                'allow_blank': False
            }
        }

    def validate(self, attrs):
        if self.Meta.model.objects.filter(**attrs).exists():
            raise serializers.ValidationError('You have already added this!')
        return attrs
