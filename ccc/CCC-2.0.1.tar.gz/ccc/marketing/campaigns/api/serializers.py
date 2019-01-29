import json

from django.urls import reverse
from phonenumber_field.validators import validate_international_phonenumber
from rest_framework import serializers

from ccc.campaigns.cloud_tasks import follow_up_campaign_trigger
from ccc.campaigns.models import (IMMS, ISMS, OMMS, OSMS, Campaign,
                                  CampaignEmailTemplate, EmailCampaign,
                                  IEmail, IVoiceCall,
                                  MappedKeywords, MMSCampaign, OEmail,
                                  OVoiceCall, SampleVoiceCall, SMSCampaign,
                                  VoiceCampaign, FollowUpDetail)
from ccc.constants import DURATION_CHOICES
from ccc.marketing.api.serializers import TeamMemberSerializer
from ccc.marketing.campaigns.api.constants import SCHEDULE_CHOICES
from ccc.packages.models import TwilioNumber
from ccc.template_design.models import TemplateDesign
from django_filters import rest_framework as django_filters
from django_filters.rest_framework import FilterSet


# class FUCampaignFilter(FilterSet):
#     class Meta:
#         model = FUCampaign
#         exclude = ('voice_original', 'voice_converted', 'att1', 'att2', 'att3', 'att4', 'att5', 'att6',
#                    'mms_image1', 'mms_image2', 'mms_video')
#
#
# class FUCampaignSerializer(serializers.ModelSerializer):
#     """Followup Campaign Serializer"""
#     url = serializers.SerializerMethodField()
#
#     class Meta:
#         model = FUCampaign
#         fields = '__all__'
#
#     def get_url(self, obj):
#         try:
#             return reverse('srm:marketing:campaigns:edit_fu_campaigns', args=[obj.campaign.id, obj.id])
#         except AttributeError:
#             return
#
#     def validate_company(self, company):
#         if not company:
#             raise serializers.ValidationError("This field is required.")
#         return company
#
#     def validate_name(self, name):
#         if not name:
#             raise serializers.ValidationError("This field is required.")
#         return name
#
#     def validate_phone(self, phone):
#         if not phone:
#             raise serializers.ValidationError("This field is required.")
#         return phone


class CampaignFilter(FilterSet):
    name = django_filters.CharFilter(name='name', lookup_expr='icontains')
    created_at = django_filters.DateFilter(lookup_expr='icontains', name='created_at')

    class Meta:
        model = Campaign
        exclude = ('voice_greeting_original', 'voice_greeting_converted',
                   'mms_image1', 'mms_image2', 'mms_video', 'logo')


class FollowUpDetailSerializer(serializers.ModelSerializer):
    schedule_type = serializers.SerializerMethodField()

    class Meta:
        model = FollowUpDetail
        fields = '__all__'
        extra_kwargs = {
            'sp_date': {
                'allow_null': True
            },
            'campaign': {
                'read_only': True
            },
            'sent_to': {
                'read_only': True
            }
        }

    def get_schedule_type(self, obj):
        for c in SCHEDULE_CHOICES:
            if getattr(obj, c):
                return c
        return ''

    def validate(self, attrs):
        custom = attrs.get('custom')
        specific = attrs.get('specific')
        recur = attrs.get('recur')
        recur_interval = attrs.get('recur_interval')
        recur_interval_unit = attrs.get('recur_interval_unit')
        specific_date = attrs.get('sp_date')
        custom_delay = attrs.get('custom_delay')
        custom_delay_unit = attrs.get('custom_delay_unit')
        errors = {}
        if custom:
            if not custom_delay:
                errors.update({'custom_delay': 'This field is required'})
            if not custom_delay_unit:
                errors.update({'custom_delay_unit': 'This field is required'})
        if specific:
            if not specific_date:
                errors.update({'specific_date': 'This field is required'})
        if recur:
            if not recur_interval:
                errors.update({'recur_interval': 'This field is required'})
            if not recur_interval_unit:
                errors.update({'recur_interval_unit': 'This field is required'})
        if bool(errors):
            raise serializers.ValidationError(errors)
        return attrs


