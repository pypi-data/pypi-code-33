import os
from datetime import datetime, timedelta

import magic
import pendulum
import validators
from cloud_tools.contrib.mail.send import send_templated_email
from django import forms
from django.conf import settings
from django.forms.models import (inlineformset_factory,
                                 modelformset_factory)
from twilio.rest import Client as TwilioRestClient

from ccc.campaigns.constants import EmailConstatnt
from ccc.campaigns.models import (DURATION_CHOICES, TIMEZONE_CHOICES, Campaign,
                                  CampaignMMSImages, CampaignSignupExtraField,
                                  MappedKeywords, Notify,
                                  SampleVoiceCall, VoiceCampaign)
from ccc.campaigns.utils.shortcut import remove_time_zone
from ccc.constants import step_duration_date
from ccc.contacts.forms import CampaignAndGroupMixin
from ccc.contacts.models import Contact, ContactGroup
from ccc.packages.models import TwilioNumber
from ccc.template_design.models import TemplateDesign
from .models import CampaignEmailTemplate, TemplateImages

ACCOUNT_SID = settings.TWILIO_SID
AUTH_TOKEN = settings.TWILIO_TOKEN
client = TwilioRestClient(ACCOUNT_SID, AUTH_TOKEN)

SUPPORTED_VIDEO_MIME_FORMATS = (
    'video/mpeg',
    'video/mp4',
    'video/quicktime',
    'video/webm',
    'video/3gpp',
    'video/3gpp2',
    'video/3gpp-tt',
    'video/H261',
    'video/H263',
    'video/H263-1998',
    'video/H263-2000',
    'video/H264',
)


class VCampaignForm(forms.ModelForm):
    class Meta:
        model = VoiceCampaign
        fields = ['campaign', 'audio', 'voice_to_text', 'user', 'prompt1', 'prompt2', 'ended', 'ended_at']


class NotificationForm(forms.ModelForm):
    class Meta:
        model = Notify
        fields = ['email', 'call', 'phone', 'mail', 'sms', 'duration']

    def __init__(self, *args, **kwargs):
        super(NotificationForm, self).__init__(*args, **kwargs)
        self.fields['duration'].widget.attrs['class'] = 'form-control'

    def clean(self):
        cleaned_data = super(NotificationForm, self).clean()
        if cleaned_data.get('email') and not cleaned_data.get('mail'):
            raise forms.ValidationError(
                "For receiving email notifications, you must provide you email address.")
        if cleaned_data.get('sms') and not cleaned_data.get('phone'):
            raise forms.ValidationError(
                "For receiving sms notifications, you must provide you number.")
        if cleaned_data.get('call') and not cleaned_data.get('phone'):
            raise forms.ValidationError(
                "For receiving call notifications, you must provide you number.")
        return cleaned_data


class CampaignForm(forms.ModelForm):
    class Meta:
        model = Campaign

        fields = ['name', 'phone', ]


class TestSampleVoiceForm(forms.ModelForm):
    class Meta:
        model = SampleVoiceCall
        exclude = ('user', 'voice_greeting_converted')

    def clean(self):
        cleaned_data = super(TestSampleVoiceForm, self).clean()
        if not cleaned_data.get("voice_greeting_original") and not cleaned_data.get('greeting_text').strip():
            raise forms.ValidationError("Either upload audio or fill in voice to text.")
        return cleaned_data


class TestSampleSMSForm(forms.Form):
    phone = forms.CharField()
    sms_greeting = forms.CharField()
    sample_phone_for_sms = forms.CharField()
    sample_sms_contact = forms.ModelChoiceField(queryset=Contact.objects.none(
    ), required=False)  # prevent from getting Contact info for another account

    def __init__(self, *args, **kwargs):
        contacts = kwargs.pop('contacts', None)
        super(TestSampleSMSForm, self).__init__(*args, **kwargs)
        if contacts:
            self.fields['sample_sms_contact'].queryset = contacts


class PreviewEmailForm(forms.Form):
    """ For previewing email templates, rendered with temporary data """
    from_email = forms.EmailField(required=False)

    e_greeting = forms.CharField(initial='', required=False)
    company = forms.CharField(initial='', required=False)
    description = forms.CharField(required=False)
    logo = forms.FileField(required=False)

    def clean_template(self):
        template_id = self.cleaned_data.get('template')
        if template_id:
            try:
                cet = CampaignEmailTemplate.objects.get(pk=template_id)
            except CampaignEmailTemplate.DoesNotExist:
                raise forms.ValidationError("Invalid template selected")
            return cet


class TestSampleEmailForm(PreviewEmailForm):
    email_type = forms.CharField(required=False)
    template = forms.CharField(required=False)
    premium_email_template = forms.CharField(required=False)
    e_greeting_subject = forms.CharField()
    sample_email_for_email = forms.EmailField()
    sample_email_contact = forms.ModelChoiceField(queryset=Contact.objects.none(
    ), required=False)  # prevent from getting Contact info for another account

    def __init__(self, *args, **kwargs):
        contacts = kwargs.pop('contacts', None)
        super(TestSampleEmailForm, self).__init__(*args, **kwargs)
        if contacts:
            self.fields['sample_email_contact'].queryset = contacts

    def clean_premium_email_template(self):
        if self.cleaned_data.get('email_type') == u'premium':
            template_id = self.cleaned_data.get('premium_email_template')
            if not template_id:
                raise forms.ValidationError("Select premium template.")
            try:
                cet = TemplateDesign.objects.get(pk=int(template_id))
            except TemplateDesign.DoesNotExist:
                raise forms.ValidationError("Invalid template selected.")
            return cet

    def clean_template(self):
        if self.cleaned_data.get('email_type') != u'premium':
            template_id = self.cleaned_data.get('template')
            if not template_id:
                raise forms.ValidationError("Select email template.")
            try:
                cet = CampaignEmailTemplate.objects.get(pk=template_id)
            except CampaignEmailTemplate.DoesNotExist:
                raise forms.ValidationError("Invalid template selected")
            return cet