class CampaignSerializer(serializers.ModelSerializer):
    logo_url = serializers.SerializerMethodField()
    is_email_campaign = serializers.SerializerMethodField()
    is_voice_campaign = serializers.SerializerMethodField()
    is_sms_campaign = serializers.SerializerMethodField()
    is_mms_campaign = serializers.SerializerMethodField()
    detail_url = serializers.SerializerMethodField()
    archive_url = serializers.SerializerMethodField()
    follow_up = serializers.SerializerMethodField()
    fu_url = serializers.SerializerMethodField()
    phone_number = serializers.SerializerMethodField()
    phone = serializers.PrimaryKeyRelatedField(required=False, queryset=TwilioNumber.objects.all())
    redirect_no = serializers.SerializerMethodField(read_only=True)
    team_name = serializers.SerializerMethodField(read_only=True)
    team_members = serializers.SerializerMethodField(read_only=True)
    follow_up_details = FollowUpDetailSerializer(source='followupdetail', allow_null=True, required=False)

    class Meta:
        model = Campaign
        fields = '__all__'
        extra_kwargs = {
            'phone': {
                'required': True,
            },
            'name': {
                'required': True,
                'allow_blank': False,
                'allow_null': False
            },
            'company': {
                'required': True,
                'allow_blank': False,
                'allow_null': False
            }
        }

    def get_phone_number(self, obj):
        if obj.phone:
            return obj.phone.friendly_name

    def get_is_email_campaign(self, obj):
        """is_email_campaign"""
        return obj.emailcampaign_set.exists()

    def get_is_voice_campaign(self, obj):
        """is_email_campaign"""
        return obj.voicecampaign_set.exists()

    def get_is_sms_campaign(self, obj):
        """is_email_campaign"""
        return obj.smscampaign_set.exists()

    def get_is_mms_campaign(self, obj):
        """is_email_campaign"""
        return obj.mmscampaign_set.exists()

    def get_logo_url(self, obj):
        if obj.logo:
            return self.context['request'].build_absolute_uri(obj.logo.url)

    def get_detail_url(self, obj):
        url = reverse('srm:marketing:campaigns:edit_campaign', args=[obj.id])
        if obj.is_follow_up:
            url = reverse('srm:marketing:campaigns:edit_fu_campaigns', args=[obj.id])
        if obj.active:
            return url
        return url + '?archive=true'

    def get_archive_url(self, obj):
        url = reverse('srm:api_marketing:campaigns:archive_campaign', args=[obj.id])
        if obj.active:
            return url
        return url + '?archive=true'

    def get_follow_up(self, obj):
        """Get follow up"""
        return CampaignSerializer(obj.campaign_set.all(), many=True, context=self.context).data

    def get_fu_url(self, obj):
        return reverse('srm:marketing:campaigns:create_fu_campaigns', args=[obj.id])

    def get_redirect_no(self, obj):
        if obj.redirect_no:
            return obj.redirect_no.to_no
        return None

    def get_team_name(self, obj):
        if obj.team:
            return obj.team.name
        return None

    def get_team_members(self, obj):
        if obj.team:
            return TeamMemberSerializer(obj.team.members(), many=True).data
        return []

    def validate_follow_up_details(self, follow_up):
        schedule_type = None
        errors = {}
        for c in SCHEDULE_CHOICES:
            if follow_up.get(c, None):
                schedule_type = c
        if schedule_type:
            pass
        else:
            errors.update({'schedule_type': ['Please select a valid schedule.']})
        if bool(errors):
            raise serializers.ValidationError(errors)
        return follow_up

    def readable_duration(self, duration, unit):
        unit = unit.rstrip('s').lower()
        if duration < 2:
            return str(duration) + ' ' + unit + 's'
        return str(duration) + ' ' + unit + 's'

    def get_filtered_campaign_channels(self, campaign, filter_params):
        voice = campaign.voicecampaign_set.filter(**filter_params).first()
        sms = campaign.smscampaign_set.filter(**filter_params).first()
        mms = campaign.mmscampaign_set.filter(**filter_params).first()
        email = campaign.emailcampaign_set.filter(**filter_params).first()
        return voice, sms, mms, email

    def verify_onleadcapture(self, follow_up, other_follow_ups):
        errors = list()
        other_follow_ups = other_follow_ups.filter(followupdetail__onleadcapture=True)
        parent_campaign = follow_up.parent_campaign
        # filter the parent campaign channels by 'no delay or no trigger'
        voice, sms, mms, email = self.get_filtered_campaign_channels(parent_campaign, {'delay_type': None,
                                                                                       'trigger_date': None})
        error_message_follow_up = 'You have other follow up campaigns under the ' + parent_campaign.name + \
                                  ' that send {} on lead capture.'
        error_message_parent = 'The parent campaign already sends a {} on lead capture.'
        if all([voice, parent_campaign.use_voice, follow_up.use_voice]):
            errors.append(error_message_parent.format('voice message'))
        if all([sms, parent_campaign.use_sms, follow_up.use_sms]):
            errors.append(error_message_parent.format('SMS'))
        if all([mms, parent_campaign.use_mms, follow_up.use_mms]):
            errors.append(error_message_parent.format('MMS'))
        if all([email, parent_campaign.use_email, follow_up.use_email]):
            errors.append(error_message_parent.format('email'))

        if follow_up.use_email and other_follow_ups.filter(use_email=True).exists():
            errors.append(error_message_follow_up.format('email'))
        if follow_up.use_mms and other_follow_ups.filter(use_mms=True).exists():
            errors.append(error_message_follow_up.format('MMS'))
        if follow_up.use_sms and other_follow_ups.filter(use_sms=True).exists():
            errors.append(error_message_follow_up.format('SMS'))
        if follow_up.use_voice and other_follow_ups.filter(use_voice=True).exists():
            errors.append(error_message_follow_up.format('voice'))
        if bool(errors):
            raise serializers.ValidationError({'time_clash': errors})

    def verify_now4leads(self, follow_up, other_follow_ups):
        pass

    def verify_custom(self, follow_up, follow_up_details, other_follow_ups):
        errors = list()
        custom_delay = follow_up_details.get('custom_delay')
        custom_delay_unit = follow_up_details.get('custom_delay_unit')
        custom_delay_unit_readable = dict(DURATION_CHOICES).get(custom_delay_unit)
        readable_duration = self.readable_duration(custom_delay, custom_delay_unit_readable)
        other_follow_ups = other_follow_ups.filter(followupdetail__custom=True,
                                                   followupdetail__custom_delay=custom_delay,
                                                   followupdetail__custom_delay_unit=custom_delay_unit)
        parent_campaign = follow_up.parent_campaign
        # filter the parent campaign channels by the custom delays
        voice, sms, mms, email = self.get_filtered_campaign_channels(parent_campaign, {'delay_type': custom_delay_unit,
                                                                                       'delay_value': custom_delay})
        error_message_follow_up = 'There are other follow up campaigns under ' + parent_campaign.name + \
                                  ' that send {} {} after capture.'
        error_message_parent = 'Parent campaign already sends a {} ' + readable_duration + ' after capture.'
        if all([voice, parent_campaign.use_voice, follow_up.use_voice]):
            errors.append(error_message_parent.format('voice message'))
        if all([sms, parent_campaign.use_sms, follow_up.use_sms]):
            errors.append(error_message_parent.format('SMS'))
        if all([mms, parent_campaign.use_mms, follow_up.use_mms]):
            errors.append(error_message_parent.format('MMS'))
        if all([email, parent_campaign.use_email, follow_up.use_email]):
            errors.append(error_message_parent.format('email'))

        if follow_up.use_email and other_follow_ups.filter(use_email=True).exists():
            errors.append(error_message_follow_up.format('email', readable_duration))
        if follow_up.use_mms and other_follow_ups.filter(use_mms=True).exists():
            errors.append(error_message_follow_up.format('MMS', readable_duration))
        if follow_up.use_sms and other_follow_ups.filter(use_sms=True).exists():
            errors.append(error_message_follow_up.format('SMS', readable_duration))
        if follow_up.use_voice and other_follow_ups.filter(use_voice=True).exists():
            errors.append(error_message_follow_up.format('voice', readable_duration))
        if bool(errors):
            raise serializers.ValidationError({'time_clash': errors})

    def verify_specific(self, follow_up, follow_up_details, other_follow_ups):
        errors = list()
        specific_date = follow_up_details.get('sp_date')
        other_follow_ups = other_follow_ups.filter(followupdetail__specific=True,
                                                   followupdetail__sp_date=specific_date)
        parent_campaign = follow_up.parent_campaign
        error_message_follow_up = 'You have other follow up campaigns under ' + parent_campaign.name + \
                                  ' that send {} at ' + str(specific_date) + '.'
        error_message_parent = 'Parent campaign already sends a {} at ' + str(specific_date) + '.'
        voice, sms, mms, email = self.get_filtered_campaign_channels(parent_campaign, {'trigger_date': specific_date})
        if all([voice, parent_campaign.use_voice]):
            errors.append(error_message_parent.format('voice message'))
        if all([sms, parent_campaign.use_sms]):
            errors.append(error_message_parent.format('SMS'))
        if all([mms, parent_campaign.use_mms]):
            errors.append(error_message_parent.format('MMS'))
        if all([email, parent_campaign.use_email]):
            errors.append(error_message_parent.format('email'))

        if follow_up.use_email and other_follow_ups.filter(use_email=True).exists():
            errors.append(error_message_follow_up.format('email'))
        if follow_up.use_mms and other_follow_ups.filter(use_mms=True).exists():
            errors.append(error_message_follow_up.format('MMS'))
        if follow_up.use_sms and other_follow_ups.filter(use_sms=True).exists():
            errors.append(error_message_follow_up.format('SMS'))
        if follow_up.use_voice and other_follow_ups.filter(use_voice=True).exists():
            errors.append(error_message_follow_up.format('voice'))
        if bool(errors):
            raise serializers.ValidationError({'time_clash': errors})

    def verify_recur(self, follow_up, follow_up_details, other_follow_ups):
        errors = list()
        recur_delay = follow_up_details.get('recur_interval')
        recur_delay_unit = follow_up_details.get('recur_interval_unit')
        recur_delay_unit_readable = dict(DURATION_CHOICES).get(recur_delay_unit)
        readable_duration = self.readable_duration(recur_delay, recur_delay_unit_readable)
        other_follow_ups = other_follow_ups.filter(followupdetail__recur=True,
                                                   followupdetail__recur_interval=recur_delay,
                                                   followupdetail__recur_interval_unit=recur_delay_unit)
        error_message = 'You have other follow up campaigns under ' + follow_up.parent_campaign.name + \
                        ' that send {} every {} after capture.'
        if follow_up.use_email and other_follow_ups.filter(use_email=True).exists():
            errors.append(error_message.format('email', readable_duration))
        if follow_up.use_mms and other_follow_ups.filter(use_mms=True).exists():
            errors.append(error_message.format('MMS', readable_duration))
        if follow_up.use_sms and other_follow_ups.filter(use_sms=True).exists():
            errors.append(error_message.format('SMS', readable_duration))
        if follow_up.use_voice and other_follow_ups.filter(use_voice=True).exists():
            errors.append(error_message.format('voice', readable_duration))
        if bool(errors):
            raise serializers.ValidationError({'time_clash': errors})

    def verify_no_time_clash(self, follow_up, follow_up_details):
        is_onleadcapture = follow_up_details.get('onleadcapture')
        is_now4leads = follow_up_details.get('now4leads')
        is_custom = follow_up_details.get('custom')
        is_specific = follow_up_details.get('specific')
        is_recur = follow_up_details.get('recur')
        other_follow_ups = follow_up.parent_campaign.campaign_set.all().exclude(pk=follow_up.id)
        if is_onleadcapture:
            self.verify_onleadcapture(follow_up, other_follow_ups)
        if is_now4leads:
            self.verify_now4leads(follow_up, other_follow_ups)
        if is_custom:
            self.verify_custom(follow_up, follow_up_details, other_follow_ups)
        if is_specific:
            self.verify_specific(follow_up, follow_up_details, other_follow_ups)
        if is_recur:
            self.verify_recur(follow_up, follow_up_details, other_follow_ups)

    def update(self, instance, validated_data):
        follow_up_detail = validated_data.pop('followupdetail', None)
        campaign = super(CampaignSerializer, self).update(instance, validated_data)
        if follow_up_detail:
            follow_up_detail_instance = instance.followupdetail
            self.verify_no_time_clash(campaign, follow_up_detail)
            for key, value in dict(follow_up_detail).items():
                if value is not None:
                    setattr(follow_up_detail_instance, key, value)
            follow_up_detail_instance.save()
            follow_up_campaign_trigger(campaign_id=instance.id, trigger_source='form_update').execute()
        return campaign

    def create(self, validated_data):
        follow_up_detail = validated_data.pop('followupdetail', None)
        campaign = super(CampaignSerializer, self).create(validated_data)
        if follow_up_detail:
            follow_up_detail_instance = campaign.followupdetail
            self.verify_no_time_clash(campaign, follow_up_detail_instance)
            for key, value in dict(follow_up_detail).items():
                if value is not None:
                    setattr(follow_up_detail_instance, key, value)
            follow_up_detail_instance.save()
            follow_up_campaign_trigger(campaign_id=campaign.id, trigger_source='form_update').execute()
        return campaign


class EmailCampaignFilter(FilterSet):
    class Meta:
        model = EmailCampaign
        exclude = ('att1', 'att2', 'att3', 'att4', 'att5', 'att6',)


class CampaignChannelDelaySerializerMixin(serializers.ModelSerializer):
    delay_type = serializers.CharField(required=False)

    class Meta:
        pass

    def validate(self, attrs):
        from ccc.constants import DURATION_CHOICES
        delay_type = attrs.get('delay_type')
        delay_value = attrs.get('delay_value')
        if delay_type != '5':
            attrs['trigger_date'] = None
        if delay_type not in dict(DURATION_CHOICES).keys():
            attrs['delay_type'] = None
        if dict(DURATION_CHOICES).get(delay_type, None) and not delay_value:
            raise serializers.ValidationError("Please provide the '{}' delay value."
                                              .format(dict(DURATION_CHOICES).get(delay_type)))
        return attrs


class EmailCampaignSerializer(CampaignChannelDelaySerializerMixin):
    template_name = serializers.SerializerMethodField(read_only=True)
    campaign_object = CampaignSerializer(source='campaign', read_only=True)

    class Meta:
        model = EmailCampaign
        fields = '__all__'

    def get_template_name(self, obj):
        if obj.premium_template:
            return obj.premium_template.name
        return obj.template.name

    def validate(self, attrs):
        """Check if a template was attached"""
        if attrs.get('email_type') == 'basic':
            if not attrs.get('template'):
                raise serializers.ValidationError({'template': 'Please select a basic template!'})
            if not attrs.get('body') or attrs.get('body') == 'undefined':
                raise serializers.ValidationError({'body': 'A basic template requires a valid email body!'})
        if attrs.get('email_type') == 'premium' and not attrs.get('premium_template'):
            raise serializers.ValidationError({'premium_email_template': 'Please select a premium template!'})
        return super(EmailCampaignSerializer, self).validate(attrs)