def get_delay_seconds(schedular_step, schedular_duration):
    schedular_duration = int(schedular_duration)
    if schedular_step == '1':  # Days
        return timedelta(days=schedular_duration).total_seconds()
    elif schedular_step == '2':  # Hours
        return timedelta(hours=schedular_duration).total_seconds()
    elif schedular_step == '3':  # Minutes
        return timedelta(minutes=schedular_duration).total_seconds()


class BaseCampaignForm(forms.ModelForm):
    """
    There are different fields in both campaignFormnew and this forms.
    That forms was written before. Then for update view wrote this.
    But had no time to remove the dulicate fields from this or campaign create
    form will do it sometime

    """

    VOICE_GREETING_TYPE_CHOICES = (
        ('voice_greeting_upload', 'Audio file'),
        ('voice_greeting_record', 'Record own message'),
    )

    email_type = forms.CharField(required=False)
    sample_phone_for_voice = forms.CharField(required=False)
    sample_phone_for_sms = forms.CharField(required=False)
    sample_phone_for_mms = forms.CharField(required=False)
    sample_email_for_email = forms.EmailField(required=False)
    premium_email_template = forms.CharField(required=False)
    voice_greeting_type = forms.ChoiceField(
        choices=VOICE_GREETING_TYPE_CHOICES, required=False)
    voice_greeting_original_recording = forms.CharField(required=False)
    voice_campaign_trigger_date = forms.DateTimeField(required=False)
    mms_campaign_trigger_date = forms.DateTimeField(required=False)
    sms_campaign_trigger_date = forms.DateTimeField(required=False)
    email_campaign_trigger_date = forms.DateTimeField(required=False)

    class Meta:
        model = Campaign
        exclude = ['created_at', 'ended', 'user']

    def check_mms_capability(self, phone):
        numbers = client.incoming_phone_numbers.list(phone_number=phone)
        if numbers:
            number_detail = numbers[0]
            if number_detail.capabilities.get("mms", False):
                return True
        return False

    def clean_sms_greeting(self):
        sms_greeting = self.cleaned_data.get("sms_greeting")
        if not sms_greeting:
            return sms_greeting

        if len(sms_greeting) > 1600:
            raise forms.ValidationError(
                "Please enter no more than 1600 characters in SMS Text")
        return sms_greeting

    def clean_name(self):
        if not self.cleaned_data.get("name"):
            raise forms.ValidationError(
                "Campaign details Invalid , Please Check again")
        return self.cleaned_data["name"]

    def clean_phone(self):
        if not self.cleaned_data.get("phone"):
            raise forms.ValidationError(
                "A phone number is required, Please buy one")
        return self.cleaned_data['phone']

    def clean_voice_greeting_original(self):
        file = self.cleaned_data.get("voice_greeting_original")
        if file:
            ext = os.path.splitext(file.name)[1]
            if not ext.lower() in [".mp3", ".wav", ".m4a"]:
                raise forms.ValidationError(
                    'Invalid audio file. Please upload a valid audio file'
                )
        return file

    def clean_mms_video(self):
        mms_video = self.cleaned_data.get("mms_video")
        if mms_video:
            file_mime = magic.from_buffer(mms_video.file.read(1024), mime=True)
            mms_video.file.seek(0)
            if file_mime not in SUPPORTED_VIDEO_MIME_FORMATS:
                raise forms.ValidationError(
                    "The file you uploaded in not a valid video file.")

            if mms_video.size > 512000:  # 500KB
                raise forms.ValidationError(
                    "The video file must be smaller than 500KB.")

        return mms_video

    def clean_from_email(self):
        from_email = self.cleaned_data.get('from_email')
        if self.data.get("use_email"):
            if not validators.email(from_email):
                raise forms.ValidationError("Enter valid From Email address.")
        return from_email

    def clean_e_greeting_subject(self):
        e_greeting_subject = self.cleaned_data.get('e_greeting_subject')
        if self.data.get("use_email"):
            if not e_greeting_subject:
                raise forms.ValidationError("Email Subject field is required.")
        return e_greeting_subject

    def clean_e_greeting(self):
        e_greeting = self.cleaned_data.get('e_greeting')
        if self.data.get("use_email") == "basic":
            if not e_greeting:
                raise forms.ValidationError("Email Body field is required.")
        return e_greeting

    def clean_template(self):
        template = self.cleaned_data.get('template')
        if self.data.get("use_email") == "basic":
            if not template:
                raise forms.ValidationError("Please select Email tempate.")

        return template

    def clean(self):
        data = self.cleaned_data

        if not data.get("use_mms") and not data.get("use_sms") and not data.get("use_voice") \
            and not data.get("use_email"):
            raise forms.ValidationError(
                'To create campaign you must include at least one  of SMS, MMS, Email or Voice'
            )

        if data.get("use_voice"):
            if not data.get("phone"):
                raise forms.ValidationError(
                    "You have Voice campaign checked and no phone number")
            if not data.get('voice_greeting_original') and not data.get(
                'voice_greeting_original_recording') and not data.get("greeting_text"):
                raise forms.ValidationError(
                    "You have Voice campaign checked and no Audio or voice text")

        if data.get("use_email"):
            email_type = data.get('email_type')
            if email_type:
                if email_type == 'basic':
                    if not data.get("company"):
                        raise forms.ValidationError("Enter Company Name.")
                else:
                    if email_type == 'premium' and not data.get('premium_email_template'):
                        raise forms.ValidationError("Please select Premium template")
            else:
                raise forms.ValidationError("Please select email type")
        if data.get("use_sms"):
            if not data.get("phone") or not data.get("sms_greeting") or (
                data.get("sms_greeting") and len(data.get("sms_greeting")) > 1600):
                raise forms.ValidationError(
                    """To use SMS campaign Please enter a valid phone number, SMS Text not more than 1600 characters""")

        if data.get("use_mms"):
            phone = data.get("phone")
            if not self.check_mms_capability(phone):
                raise forms.ValidationError(
                    "The number you chose is not MMS enabled, MMS is available only in US and Canada numbers")
        return self.cleaned_data

    def calculate_response_delay(self, campaign, commit=False):
        # Calulcate the response delay in seconds
        for data in step_duration_date:
            schedular_step, schedular_duration, campaign_trigger_date, delay = data
            schedular_step = self.cleaned_data.get(schedular_step)
            schedular_duration = self.cleaned_data.get(schedular_duration)
            trigger_date = self.cleaned_data.get(campaign_trigger_date)
            if schedular_step != "0" and (schedular_duration or trigger_date):
                if trigger_date:
                    setattr(campaign, campaign_trigger_date, remove_time_zone(trigger_date))
                else:
                    setattr(campaign, delay, get_delay_seconds(schedular_step, schedular_duration) or 0)
                    setattr(campaign, campaign_trigger_date, None)

        if commit:
            campaign.save()
        return campaign