class VoiceCampaignFilter(FilterSet):
    class Meta:
        model = VoiceCampaign
        exclude = ('audio', 'voice_greeting_original', 'voice_greeting_converted')


def validate_voice_file_size(file):
    # Ensure that file is not larger than 64kb
    if file.size > 64000:
        raise serializers.ValidationError('File size of {}kb exceeds limit of 64kb, you might want to record a '
                                          'shorter audio or upload a less heavier file'.format(file.size / 1000))


class VoiceCampaignSerializer(CampaignChannelDelaySerializerMixin):
    campaign_object = CampaignSerializer(source='campaign', read_only=True)
    remove_file_link = serializers.SerializerMethodField()
    audio = serializers.FileField(required=False, validators=[validate_voice_file_size])

    class Meta:
        model = VoiceCampaign
        fields = '__all__'

    def get_remove_file_link(self, obj):
        if obj:
            return reverse('srm:api_marketing:campaigns:remove_file_link', args=[obj.id, 'voice'])

    def validate(self, data):
        audio_was_uploaded = data.get('audio') or data.get('voice_to_text')
        audio_already_exists = data.get('campaign') and data.get('campaign').voicecampaign_set.last() \
                               and data.get('campaign').voicecampaign_set.last().audio
        if not audio_was_uploaded and not audio_already_exists:
            raise serializers.ValidationError('Please provide audio or voice to text')
        return super(VoiceCampaignSerializer, self).validate(data)


class SampleVoiceCallSerializer(serializers.ModelSerializer):
    audio = serializers.FileField(required=False, validators=[validate_voice_file_size])
    sample_phone = serializers.CharField(validators=[validate_international_phonenumber])

    class Meta:
        model = SampleVoiceCall
        fields = '__all__'


class MMSCampaignFilter(FilterSet):
    class Meta:
        model = MMSCampaign
        exclude = ('image1', 'image2', 'video')


def validate_mms_file_size(file):
    # Ensure that file is not larger than 5MB
    if file.size > 5000000:
        raise serializers.ValidationError('File size of {}MB exceeds limit of 5MB'.format(file.size / 1000000))


class MMSCampaignSerializer(CampaignChannelDelaySerializerMixin):
    campaign_object = CampaignSerializer(source='campaign', read_only=True)
    remove_file_link = serializers.SerializerMethodField()
    video = serializers.FileField(required=False)
    image1 = serializers.ImageField(required=False)
    image2 = serializers.ImageField(required=False)

    class Meta:
        model = MMSCampaign
        fields = '__all__'

    def get_remove_file_link(self, obj):
        if obj:
            return reverse('srm:api_marketing:campaigns:remove_file_link', args=[obj.id, 'mms'])

    def validate(self, attrs):
        image1 = attrs.get('image1') or (self.instance.image1 if self.instance else None)
        image2 = attrs.get('image2') or (self.instance.image2 if self.instance else None)
        video = attrs.get('video') or (self.instance.video if self.instance else None)
        text = attrs.get('text')
        sample_no = attrs.get('sample_no')
        if not image1 and not image2 and not video and not text:
            raise serializers.ValidationError('A media file or MMS text is required')
        image1_size = image1.size if image1 else 0
        image2_size = image2.size if image2 else 0
        video_size = video.size if video else 0
        if (image1_size + image2_size + video_size) > 5000000:
            raise serializers.ValidationError('Total media size cannot be more than 5MB')
        if self.context.get('is_sample'):
            if not sample_no:
                raise serializers.ValidationError({'sample_no': 'This field is required'})
            validate_international_phonenumber(sample_no)
        return super(MMSCampaignSerializer, self).validate(attrs)