class CampaignFormNew(BaseCampaignForm):
    """ use these fields for schedule and other things which are not in model"""
    voice_campaign = forms.CharField(required=False)

    voice_schedular_step = forms.CharField(required=False)
    voice_schedular_duration = forms.CharField(required=False)

    sms_schedular_step = forms.CharField(required=False)
    sms_schedular_duration = forms.CharField(required=False)

    email_schedular_step = forms.CharField(required=False)
    email_schedular_duration = forms.CharField(required=False)

    mms_schedular_step = forms.CharField(required=False)
    mms_schedular_duration = forms.CharField(required=False)

    sample_phone = forms.CharField(required=False)
    sample_sms = forms.CharField(required=False)
    sample_mms = forms.CharField(required=False)
    sample_email = forms.EmailField(required=False)

    class Meta:
        model = Campaign

        exclude = ['created_at', 'ended', 'user']

    def save(self, commit=False, *args, **kwargs):
        campaign = super(CampaignFormNew, self).save(commit=False, *args, **kwargs)
        return super(CampaignFormNew, self).calculate_response_delay(campaign, commit=False)


class CampaignUpdateForm(BaseCampaignForm):
    voice_schedular_step = forms.CharField(required=False)
    voice_schedular_duration = forms.CharField(required=False)

    sms_schedular_step = forms.CharField(required=False)
    sms_schedular_duration = forms.CharField(required=False)

    email_schedular_step = forms.CharField(required=False)
    email_schedular_duration = forms.CharField(required=False)
    mms_schedular_step = forms.CharField(required=False)
    mms_schedular_duration = forms.CharField(required=False)

    def save(self, commit=False, *args, **kwargs):
        campaign = super(CampaignUpdateForm, self).save(commit=False, *args, **kwargs)
        return super(CampaignUpdateForm, self).calculate_response_delay(campaign, commit=True)

    class Meta:
        model = Campaign
        exclude = ['created_at', 'active', 'ended', 'voice_greeting_converted',
                   'user', 'start_at']


class FollowupCampaignBaseForm(forms.ModelForm):
    pass
    # sample_phone_for_voice = forms.CharField(required=False)
    # sample_phone_for_sms = forms.CharField(required=False)
    # sample_phone_for_mms = forms.CharField(required=False)
    # sample_email_for_email = forms.EmailField(required=False)
    #
    # VOICE_GREETING_TYPE_CHOICES = (
    #     ('voice_greeting_upload', 'Audio file'),
    #     ('voice_greeting_record', 'Record own message'),
    # )
    #
    # voice_greeting_type = forms.ChoiceField(
    #     choices=VOICE_GREETING_TYPE_CHOICES, required=False)
    # voice_greeting_original_recording = forms.CharField(required=False)
    #
    # class Meta:
    #     model = FUCampaign
    #     exclude = ['created_at', 'ended', 'user']
    #
    # def __init__(self, *args, **kwargs):
    #     self.parent_campaign = kwargs.pop('parent_campaign', None)
    #     super(FollowupCampaignBaseForm, self).__init__(*args, **kwargs)
    #
    # def check_mms_capability(self, phone):
    #     numbers = client.incoming_phone_numbers.list(phone_number=phone)
    #     if numbers:
    #         number_detail = numbers[0]
    #         if number_detail.capabilities.get("mms", False):
    #             return True
    #     return False
    #
    # def clean_sms_text(self):
    #
    #     if self.cleaned_data['sms_text'] and len(self.cleaned_data['sms_text']) > 1600:
    #         raise forms.ValidationError(
    #             "Please enter no more than 1600 characters in SMS Text")
    #     return self.cleaned_data['sms_text']


class FollowUpCampaignForm(FollowupCampaignBaseForm):
    pass
    # schedule = forms.CharField()
    # sp_date = forms.CharField(required=False)
    # sp_date_tz = forms.ChoiceField(required=False, choices=TIMEZONE_CHOICES,
    #                                label='Choose Timezone', help_text='Choose Timezone to be used by this Campaign')
    # mms_images = forms.ImageField(
    #     required=False, widget=forms.FileInput(attrs={"multiple": True}))
    # email_attachments = forms.FileField(required=False)
    # recur_duration = forms.IntegerField(
    #     required=False, widget=forms.NumberInput(attrs={'placeholder': 'e.g. 2'}))
    # recur_step = forms.ChoiceField(required=False, choices=DURATION_CHOICES)
    #
    # send_at = forms.IntegerField(
    #     required=False, widget=forms.NumberInput(attrs={'placeholder': 'e.g. 2'}))
    #
    # e_greeting_subject = forms.CharField(required=False)
    # e_greeting = forms.CharField(required=False)
    #
    # class Meta:
    #     model = FUCampaign
    #
    #     exclude = ['user' 'att3', 'att4', 'att5', 'att6', 'date_created',
    #                'last_updated', 'sent', 'sent_to', "user",]
    #
    #     error_messages = {
    #         'name': {
    #             'required': "Name field is required.",
    #         },
    #         'duration': {
    #             'required': "Duration field is required.",
    #         },
    #         'type': {
    #             'required': "Campaign Type field is required.",
    #         },
    #         'sequence': {
    #             'required': "Sequence field is required.",
    #         },
    #     }
    #
    # def __init__(self, *args, **kwargs):
    #     super(FollowUpCampaignForm, self).__init__(*args, **kwargs)
    #
    #     # TODO: This naming trickery is very a bad thing, very inconsistent.
    #     self.fields['recur_step'].initial = self.instance.duration
    #     self.fields['recur_duration'].initial = self.instance.send_at
    #
    #     if self.instance.sp_date and self.instance.sp_date_tz:
    #         self.fields['sp_date'].initial = pendulum.timezone(
    #             self.instance.sp_date_tz).normalize(self.instance.sp_date)
    #         self.fields[
    #             'sp_date_tz'].initial = self.instance.sp_date.tzinfo.zone
    #
    # def clean_voice_original(self):
    #     file = self.cleaned_data.get("voice_original")
    #     if file:
    #         ext = os.path.splitext(file.name)[1]
    #         if not ext.lower() in [".mp3", ".wav", ".m4a"]:
    #             raise forms.ValidationError(
    #                 'Invalid audio file. Please upload a valid audio file'
    #             )
    #     return file
    #
    # def clean_sequence(self):
    #     if not self.cleaned_data['sequence']:
    #         return 0
    #     return self.cleaned_data['sequence']
    #
    # def clean_schedule(self):
    #     if not self.cleaned_data['schedule'] or not self.cleaned_data['schedule'] in ['1', '2', '3', '4', '5']:
    #         raise forms.ValidationError("Please chose a valid schedule")
    #     return self.cleaned_data['schedule']
    #
    # def clean(self):
    #     data = super(FollowUpCampaignForm, self).clean()
    #     sp_date = data.get('sp_date')
    #     self.cleaned_data['sp_date'] = None
    #     if not any([data.get("send_sms"), data.get("send_email"), data.get("send_mms"), data.get("send_voice")]):
    #         raise forms.ValidationError(
    #             "To create campaign you must include at least one  of SMS, MMS, Email,Voice")
    #
    #     if data.get('send_voice'):
    #         if not data.get('voice_original') and not data.get(
    #                 'voice_greeting_original_recording') and not data.get('voice_text'):
    #             raise forms.ValidationError(
    #                 "You have Voice campaign checked and no Audio or voice text")
    #
    #     if data.get('send_email'):
    #         if not all([data.get('from_email'), data.get('e_greeting'),
    #                     data.get('e_greeting_subject'), data.get('template')]):
    #             # if not data.get('from_email') or not data.get('email_body')
    #             # or not data.get('email_subject') or not data.get('template'):
    #             raise forms.ValidationError(
    #                 "To start Email Campaign From Email, Email Body, Email Subject and Template are required")
    #
    #     if data.get('send_sms') and not data.get('sms_text'):
    #         raise forms.ValidationError(
    #             "You have SMS  campaign checked and no SMS Text")
    #
    #     if data.get('schedule') == '2':
    #         timezone = data.get('sp_date_tz', None)
    #
    #         if not sp_date or not timezone:
    #             raise forms.ValidationError(
    #                 "You chose specific date and time please choose Timezone and date time")
    #         sp_date = datetime.strptime(sp_date, '%d %B %Y - %I:%M %p')
    #         sp_date = pendulum.timezone(timezone).convert(sp_date)
    #         self.cleaned_data['sp_date'] = sp_date
    #
    #     if data.get('schedule') == '4' and not data.get('recur_step'):
    #         raise forms.ValidationError(
    #             "You chose recur schedule, please enter recur step")
    #     if data.get('schedule') == '4' and not data.get('recur_duration'):
    #         raise forms.ValidationError(
    #             "You chose recur schedule, please enter the number of hours or days")
    #
    #     elif data.get('schedule') == '5' and not data.get('send_at'):
    #         raise forms.ValidationError(
    #             "You chose custom schedule, please choose duration")
    #
    #     # ---- validate same-schedule followups (& parent_campaign) ----
    #     # TODO: do the same for edit-campaign
    #     parent_campaign = self.instance.campaign or self.parent_campaign
    #     fu_query = FUCampaign.objects.filter(campaign=parent_campaign)
    #     if self.instance:  # edit Fu
    #         fu_query = fu_query.exclude(pk=self.instance.pk)  # exclude self
    #
    #     schedule = data.get('schedule')
    #
    #     # 1: Immediately
    #     if schedule == '1':
    #         if data.get("send_email") and fu_query.filter(send_email=True, onleadcapture=True).exists():
    #             raise forms.ValidationError(
    #                 "There is already another follow-up action for this campaign which sends an email immediately on lead capture.")
    #
    #         if data.get("send_sms") and fu_query.filter(send_sms=True, onleadcapture=True).exists():
    #             raise forms.ValidationError(
    #                 "There is already another follow-up action for this campaign which sends an SMS immediately on lead capture.")
    #
    #         if data.get("send_mms") and fu_query.filter(send_mms=True, onleadcapture=True).exists():
    #             raise forms.ValidationError(
    #                 "There is already another follow-up action for this campaign which sends an MMS immediately on lead capture.")
    #
    #         if data.get("send_voice") and fu_query.filter(send_voice=True, onleadcapture=True).exists():
    #             raise forms.ValidationError(
    #                 "There is already another follow-up action for this campaign which makes a phone call immediately on lead capture.")
    #
    #         if data.get("send_email") and parent_campaign.use_email and parent_campaign.email_delay == 0:
    #             raise forms.ValidationError(
    #                 "The campaign already sends an email immediately on lead capture.")
    #
    #         if data.get("send_sms") and parent_campaign.use_sms and parent_campaign.sms_delay == 0:
    #             raise forms.ValidationError(
    #                 "The campaign already sends an SMS immediately on lead capture.")
    #
    #         if data.get("send_mms") and parent_campaign.use_mms and parent_campaign.mms_delay == 0:
    #             raise forms.ValidationError(
    #                 "The campaign already sends an MMS immediately on lead capture.")
    #
    #         if data.get("send_voice") and parent_campaign.use_voice and parent_campaign.voice_delay == 0:
    #             raise forms.ValidationError(
    #                 "The campaign already makes a phone call immediately on lead capture.")
    #
    #     # 2: Specific date : 'sp_date'
    #     if schedule == '2':
    #
    #         if data.get("send_email") and fu_query.filter(send_email=True, specific=True, sp_date=sp_date).exists():
    #             raise forms.ValidationError(
    #                 "There is already another follow-up action for this campaign which sends an email on %s." % sp_date)
    #
    #         if data.get("send_sms") and fu_query.filter(send_sms=True, specific=True, sp_date=sp_date).exists():
    #             raise forms.ValidationError(
    #                 "There is already another follow-up action for this campaign which sends an SMS on %s." % sp_date)
    #
    #         if data.get("send_mms") and fu_query.filter(send_mms=True, specific=True, sp_date=sp_date).exists():
    #             raise forms.ValidationError(
    #                 "There is already another follow-up action for this campaign which sends an MMS on %s." % sp_date)
    #
    #         if data.get("send_voice") and fu_query.filter(send_voice=True, specific=True, sp_date=sp_date).exists():
    #             raise forms.ValidationError(
    #                 "There is already another follow-up action for this campaign which makes a phone call on %s." %
    #                 sp_date)
    #
    #     # 3: Immediately existing
    #     if schedule == '3':
    #         if data.get("send_email") and fu_query.filter(send_email=True, now4leads=True).exists():
    #             raise forms.ValidationError(
    #                 "There is already another follow-up action for this campaign which sends an email immediately for existing leads.")
    #
    #         if data.get("send_sms") and fu_query.filter(send_sms=True, now4leads=True).exists():
    #             raise forms.ValidationError(
    #                 "There is already another follow-up action for this campaign which sends an SMS immediately for existing leads.")
    #
    #         if data.get("send_mms") and fu_query.filter(send_mms=True, now4leads=True).exists():
    #             raise forms.ValidationError(
    #                 "There is already another follow-up action for this campaign which sends an MMS immediately for existing leads.")
    #
    #         if data.get("send_voice") and fu_query.filter(send_voice=True, now4leads=True).exists():
    #             raise forms.ValidationError(
    #                 "There is already another follow-up action for this campaign which makes a phone call immediately for existing leads.")
    #
    #         if data.get("send_email") and parent_campaign.use_email and parent_campaign.email_delay == 0:
    #             raise forms.ValidationError(
    #                 "The campaign already sends an email immediately on lead capture.")
    #
    #         if data.get("send_sms") and parent_campaign.use_sms and parent_campaign.sms_delay == 0:
    #             raise forms.ValidationError(
    #                 "The campaign already sends an SMS immediately on lead capture.")
    #
    #         if data.get("send_mms") and parent_campaign.use_mms and parent_campaign.mms_delay == 0:
    #             raise forms.ValidationError(
    #                 "The campaign already sends an MMS immediately on lead capture.")
    #
    #         if data.get("send_voice") and parent_campaign.use_voice and parent_campaign.voice_delay == 0:
    #             raise forms.ValidationError(
    #                 "The campaign already makes a phone call immediately on lead capture.")
    #
    #     # 4: Recurring: 'recur_duration', 'recur_step'
    #     if schedule == '4':
    #         send_at = data.get('recur_duration', None)
    #         duration = data.get('recur_step', None)
    #
    #         if data.get("send_email") and fu_query.filter(
    #                 send_email=True, recur=True, send_at=send_at, duration=duration).exists():
    #             raise forms.ValidationError(
    #                 "There is already another follow-up action for this campaign which sends an email for every %s %s(s)" %
    #                 (send_at, {
    #                     '1': 'Day', '2': 'Hour', '3': 'minutes'}[duration]))
    #
    #         if data.get("send_sms") and fu_query.filter(
    #                 send_sms=True, recur=True, send_at=send_at, duration=duration).exists():
    #             raise forms.ValidationError(
    #                 "There is already another follow-up action for this campaign which sends an SMS for every %s %s(s)" %
    #                 (send_at, {
    #                     '1': 'Day', '2': 'Hour', '3': 'minutes'}[duration]))
    #
    #         if data.get("send_mms") and fu_query.filter(
    #                 send_mms=True, recur=True, send_at=send_at, duration=duration).exists():
    #             raise forms.ValidationError(
    #                 "There is already another follow-up action for this campaign which sends an MMS for every %s %s(s)" %
    #                 (send_at, {
    #                     '1': 'Day', '2': 'Hour', '3': 'minutes'}[duration]))
    #
    #         if data.get("send_voice") and fu_query.filter(
    #                 send_voice=True, recur=True, send_at=send_at, duration=duration).exists():
    #             raise forms.ValidationError(
    #                 "There is already another follow-up action for this campaign which makes a phone for every %s %s(s)" %
    #                 (send_at, {
    #                     '1': 'Day', '2': 'Hour', '3': 'minutes'}[duration]))
    #
    #     # 5: custom period: 'duration', 'send_at'
    #     if schedule == '5':
    #         send_at = data.get('send_at', None)
    #         duration = data.get('duration', None)
    #
    #         if data.get("send_email") and fu_query.filter(
    #                 send_email=True, custom=True, send_at=send_at, duration=duration).exists():
    #             raise forms.ValidationError(
    #                 "There is already another follow-up action for this campaign which sends an email %s %s(s) after lead capture." %
    #                 (send_at, {
    #                     '1': 'Day', '2': 'Hour', '3': 'minutes'}[duration]))
    #
    #         if data.get("send_sms") and fu_query.filter(
    #                 send_sms=True, custom=True, send_at=send_at, duration=duration).exists():
    #             raise forms.ValidationError(
    #                 "There is already another follow-up action for this campaign which sends an SMS %s %s(s) after lead capture." %
    #                 (send_at, {
    #                     '1': 'Day', '2': 'Hour', '3': 'minutes'}[duration]))
    #
    #         if data.get("send_mms") and fu_query.filter(
    #                 send_mms=True, custom=True, send_at=send_at, duration=duration).exists():
    #             raise forms.ValidationError(
    #                 "There is already another follow-up action for this campaign which sends an MMS %s %s(s) after lead capture." %
    #                 (send_at, {
    #                     '1': 'Day', '2': 'Hour', '3': 'minutes'}[duration]))
    #
    #         if data.get("send_voice") and fu_query.filter(
    #                 send_voice=True, custom=True, send_at=send_at, duration=duration).exists():
    #             raise forms.ValidationError(
    #                 "There is already another follow-up action for this campaign which makes a phone %s %s(s) after lead capture." %
    #                 (send_at, {
    #                     '1': 'Day', '2': 'Hour', '3': 'minutes'}[duration]))
    #
    #         delay_seconds = get_delay_seconds(duration, send_at)
    #         if data.get("send_email") and parent_campaign.use_email and parent_campaign.email_delay == delay_seconds:
    #             raise forms.ValidationError(
    #                 "The campaign already sends an email %s after lead capture." % timedelta(seconds=delay_seconds))
    #
    #         if data.get("send_sms") and parent_campaign.use_sms and parent_campaign.sms_delay == delay_seconds:
    #             raise forms.ValidationError(
    #                 "The campaign already sends an SMS %s after lead capture." % timedelta(seconds=delay_seconds))
    #
    #         if data.get("send_mms") and parent_campaign.use_mms and parent_campaign.mms_delay == delay_seconds:
    #             raise forms.ValidationError(
    #                 "The campaign already sends an MMS %s after lead capture." % timedelta(seconds=delay_seconds))
    #
    #         if data.get("send_voice") and parent_campaign.use_voice and parent_campaign.voice_delay == delay_seconds:
    #             raise forms.ValidationError(
    #                 "The campaign already makes a phone call %s after lead capture." % timedelta(seconds=delay_seconds))
    #
    #     return self.cleaned_data
CampaignMMSImagesFormset = modelformset_factory(
    CampaignMMSImages, fields=("image",), max_num=10, extra=2)


class TestSampleMMSForm(forms.Form):
    phone = forms.CharField()
    mms_greeting_text = forms.CharField()
    sample_phone_for_mms = forms.CharField()
    mms_image1 = forms.ImageField(required=True)
    mms_image2 = forms.ImageField(required=False)
    mms_video = forms.FileField(required=False)

    def __init__(self, *args, **kwargs):
        edit_mode = kwargs.pop('edit_mode', None)
        super(TestSampleMMSForm, self).__init__(*args, **kwargs)

        # mms_image is only required when creating a new (fu)campaign.
        # For exisitng (fu)campaigns, it must be optional
        # (the filefield is always empty on edit)
        if edit_mode:
            self.fields['mms_image1'].required = False

    def clean_phone(self):
        phone = self.cleaned_data['phone']
        try:
            twilio_number = TwilioNumber.objects.get(pk=int(phone))
        except TwilioNumber.DoesNotExist:
            return forms.ValidationError("Please select a valid phone number")
        if not twilio_number.mms_enabled:
            raise forms.ValidationError(
                "MMS capability is allowed for US and Canada numbers")
        return self.cleaned_data['phone']

    def clean_mms_video(self):
        mms_video = self.cleaned_data.get("mms_video")
        if mms_video:
            file_mime = magic.from_buffer(mms_video.file.read(1024), mime=True)
            mms_video.file.seek(0)
            if file_mime not in SUPPORTED_VIDEO_MIME_FORMATS:
                raise forms.ValidationError(
                    "The file you uploaded in not a valid video file.")

            if mms_video._size > 512000:  # 500KB
                raise forms.ValidationError(
                    "The video file must be smaller than 500KB.")

        return mms_video


class EmailAttachmentsForm(forms.ModelForm):
    number = forms.IntegerField(widget=forms.HiddenInput())

    class Meta:
        model = TemplateImages

        fields = ['image', 'description', 'url', 'attachment', 'number']

        error_messages = {
            "description": {"required": "Description texts are required"}
        }

    def clean(self):
        data = self.cleaned_data

        if data.get('image') and data.get('url'):
            raise forms.ValidationError(
                "Only an Image or a URL can be attached")

        if data.get('image') and data.get('attachment'):
            raise forms.ValidationError(
                "Only an Image or a attachment can be attached")
        if data.get('url') and data.get('attachment'):
            raise forms.ValidationError(
                "Only an Image or a attachment can be attached")
        return self.cleaned_data

    def clean_image(self):
        image = self.cleaned_data['image']
        if image and (image._size / (20 * 1024 * 1024)) > 20:
            raise forms.ValidationError("Image size can't be more than 20 mb")
        return self.cleaned_data['image']

    def clean_attachment(self):
        attachment = self.cleaned_data['attachment']
        if attachment and (attachment._size / (20 * 1024 * 1024)) > 20:
            raise forms.ValidationError("Image size can't be more than 20 mb")
        return self.cleaned_data['attachment']


def make_attachment_form(user=None):
    """ Form factor to inject the `user` argument in. Unfortunately there is no
    easy way in django 1.6 to pass this from the formset."""

    class AttachmentsForm(forms.ModelForm):
        TYPE_CHOICES = (
            ('image', 'Image'),
            ('audio', 'Audio'),
            ('video', 'Video'),
            ('attachment', 'Attachment'),
            ('url', 'Url'),
        )

        # required=False fro compatibility issues only
        type = forms.ChoiceField(choices=TYPE_CHOICES, required=False,
                                 widget=forms.Select(attrs={
                                     "class": "form-control type_selector"}))

        number = forms.IntegerField(
            initial=1, widget=forms.HiddenInput(), required=False)
        description = forms.CharField(
            required=False, widget=forms.TextInput(attrs={"class": "form-control"}))

        class Meta:
            model = TemplateImages
            fields = ('digital_image', 'digital_audio', 'digital_video',
                      'digital_attachment', 'url', 'description')

        def __init__(self, *args, **kwargs):
            super(AttachmentsForm, self).__init__(*args, **kwargs)

            # widget class overrides
            for field_name in ('digital_image', 'digital_audio', 'digital_video', 'digital_attachment'):
                self.fields[field_name].widget = forms.Select(
                    attrs={"class": "form-control"})
            self.fields['url'].widget = forms.TextInput(
                attrs={"class": "form-control"})

            # queryset overrides
            for field_name in ('digital_image', 'digital_audio', 'digital_video', 'digital_attachment'):
                self.fields[field_name].queryset = self.fields[
                    field_name].queryset.filter(user=user)

            if self.instance:
                if self.instance.digital_image:
                    self.fields['type'].initial = 'image'
                elif self.instance.digital_audio:
                    self.fields['type'].initial = 'audio'
                elif self.instance.digital_video:
                    self.fields['type'].initial = 'video'
                elif self.instance.digital_attachment:
                    self.fields['type'].initial = 'attachment'
                elif self.instance.url:
                    self.fields['type'].initial = 'url'

        def clean(self):
            data = self.cleaned_data

            if (data.get('url') or data.get('digital_video') or data.get('digital_image') or data.get(
                'digital_audio') or data.get('digital_attachment')) and not data.get("description"):
                raise forms.ValidationError(
                    "Please Enter the display Text for select assets")

            return self.cleaned_data

        def save(self, commit=True):
            obj = super(AttachmentsForm, self).save(commit=False)

            obj.user = user

            obj.digital_image = None
            obj.digital_audio = None
            obj.digital_video = None
            obj.digital_attachment = None
            obj.url = None

            chosen_type = self.cleaned_data.get('type')
            if chosen_type == 'image':
                obj.digital_image = self.cleaned_data.get('digital_image')

            elif chosen_type == 'audio':
                obj.digital_audio = self.cleaned_data.get('digital_audio')

            elif chosen_type == 'video':
                obj.digital_video = self.cleaned_data.get('digital_video')

            elif chosen_type == 'attachment':
                obj.digital_attachment = self.cleaned_data.get(
                    'digital_attachment')

            elif chosen_type == 'url':
                obj.url = self.cleaned_data.get('url')

            obj.save()
            return obj

    return AttachmentsForm


def attachment_formset_factory(user, parent_class=Campaign):
    """ Builds an inline formset for Campaign by default, but the parent class
    can be specified i.e for FUCampaign """

    return inlineformset_factory(
        parent_class,
        TemplateImages,
        form=make_attachment_form(user),
        extra=0,
    )


class SupportEmailForm(forms.Form):
    subject = forms.ChoiceField(choices=EmailConstatnt.EMAIL_SUBJECTS)
    message = forms.CharField(widget=forms.Textarea)

    def send_email(self, sender):
        send_templated_email(
            subject=self.cleaned_data.get('subject'),
            email_template_name='ccc/campaigns/email/support.html',
            sender=sender.email,
            recipients=settings.ADMINS,
            email_context={
                'body': self.cleaned_data.get('message'),
                'name': sender.username,
            }
        )


class CampaignEmbedUpdateForm(forms.ModelForm):
    class Meta:
        model = Campaign
        fields = ('embed_form_success', 'embed_form_last_name',
                  'embed_form_email', 'embed_form_phone')

    def clean(self):
        if not self.cleaned_data.get('embed_form_email') and not self.cleaned_data.get('embed_form_phone'):
            msg = 'Either email or phone number is mandatory.'
            self._errors["embed_form_email"] = self.error_class([msg])
            self._errors["embed_form_phone"] = self.error_class([msg])
        return self.cleaned_data


class CampaignSignupExtraFieldForm(forms.ModelForm):
    name = forms.CharField(label='click here to name this field')

    class Meta:
        model = CampaignSignupExtraField
        fields = ('name', 'campaign',)


CampaignSignupExtraFieldFormSet = inlineformset_factory(
    Campaign, CampaignSignupExtraField, form=CampaignSignupExtraFieldForm,
    extra=0)


class AssignContactsToCampaignForm(CampaignAndGroupMixin, forms.Form):
    campaigns = forms.ModelMultipleChoiceField(Campaign.objects.none())
    groups = forms.ModelMultipleChoiceField(ContactGroup.objects.none())


class AssignKwywordsToCampaignForm(forms.Form):
    campaigns = forms.ModelChoiceField(
        Campaign.objects.none(), empty_label=None,
        widget=forms.Select(attrs={
            'class': 'form-control chosen-select select2'}))

    keywords = forms.CharField(
        max_length=1000, required=True,
        help_text="Campaign keywords separated by comma(,)",
        widget=forms.TextInput(attrs={'class': 'form-control'}))

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        campaign_id = kwargs.pop('campaign_id')
        super(AssignKwywordsToCampaignForm, self).__init__(*args, **kwargs)
        self.fields['campaigns'].queryset = Campaign.objects.filter(
            active=True, user=user, id=campaign_id)

    def clean_keywords(self):
        keywords = self.cleaned_data.get("keywords", '').split(",")
        if not keywords:
            return self.cleaned_data.get("keywords", '')
        keywords_list = [str(x).lower().strip() for x in keywords]

        campaign = self.cleaned_data.get("campaigns")
        campaigns = Campaign.objects.filter(phone=campaign.phone, active=True)
        maaped_keywords = MappedKeywords.objects.filter(
            campaign__in=campaigns,
            is_active=True).exclude(campaign=campaign)

        for obj in maaped_keywords:
            if str(obj.keyword).lower() in keywords_list:
                raise forms.ValidationError(
                    "{} is already mapped with {} campaign".format(obj.keyword, obj.campaign))

        return self.cleaned_data.get("keywords", '')

    def save(self):
        campaign = self.cleaned_data.get("campaigns")
        keywords = self.cleaned_data.get("keywords")
        if keywords:
            mapped_keywords = keywords.split(",")
            MappedKeywords.objects.filter(
                campaign=campaign).update(is_active=False)
            for keyword in mapped_keywords:
                keyword = keyword.strip()
                key_obj, created = MappedKeywords.objects.get_or_create(
                    campaign=campaign,
                    keyword=keyword)
                key_obj.is_active = True
                key_obj.save()