class SMSCampaignFilter(FilterSet):
    class Meta:
        model = SMSCampaign
        fields = '__all__'


class SMSCampaignSerializer(CampaignChannelDelaySerializerMixin):
    text = serializers.CharField(required=True)
    campaign_object = CampaignSerializer(source='campaign', read_only=True)

    class Meta:
        model = SMSCampaign
        fields = '__all__'

    def validate(self, attrs):
        sample_no = attrs.get('sample_no')
        if self.context.get('is_sample'):
            if not sample_no:
                raise serializers.ValidationError({'sample_no': 'This field is required'})
            validate_international_phonenumber(sample_no)
        return super(SMSCampaignSerializer, self).validate(attrs)


class TestEmailCampaignSerializer(serializers.Serializer):
    from_email = serializers.EmailField()
    body = serializers.CharField()
    subject = serializers.CharField()
    description = serializers.CharField(required=False)
    logo = serializers.FileField(required=False)
    email_type = serializers.ChoiceField(choices=(('basic', 'Basic'), ('premium', 'Premium')),
                                         initial='basic')
    template = serializers.CharField(required=False, default=None)
    premium_email_template = serializers.CharField(required=False, default=None)
    sample_email_for_email = serializers.EmailField()

    def validate_email_type(self, value):
        if value == 'basic' and not self.initial_data.get('template') and not self.initial_data.get('email_body'):
            raise serializers.ValidationError("Invalid basic template selected.")
        elif value == 'premium' and not self.initial_data.get('premium_email_template'):
            raise serializers.ValidationError("Invalid premium template selected.")
        return value

    def validate_premium_email_template(self, value):
        if self.initial_data.get('email_type') == u'premium':
            if not value:
                raise serializers.ValidationError("Select premium template.")
            try:
                template = TemplateDesign.objects.get(pk=int(value))
            except TemplateDesign.DoesNotExist:
                raise serializers.ValidationError("Invalid template selected.")
            return template

    def validate_template(self, value):
        if self.initial_data.get('email_type') != u'premium':
            if not value and not self.initial_data.get('email_body'):
                raise serializers.ValidationError("Select email template.")
            try:
                template = CampaignEmailTemplate.objects.get(pk=value)
            except CampaignEmailTemplate.DoesNotExist:
                raise serializers.ValidationError("Invalid template selected")
            except Exception as e:
                # to handle value error when invalid or non-integer is passed
                raise serializers.ValidationError("Select Valid Template")
            return template


class TriggerCampaignSerializer(serializers.Serializer):
    contacts = serializers.ListField(required=False)
    campaigns = serializers.ListField(required=False)
    groups = serializers.ListField(required=False)


class OutgoingCallsSerializer(serializers.ModelSerializer):
    campaign_object = CampaignSerializer(source='campaign', read_only=True)
    sentiment = serializers.SerializerMethodField()

    class Meta:
        model = OVoiceCall
        fields = '__all__'

    def grade(self, percent):
        percent = int(percent)
        if percent > 90:
            return 1, 'High Positive'
        elif 80 >= percent <= 90:
            return 2, 'Positive'
        elif 60 <= percent <= 80:
            return 3, 'Average'
        elif 40 <= percent <= 50:
            return 4, 'Negative'
        else:
            return 5, 'Dangerous'

    def get_sentiment(self, obj):
        if obj.recording_sentiment_score:
            percent = ((float(obj.recording_sentiment_score) + 1) / 2) * 100
            grade, readable = self.grade(percent)
            return {'percent': percent, 'grade': grade, 'readable': readable}
        return None


class ReceivedCallsSerializer(serializers.ModelSerializer):
    campaign_object = CampaignSerializer(source='campaign', read_only=True)

    class Meta:
        model = IVoiceCall
        fields = '__all__'


class OutgoingSMSSerializer(serializers.ModelSerializer):
    campaign_object = CampaignSerializer(source='campaign', read_only=True)

    class Meta:
        model = OSMS
        fields = '__all__'


class IncomingSMSSerializer(serializers.ModelSerializer):
    campaign_object = CampaignSerializer(source='campaign', read_only=True)
    my_replies = OutgoingSMSSerializer(many=True, source='osms_set.all')

    class Meta:
        model = ISMS
        fields = '__all__'


class IncomingMMSSerializer(serializers.ModelSerializer):
    campaign_object = CampaignSerializer(source='campaign', read_only=True)
    images = serializers.SerializerMethodField()

    class Meta:
        model = IMMS
        fields = '__all__'

    def get_images(self, obj):
        media_files = obj.media_list
        images = []

        if media_files:
            media_files = json.loads(obj.media_list)
            for (media_url, mime_type) in media_files:
                if 'image' in mime_type:
                    images.append(media_url)
        return images


class OutgoingMMSSerializer(serializers.ModelSerializer):
    campaign_object = CampaignSerializer(source='campaign', read_only=True)
    media_list = serializers.JSONField(read_only=True, source='media')

    class Meta:
        model = OMMS
        fields = '__all__'


class IncomingEmailSerializer(serializers.ModelSerializer):
    campaign_object = CampaignSerializer(source='campaign', read_only=True)

    class Meta:
        model = IEmail
        fields = '__all__'


class OutgoingEmailSerializer(serializers.ModelSerializer):
    campaign_object = CampaignSerializer(source='campaign', read_only=True)

    class Meta:
        model = OEmail
        fields = '__all__'


class MappedKeywordSerializer(serializers.ModelSerializer):
    keywords = serializers.ListField(write_only=True)

    class Meta:
        model = MappedKeywords
        fields = '__all__'

    def validate(self, attrs):
        keywords = attrs.get("keywords", [])
        if not keywords:
            raise serializers.ValidationError({'keywords': 'Enter at least one keyword!'})

        campaign = attrs.get('campaign')
        used_instances = MappedKeywords.objects.filter(keyword__in=keywords, campaign__phone=campaign.phone)

        if used_instances.exists():
            used_ones = used_instances.values_list('keyword', flat=True)
            raise serializers.ValidationError({'keywords': str(list(used_ones)) + ' have been used already!'})
        return attrs

    def create(self, validated_data):
        campaign = validated_data.get("campaign")
        keywords = validated_data.get("keywords")

        MappedKeywords.objects.filter(
            campaign=campaign).update(is_active=False)

        key_obj = None

        for keyword in keywords:
            key_obj, created = MappedKeywords.objects.get_or_create(
                campaign=campaign,
                keyword=keyword)
            key_obj.is_active = True
            key_obj.save()

        # Return the last one
        return key_obj


class CampaignKeywordsSerializer(serializers.Serializer):
    campaign = serializers.SerializerMethodField()
    keywords = serializers.SerializerMethodField()

    def get_campaign(self, obj):
        return CampaignSerializer(obj, context=self.context).data

    def get_keywords(self, obj):
        return MappedKeywordSerializer(obj.mappedkeywords_set.all(), many=True).data

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass
