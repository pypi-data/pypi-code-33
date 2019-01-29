import logging
import os
from io import BytesIO
from tempfile import NamedTemporaryFile

from adminsortable.models import SortableMixin
from annoying.fields import JSONField
from django.apps import apps as django_apps
from django.contrib.sites.models import Site
from django.core.files.base import ContentFile
from django.db.models.signals import post_save, pre_delete
from django.template import loader
from django.template.defaultfilters import slugify
from phonenumber_field.modelfields import PhoneNumberField
from premailer import transform
from screamshot.utils import casperjs_capture
from simple_history.models import HistoricalRecords
from twilio.base.exceptions import TwilioRestException
from twilio.rest import Client as TwilioRestClient

from ccc.campaigns.signals import (fu_campaign_pre_delete, omms_post_save,
                                   campaign_followup_post_save, signal_send_sms)
from ccc.constants import (DURATION_CHOICES, EMIAL_TYPE, LOGO_PLACE,
                           TIMEZONE_CHOICES)
from ccc.contacts.models import ContactCheckin
from ccc.digital_assets.models import *
from ccc.ocr.models import ImageContacts
from ccc.packages.models import TwilioNumber
from ccc.survey.models import Survey
from ccc.teams.models import Team
from ccc.utils.utils import validate_media_absolute_url

logger = logging.getLogger(__name__)


class RedirectNumber(models.Model):
    user = models.ForeignKey(settings.ACCOUNT_USER_PROXY_MODEL, on_delete=models.CASCADE)
    from_no = models.ForeignKey(TwilioNumber, blank=True, null=True, on_delete=models.SET_NULL)
    to_no = models.CharField(max_length=255, blank=True, null=True)
    verified = models.BooleanField(
        default=False, help_text='If None Twilio Number is Used')
    code = models.CharField(max_length=255, blank=True, null=True)
    date_created = models.DateTimeField(
        auto_now_add=True, blank=True, null=True)
    last_updated = models.DateTimeField(auto_now=True, blank=True, null=True)

    def __str__(self):
        return '%s -> %s (%s)' % (self.from_no, self.to_no, self.user)


class Notify(models.Model):
    NOTIFICATION_DURATION = (
        (0, "Immediately"),
        (1, "Once Daily")
    )
    user = models.ForeignKey(settings.ACCOUNT_USER_PROXY_MODEL, on_delete=models.CASCADE)
    phone = models.CharField(max_length=255, blank=True, null=True)
    call = models.BooleanField(default=False)
    sms = models.BooleanField(default=False)
    email = models.BooleanField(default=False)
    mail = models.CharField(max_length=255, blank=True, null=True)
    duration = models.IntegerField(default=0, choices=NOTIFICATION_DURATION)
    date_created = models.DateTimeField(
        auto_now_add=True, blank=True, null=True)
    last_updated = models.DateTimeField(auto_now=True, blank=True, null=True)


class TemplateType(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(null=True, blank=True)

    def _get_unique_slug(self):
        slug = slugify(self.title)
        unique_slug = slug
        num = 1
        while TemplateType.objects.filter(slug=unique_slug).exists():
            unique_slug = '{}-{}'.format(slug, num)
            num += 1
        return unique_slug

    #    def save(self, *args, **kwargs):
    #        # Temporary Fix
    #        self.slug = slugify(self.name)
    #         self.slug = "{}".format(self.name).replace(" ", "-")
    #        super(TemplateType, self).save(*args, **kwargs)

    def __str__(self):
        return self.name


class CampaignEmailTemplate(SortableMixin, models.Model):
    """
        Model tp store email campaign template data
    """
    template_type = models.ForeignKey(TemplateType, null=True, on_delete=models.SET_NULL)
    name = models.CharField(max_length=50, blank=True, null=True)
    email_body = models.TextField(blank=True, null=True)
    description = models.CharField(max_length=255, blank=True, null=True)
    image = models.ImageField(upload_to='campaigns/email/images')
    user = models.ForeignKey(settings.ACCOUNT_USER_PROXY_MODEL, on_delete=models.CASCADE)
    private_template = models.BooleanField(default=False)
    visible_to = models.ManyToManyField(settings.ACCOUNT_USER_PROXY_MODEL, related_name="visible_templates", blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    number_of_max_uploads = models.IntegerField(
        null=True, blank=True, default=0)

    # define the field the model should be ordered by
    order = models.PositiveIntegerField(
        default=0, editable=False, db_index=True)

    class Meta:
        db_table = 'etemplates'
        ordering = ('order', 'template_type__name', 'name')

    def __str__(self):
        return self.name

    def update_thumbnail(self):
        """
        For updating thumbnail automatically with casperjs
        Not called, only for manual use yet.

        Needs CasperJS to be installed on the system:
        `npm install casperjs` or `sudo npm install -g casperjs`
        """

        stream = self.render_thumbnail()
        self.image.save('thumbnail_%s.png' %
                        self.pk, ContentFile(stream.getvalue()))
        self.save()

    def render_thumbnail(self):
        # TODO: refactor/reuse with preview & real-rendering
        objects = []

        if len(objects) < self.number_of_max_uploads:
            for o in range(len(objects), self.number_of_max_uploads):
                objects.append({})

        objects = objects[:self.number_of_max_uploads]

        body = "<p>Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>"

        context = {
            'body': body,
            'contact_fname': '<<First Name>>',
            'e_greeting': body,
            'objects': objects,
            'hostname': Site.objects.get_current().domain,
        }

        context['protocol'] = 'http://'

        context['company'] = 'Company name'

        context['username'] = "<<Contact name>>"

        tpl = loader.get_template(self.template.path)

        img_data = "data:image;base64,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%0A"
        context['logo'] = img_data  # serve as base64 image

        template_content = transform(tpl.render(context))

        with NamedTemporaryFile(suffix='.html') as render_file:
            render_file.write(template_content.encode('utf-8'))
            render_file.seek(0)

            stream = BytesIO()
            casperjs_capture(
                stream,
                url='file://%s' % os.path.abspath(render_file.name),
                width=800,
                height=600,
                size='400x300',
            )

        return stream


class Campaign(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)
    ended = models.DateTimeField(blank=True, null=True)

    from_email = models.CharField(max_length=255, blank=True, null=True)
    company = models.CharField(max_length=255, blank=True, null=True)
    logo = models.FileField(upload_to='campaigns/attachments', blank=True, null=True)
    logo_place = models.CharField(max_length=25, choices=LOGO_PLACE, null=True, blank=True, default="top-left")
    user = models.ForeignKey(settings.ACCOUNT_USER_PROXY_MODEL, on_delete=models.CASCADE)
    phone = models.ForeignKey(TwilioNumber, blank=True, null=True, on_delete=models.SET_NULL)
    redirect_no = models.ForeignKey(RedirectNumber, blank=True, null=True, on_delete=models.SET_NULL)
    start_at = models.DateTimeField(blank=True, null=True)
    team = models.ForeignKey(Team, blank=True, null=True, on_delete=models.SET_NULL)
    use_email = models.BooleanField(default=False)
    use_voice = models.BooleanField(default=False)
    use_mms = models.BooleanField(default=False)
    use_sms = models.BooleanField(default=False)

    voice_delay = models.IntegerField(default=0, help_text="In seconds", blank=True)
    email_delay = models.IntegerField(default=0, help_text="In seconds", blank=True)
    sms_delay = models.IntegerField(default=0, help_text="In seconds", blank=True)
    mms_delay = models.IntegerField(default=0, help_text="In seconds", blank=True, )
    embed_form_success = models.TextField(blank=True, default='', verbose_name='Success message',
                                          help_text='This message will be displayed upon a successful signup.')
    embed_form_last_name = models.BooleanField(blank=True, default=True)
    embed_form_email = models.BooleanField(blank=True, default=True)
    embed_form_phone = models.BooleanField(blank=True, default=True)
    keyword = models.CharField(max_length=255, blank=True, null=True)
    voice_campaign_trigger_date = models.DateTimeField(blank=True, null=True)
    mms_campaign_trigger_date = models.DateTimeField(blank=True, null=True)
    sms_campaign_trigger_date = models.DateTimeField(blank=True, null=True)
    email_campaign_trigger_date = models.DateTimeField(blank=True, null=True)

    parent_campaign = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)
    is_follow_up = models.BooleanField(default=False)

    history = HistoricalRecords(
        excluded_fields=[
            ContactCheckin.campaign,
            Survey.campaign,
            ImageContacts.campaign,
            "phone",
            "team"])

    def voice(self):
        voice = VoiceCampaign.objects.filter(campaign=self.id).count()
        if voice:
            return voice
        else:
            return 'Not Added'

    def sms(self):
        sms = SMSCampaign.objects.filter(campaign=self.id).count()
        if sms:
            return sms
        else:
            return 'Not Added'

    def mms(self):
        mms = MMSCampaign.objects.filter(campaign=self.id).count()
        if mms:
            return mms
        else:
            return 'Not Added'

    def email(self):
        email = EmailCampaign.objects.filter(campaign=self.id).count()
        if email:
            return email
        else:
            return 'Not Added'

    def __str__(self):
        return self.name

    def get_mms(self):
        return self.mmscampaign_set.first()

    def get_premium_email_template(self):
        """Get premium email template"""
        email_tempalte = self.campaigntemplatedesign_set.filter(template_type='email').first()
        if email_tempalte:
            return email_tempalte.template

    def get_premium_web_template(self):
        """Get premium web template"""
        web_tempalte = self.campaigntemplatedesign_set.filter(template_type='web').first()
        if web_tempalte:
            return web_tempalte.template

    class Meta:
        db_table = 'all_campaigns'
        ordering = ["-created_at"]

    def update_twilio_urls(self):
        if self.phone:
            twilio_number = self.phone
            twilio_number.voice_url = reverse('srm:api_marketing:campaigns:handle-incoming-call')
            twilio_number.sms_url = reverse('srm:api_marketing:campaigns:handle-incoming-sms')
            twilio_number.save()
            # Execute update_twilio_urls async task
            twilio_number.task_update_twilio_urls()

    def reset_twilio_url_to_default(self):
        if self.phone:
            self.phone.idle()


post_save.connect(campaign_followup_post_save, sender=Campaign)


class CampaignChannelModelMixin(models.Model):
    delay_type = models.CharField(max_length=50, blank=True, null=True, choices=DURATION_CHOICES)
    delay_value = models.IntegerField(default=0, null=True, blank=True)
    trigger_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True


class CampaignSignupExtraField(models.Model):
    campaign = models.ForeignKey(Campaign, related_name='signup_extra_fields', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)


class FollowUpDetail(models.Model):
    campaign = models.OneToOneField(Campaign, on_delete=models.CASCADE, null=True, blank=True)
    type = models.CharField(choices=(('1', 'Event'), ('2', 'Marketing'), ('3', 'One Time')),
                            default=1, max_length=1, blank=True)
    ended_at = models.DateTimeField(blank=True, null=True)
    sequence = models.IntegerField(default=0, blank=True)
    # schedule should be one of this
    custom = models.BooleanField(
        default=False,
        help_text='This will be sent to your leads after the duration you specify, relative to their capture '
                  'date and time')
    specific = models.BooleanField(
        default=False,
        help_text='This will be sent on the date and time you specify, to leads in this campaign')
    recur = models.BooleanField(
        default=False,
        help_text='This will be sent periodically in the intervals you specify either day or hours to you existing '
                  'leads at that particular time')
    now4leads = models.BooleanField(
        default=False,
        help_text='This will be sent instantly to all your existing leads'
    )
    onleadcapture = models.BooleanField(
        default=False,
        help_text='When a lead is captured, this will be sent out instantly'
    )
    sp_date = models.DateTimeField(blank=True, null=True, help_text="Specific data")
    sp_date_tz = models.CharField(
        max_length=50,
        choices=TIMEZONE_CHOICES,
        null=True,
        blank=True,
        help_text='Specific date timezone'
    )
    promptly = models.DateTimeField(blank=True, null=True)
    # CUSTOM DURATION days/hours and recur hours days
    custom_delay = models.IntegerField(null=True, blank=True, help_text="This is the delay before sending after the "
                                                                        "lead is captured")
    custom_delay_unit = models.CharField(choices=DURATION_CHOICES, null=True, max_length=1,
                                         blank=True, help_text="This is the unit of the delay before sending after "
                                                               "the lead is captured")
    recur_interval = models.IntegerField(blank=True, null=True, help_text='Send after...')
    recur_interval_unit = models.CharField(choices=DURATION_CHOICES, default=1, max_length=1, blank=True)
    sent = models.BooleanField(default=False)
    sent_to = models.ManyToManyField('contacts.Contact', blank=True, help_text='Sent to contacts...')
    date_created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    history = HistoricalRecords(excluded_fields=[])

    def __str__(self):
        return self.campaign.parent_campaign.name + ' -> ' + self.campaign.name

    # def send_now_for_existing_leads(self):
    #     """
    #     This will be sent fu campaign instantly to all your existing leads, using gcloud task
    #     """
    #     from ccc.campaigns.cloud_tasks import send_follow_campaign_now
    #
    #     if self.now4leads:
    #         send_follow_campaign_now(campaign_id=self.id).execute()

    class Meta:
        verbose_name_plural = 'Follow Up campaigns'
        ordering = ['-date_created']

    def schedule_for_celery(self):
        # TODO #FIXME PENDING PENDING FOR AFTER OF DEMO
        # self.unschedule_from_celery()
        # period = DURATION_MAPPING[self.duration]
        # every = self.send_at
        # self.recurring_celery_task = RuntimePeriodicTask.schedule_every(
        #     'ccc.campaigns.tasks.send_recurring_fu_campaign',
        #     period, every, kwargs=json.dumps({'fu_campaign_pk': self.pk}))
        # self.recurring_celery_task.start()
        # self.save()
        pass

    def unschedule_from_celery(self):
        # TODO #FIXME PENDING PENDING for After of demo
        pass
        # if self.recurring_celery_task:
        #     self.recurring_celery_task.terminate()


pre_delete.connect(fu_campaign_pre_delete, sender=FollowUpDetail)


class EmailCampaign(CampaignChannelModelMixin):
    """
    Model to store campaign team information
    """
    # Email Campaign fields
    """
    Model tp store campaign email
    """
    # Email Campaign fields
    campaign = models.ForeignKey(Campaign, blank=True, null=True, on_delete=models.CASCADE)
    body = models.TextField(blank=True, null=True)
    subject = models.CharField(max_length=255, blank=True, null=True)
    template = models.ForeignKey(CampaignEmailTemplate, blank=True, null=True, on_delete=models.SET_NULL)

    premium_template = models.ForeignKey('template_design.TemplateDesign', blank=True, null=True,
                                         on_delete=models.SET_NULL)

    from_email = models.EmailField(max_length=255, blank=True, null=True)
    att1 = models.FileField(upload_to='campaigns/attachments', blank=True, null=True)
    att2 = models.FileField(upload_to='campaigns/attachments', blank=True, null=True)
    att3 = models.FileField(upload_to='campaigns/attachments', blank=True, null=True)
    att4 = models.FileField(upload_to='campaigns/attachments', blank=True, null=True)
    att5 = models.FileField(upload_to='campaigns/attachments', blank=True, null=True)
    att6 = models.FileField(upload_to='campaigns/attachments', blank=True, null=True)
    user = models.ForeignKey(settings.ACCOUNT_USER_PROXY_MODEL, blank=True, null=True, on_delete=models.SET_NULL)
    # EmailAutoResponder fields
    auto_response = models.BooleanField(default=False)

    send_sample = models.BooleanField(default=False)
    email_for_sample = models.EmailField(max_length=255, blank=True, null=True)
    email_type = models.CharField(max_length=25, choices=EMIAL_TYPE, default='basic')
    date_created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'campaign_email'
        verbose_name = 'Email Campaign'

    def __str__(self):
        if self.campaign:
            return 'email# ' + self.campaign.name
        else:
            return self.subject

    def get_attachments(self):
        attachments = ''

        if self.att1:
            attachments.append(self.att1.url)

        if self.att2:
            attachments.append(self.att2.url)
        if self.att3:
            attachments.append(self.att3.url)
        if self.att4:
            attachments.append(self.att4.url)
        if self.att5:
            attachments.append(self.att5.url)
        if self.att6:
            attachments.append(self.att6.url)

        return attachments


class VoiceCampaign(CampaignChannelModelMixin):
    # Voice Campaign fields
    campaign = models.ForeignKey(Campaign, blank=True, null=True, on_delete=models.CASCADE)
    audio = models.FileField(upload_to='campaigns/voice/', blank=True, null=True, help_text='MP3 formats only')
    voice_to_text = models.TextField(blank=True, null=True)
    voice_greeting_original = models.FileField(upload_to='campaigns/sample_test_voice', blank=True, null=True)
    voice_greeting_converted = models.FileField(upload_to='campaigns/sample_test_voice', blank=True, null=True)
    user = models.ForeignKey(settings.ACCOUNT_USER_PROXY_MODEL, on_delete=models.CASCADE)
    prompt1 = models.BooleanField(default=False)
    prompt2 = models.BooleanField(default=False)
    ended = models.BooleanField(default=True)
    ended_at = models.DateTimeField(blank=True, null=True)
    date_created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'voice_campaigns'

    def __str__(self):
        if self.campaign:
            return 'voice# ' + self.campaign.name
        return 'voice# '


def convert_voice_campaign_audio(sender, instance, created, **kwargs):
    if not instance.voice_greeting_converted and instance.audio:
        from ccc.campaigns.cloud_tasks import voice_campaign_convert_audio
        voice_campaign_convert_audio(voice_campaign_id=instance.id).execute()


post_save.connect(convert_voice_campaign_audio, sender=VoiceCampaign)


class OVoiceCall(models.Model):
    caller_name = models.CharField(max_length=255, null=True, blank=True)
    from_no = models.CharField(max_length=255, null=True, blank=True)
    to = models.CharField(max_length=255, null=True, blank=True)
    time = models.DateTimeField(auto_now_add=True)

    campaign = models.ForeignKey(Campaign, null=True, blank=True, on_delete=models.SET_NULL)

    raw_data = models.TextField(blank=True, null=True)
    record_sid = models.CharField(max_length=255, null=True, blank=True)
    recording = models.FileField(null=True, upload_to='calls/recordings')
    recording_wav = models.FileField(null=True, upload_to='calls/recordings/wav')
    recording_text = models.TextField(blank=True, null=True)
    recording_sentiment_score = models.CharField(max_length=255, null=True, blank=True)
    recording_sentiment_magnitude = models.CharField(max_length=255, null=True, blank=True)
    call_sid = models.CharField(max_length=255, null=True, blank=True)
    from_city = models.CharField(max_length=255, null=True, blank=True)
    from_country = models.CharField(max_length=255, null=True, blank=True)
    duration = models.IntegerField(default=0)
    from_state = models.CharField(max_length=255, null=True, blank=True)
    to_country = models.CharField(max_length=255, null=True, blank=True)
    to_zip = models.CharField(max_length=255, null=True, blank=True)
    from_zip = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(max_length=255, null=True, blank=True)
    price = models.DecimalField(max_digits=9, decimal_places=6, default=0.0)
    forwarded_from = models.CharField(max_length=255, null=True, blank=True)
    start_time = models.CharField(max_length=255, null=True, blank=True)
    end_time = models.CharField(max_length=255, null=True, blank=True)
    charged = models.BooleanField(default=False)
    sent = models.BooleanField(default=False)
    send_at = models.DateTimeField(auto_now=True, blank=True, null=True)
    date_created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    @property
    def campaign_no(self):
        my_campaign = TwilioNumber.objects.filter(twilio_number=self.to)
        if my_campaign:
            myc = VoiceCampaign.objects.filter(campaign_no=my_campaign[0].id)
            if myc:
                return myc[0].name
        else:
            return None

    def __str__(self):
        return self.to

    class Meta:
        db_table = 'sent_voice'


class IVoiceCall(models.Model):
    caller_name = models.CharField(max_length=255, null=True, blank=True)
    from_no = models.CharField(max_length=255, null=True, blank=True)
    to = models.CharField(max_length=255, null=True, blank=True)
    time = models.DateTimeField(auto_now_add=True)
    campaign = models.ForeignKey(Campaign, null=True, blank=True, on_delete=models.SET_NULL)
    raw_data = models.TextField(blank=True, null=True)
    record_sid = models.CharField(max_length=255, null=True, blank=True)
    call_sid = models.CharField(max_length=255, null=True, blank=True)
    from_city = models.CharField(max_length=255, null=True, blank=True)
    from_country = models.CharField(max_length=255, null=True, blank=True)
    duration = models.IntegerField(default=0)
    from_state = models.CharField(max_length=255, null=True, blank=True)
    to_country = models.CharField(max_length=255, null=True, blank=True)
    to_zip = models.CharField(max_length=255, null=True, blank=True)
    from_zip = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(max_length=255, null=True, blank=True)
    price = models.DecimalField(max_digits=9, decimal_places=6, default=0.0)
    forwarded_from = models.CharField(max_length=255, null=True, blank=True)
    start_time = models.CharField(max_length=255, null=True, blank=True)
    end_time = models.CharField(max_length=255, null=True, blank=True)
    recording_url = models.CharField(max_length=255, null=True, blank=True)
    recording_short_url = models.URLField(null=True, blank=True)
    recording_duration = models.CharField(max_length=255, null=True, blank=True)
    recording_sid = models.CharField(max_length=255, null=True, blank=True)

    charged = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    completed = models.BooleanField(default=False)

    def __str__(self):
        return self.from_no

    class Meta:
        db_table = 'incoming_voice'


class SMSCampaign(CampaignChannelModelMixin):
    # SMS Campaign fields
    text = models.CharField(max_length=255, blank=True, null=True)
    campaign = models.ForeignKey(Campaign, blank=True, null=True, on_delete=models.CASCADE)
    sample_no = models.CharField(max_length=255, blank=True, null=True)
    ended_at = models.DateTimeField(blank=True, null=True)
    user = models.ForeignKey(settings.ACCOUNT_USER_PROXY_MODEL, on_delete=models.CASCADE)
    date_created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.campaign:
            return '#sms_campaign ' + self.campaign.name
        else:
            '#sms_campaign'

    class Meta:
        db_table = 'sms_campaign'
        verbose_name = 'SMS Campaign'


class ISMS(models.Model):
    sender_id = models.CharField(max_length=255, null=True, blank=True)
    from_no = models.CharField(max_length=255, null=True, blank=True)
    to = models.CharField(max_length=255, null=True, blank=True)
    campaign = models.ForeignKey(Campaign, null=True, blank=True, on_delete=models.SET_NULL)
    text = models.TextField(blank=True, null=True)
    raw_data = models.TextField(blank=True, null=True)
    from_city = models.CharField(max_length=255, null=True, blank=True)
    from_country = models.CharField(max_length=255, null=True, blank=True)
    duration = models.CharField(max_length=255, null=True, blank=True)
    from_state = models.CharField(max_length=255, null=True, blank=True)
    to_country = models.CharField(max_length=255, null=True, blank=True)
    to_zip = models.CharField(max_length=255, null=True, blank=True)
    from_zip = models.CharField(max_length=255, null=True, blank=True)
    message_sid = models.CharField(max_length=255, null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    @property
    def campaign_no(self):
        my_campaign = TwilioNumber.objects.filter(twilio_number=self.to)
        if my_campaign:
            myc = SMSCampaign.objects.filter(campaign_no=my_campaign[0].id)
            if myc:
                return myc[0].name
        else:
            return None

    class Meta:
        db_table = 'incoming_sms'


class OSMS(models.Model):
    """Outgoing SMS"""
    sender_id = models.CharField(max_length=255, null=True, blank=True)
    from_no = PhoneNumberField()
    to = PhoneNumberField()
    campaign = models.ForeignKey(Campaign, null=True, blank=True, on_delete=models.SET_NULL)
    text = models.TextField(blank=True, null=True)
    raw_data = models.TextField(blank=True, null=True)
    from_city = models.CharField(max_length=255, null=True, blank=True)
    from_country = models.CharField(max_length=255, null=True, blank=True)
    duration = models.CharField(max_length=255, null=True, blank=True)
    from_state = models.CharField(max_length=255, null=True, blank=True)
    to_country = models.CharField(max_length=255, null=True, blank=True)
    to_zip = models.CharField(max_length=255, null=True, blank=True)
    from_zip = models.CharField(max_length=255, null=True, blank=True)
    message_sid = models.CharField(max_length=255, null=True, blank=True)
    send_at = models.DateTimeField(blank=True, null=True)
    status = models.CharField(max_length=255, null=True, blank=True, default='created')
    # Initial must be "created" (before accepted or queued)
    # Possible status values from twilio:
    #   (created,) accepted, queued, sending, sent
    #       delivered, failed, undelivered

    is_reply_to = models.ForeignKey(ISMS, on_delete=models.SET_NULL, null=True, blank=True)
    status_checked = models.BooleanField(default=False)
    sent = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    is_sample = models.BooleanField(blank=True, default=False)

    num_segments = models.PositiveIntegerField(blank=True, default=1)
    # The number of segments were determined by twilio upon sending/queueing
    #   this vaule is used at billing only.

    countdown = models.IntegerField(default=0, help_text="In seconds", blank=True)

    @property
    def twilio_callback_url(self):
        """Twillio callback URL for SMS outgoing"""
        domain = Site.objects.get_current().domain
        link = reverse('srm:marketing:sms_callback')
        return 'https://{}{}'.format(domain, link)

    @property
    def campaign_no(self):

        my_campaign = TwilioNumber.objects.filter(twilio_number=self.to)
        if my_campaign:
            myc = SMSCampaign.objects.filter(campaign_no=my_campaign[0].id)
            if myc:
                return myc[0].name
        else:
            return None

    @property
    def twilio_number(self):
        from ccc.campaigns.utils.twilio import get_obj_from_twilio_number
        return get_obj_from_twilio_number(self.from_no)

    class Meta:
        db_table = 'sent_sms'
        verbose_name = 'Outgoing SMS (OSMS)'
        verbose_name_plural = "Outgoing SMSes"

    def send(self):
        """Send this SMS"""
        try:
            #         msg_text = "{} \nSend STOP to unsubscribe".format(osms.text)
            # TODO Need to send stop message once per contact
            twilio_number = self.twilio_number
            twilio_no_obj = twilio_number  # todo WTF ?

            msg_text = "{}".format(self.text)
            if twilio_number and twilio_number.user.balance.get('sms', 0) >= 0:
                response = client.messages.create(
                    body=msg_text,
                    to=self.to.as_international,
                    from_=twilio_no_obj.twilio_number,
                    status_callback=self.twilio_callback_url
                )
            else:
                title_msg = "SMS limit exhausted for {}. Email={}"
                title_msg = title_msg.format(
                    twilio_no_obj.user.full_name,
                    twilio_no_obj.user.email
                )
                message = "SMS Remaining={} To_number={} From_no={} body={}"
                message = message.format(
                    twilio_no_obj.user.balance.get('sms', 0),
                    self.to.as_international,
                    self.from_no, msg_text
                )
                # TODO I think the user will be notified via dashboard. #IMPROVEMENT
                logger.error(title_msg)
                logger.error(message)
                return

        except TwilioRestException as exception:
            raise exception
        else:
            logger.info("SMS send successfully [in {} segments] | from={} | to={} | ".format(
                response.num_segments, twilio_no_obj.twilio_number, self.to.as_international))

            self.message_sid = response.sid
            self.status = response.status
            self.num_segments = int(response.num_segments)
            self.save()


class MMSCampaign(CampaignChannelModelMixin):
    text = models.CharField(max_length=255, blank=True, null=True)
    campaign = models.ForeignKey(Campaign, blank=True, null=True, on_delete=models.CASCADE)
    sample_no = models.CharField(max_length=255, blank=True, null=True)
    image1 = models.ImageField(upload_to='campaigns/mms', blank=True, null=True)
    image2 = models.ImageField(upload_to='campaigns/mms', blank=True, null=True)
    video = models.FileField(upload_to='campaigns/mms', blank=True, null=True)
    user = models.ForeignKey(settings.ACCOUNT_USER_PROXY_MODEL, on_delete=models.CASCADE)
    ended_at = models.DateTimeField(blank=True, null=True)
    date_created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '#mms ' + self.campaign.name

    class Meta:
        db_table = 'mms_campaign'


class IMMS(models.Model):
    from_no = models.CharField(max_length=255, null=True, blank=True)
    to = models.CharField(max_length=255, null=True, blank=True)

    campaign = models.ForeignKey(Campaign, null=True, blank=True, on_delete=models.SET_NULL)

    raw_data = models.TextField(blank=True, null=True)
    media_list = models.TextField(blank=True, null=True)
    from_city = models.CharField(max_length=255, null=True, blank=True)
    from_country = models.CharField(max_length=255, null=True, blank=True)
    duration = models.CharField(max_length=255, null=True, blank=True)
    from_state = models.CharField(max_length=255, null=True, blank=True)
    to_country = models.CharField(max_length=255, null=True, blank=True)
    to_zip = models.CharField(max_length=255, null=True, blank=True)
    from_zip = models.CharField(max_length=255, null=True, blank=True)
    message_sid = models.CharField(max_length=255, null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    @property
    def campaign_no(self):

        my_campaign = TwilioNumber.objects.filter(twilio_number=self.to)
        if my_campaign:
            myc = MMSCampaign.objects.filter(campaign_no=my_campaign[0].id)
            if myc:
                return myc[0].name
        else:
            return None

    class Meta:
        db_table = 'incoming_mms'


class OMMS(models.Model):
    from_no = models.CharField(max_length=255, null=True, blank=True)
    to = models.CharField(max_length=255, null=True, blank=True)
    text = models.TextField(blank=True, null=True)

    campaign = models.ForeignKey(Campaign, null=True, blank=True, on_delete=models.SET_NULL)

    message_sid = models.CharField(max_length=255, null=True, blank=True)

    status = models.CharField(max_length=255, null=True, blank=True, default='created')
    # Initial must be "created" (before accepted or queued)
    # Possible status values from twilio:
    #   (created,) accepted, queued, sending, sent
    #       delivered, failed, undelivered

    is_sample = models.BooleanField(blank=True, default=False)

    countdown = models.IntegerField(default=0, help_text="In seconds", blank=True)
    # Used for scheduling the sms sending with celery

    date_created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    media = JSONField(blank=True, default=[])

    def __str__(self):
        return '%s -> %s @ %s' % (self.from_no, self.to, self.date_created)

    class Meta:
        db_table = 'sent_mms'
        verbose_name = 'outgoing MMS'
        verbose_name_plural = 'outgoing MMSes'

    def media_absolute_urls(self):
        media_list = list()
        for url in self.media:
            # avoid None url
            if url:
                media_list.append(validate_media_absolute_url(url))
        return media_list


# Handle OMMS post_save signal (send mms)
post_save.connect(omms_post_save, sender=OMMS)


class OEmail(models.Model):
    logo = models.CharField(max_length=255, null=True, blank=True)
    from_email = models.CharField(max_length=255, null=True, blank=True)
    to_email = models.CharField(max_length=255, null=True, blank=True)
    time = models.DateTimeField(auto_now_add=True)

    campaign = models.ForeignKey(Campaign, null=True, blank=True, on_delete=models.SET_NULL)

    company = models.CharField(max_length=255, null=True, blank=True)
    template = models.CharField(max_length=255, null=True, blank=True)
    sent = models.BooleanField(default=False)
    send_at = models.DateTimeField(blank=True, null=True)
    body = models.TextField(blank=True, null=True)
    subject = models.CharField(max_length=255, null=True, blank=True)
    attachment = models.TextField(blank=True, null=True)
    lead_name = models.CharField(max_length=255, null=True, blank=True)
    last_name = models.CharField(max_length=55, null=True, blank=True)
    user = models.ForeignKey(settings.ACCOUNT_USER_PROXY_MODEL, null=True, blank=True, on_delete=models.SET_NULL)

    class Meta:
        db_table = 'sent_email'

    def __str__(self):
        if self.to_email:
            return self.to_email
        else:
            return str(self.id)


class IEmail(models.Model):
    from_email = models.CharField(max_length=255, null=True, blank=True)
    campaign = models.ForeignKey(Campaign, null=True, blank=True, on_delete=models.SET_NULL)
    raw_data = models.TextField(blank=True, null=True)
    from_city = models.CharField(max_length=255, null=True, blank=True)
    from_country = models.CharField(max_length=255, null=True, blank=True)
    from_state = models.CharField(max_length=255, null=True, blank=True)
    from_zip = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'incoming_emails'


class SampleVoiceCall(models.Model):
    user = models.ForeignKey(settings.ACCOUNT_USER_PROXY_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    voice_greeting_original = models.FileField(upload_to='campaigns/sample_test_voice', blank=True, null=True)
    voice_greeting_converted = models.FileField(upload_to='campaigns/sample_test_voice', blank=True, null=True)
    greeting_text = models.TextField(blank=True, null=True)
    phone = models.ForeignKey(TwilioNumber, on_delete=models.CASCADE)
    sample_phone = PhoneNumberField()

    def __str__(self):
        return self.sample_phone.as_international

    @property
    def voice_greeting(self):
        return self.voice_greeting_converted or \
               self.voice_greeting_original


def create_out_email(sender, instance, created, **kwargs):
    if created:
        Contact = django_apps.get_model('contacts', 'Contact')
        # TODO: REVISE THIS
        contact = Contact.objects.filter(user=instance.user.id)
        # !!! Will send out-eamil to all contacts for that particular user. Wrong.
        if contact:
            for i in contact:
                if i.email:
                    if instance.campaign.logo:
                        logo = instance.campaign.logo.url
                    else:
                        logo = '/static/images/logo_blue.png'
                    if instance.template:
                        template = instance.template.name
                    else:
                        template = 'default'

                    OEmail.objects.create(campaign=instance.campaign, from_email=instance.campaign.from_email,
                                          to_email=i.email,
                                          body=instance.body,
                                          subject=instance.subject, company=instance.campaign.company,
                                          lead_name=i.first_name, send_at=instance.send_at, template=template,
                                          logo=logo)


# def create_out_sms(sender, instance, created, **kwargs):
#     campaign = instance.campaign
#     if created:
#         Contact = django_apps.get_model('contacts', 'Contact')
#         contacts = Contact.objects.filter(campaigns=campaign).distinct()
#         for contact in contacts:
#             if contact.phone:
#                 OSMS.objects.create(campaign=campaign, to=contact.phone, from_no=campaign.phone.twilio_number,
#                                     sender_id=contact.first_name, send_at=instance.trigger_date, text=instance.text)
#
#
# post_save.connect(create_out_sms, sender=SMSCampaign)


def create_out_voice(sender, instance, created, **kwargs):
    if created:
        Contact = django_apps.get_model('contacts', 'Contact')
        # TODO: REVISE THIS
        contact = Contact.objects.filter(user=instance.user.id)
        if contact:

            for i in contact:
                if i.phone:
                    if isinstance(instance, VoiceCampaign):
                        OVoiceCall.objects.create(campaign=instance.campaign, to=i.phone,
                                                  from_no=instance.campaign.phone.twilio_number,
                                                  send_at=instance.trigger_date)


ACCOUNT_SID = settings.TWILIO_SID
AUTH_TOKEN = settings.TWILIO_TOKEN
client = TwilioRestClient(ACCOUNT_SID, AUTH_TOKEN)


def send_sms_received(sender, instance, created, **kwargs):
    if created:
        numbers = TwilioNumber.objects.filter(user=instance.campaign.user)
        if numbers:
            try:
                contact = Notify.objects.get(user=instance.campaign.user.id)
            except Notify.DoesNotExist:
                # Notify object does not exist for this user yet
                # TODO: Create notify object on post_save of UserProfile
                return
            if contact.phone and contact.sms:
                body = 'You have received an sms from {}'.format(
                    instance.from_no)
                if instance.campaign.user.balance.get('sms', 0) > 0:
                    try:
                        sms = client.messages.create(
                            body=body, to=contact.phone, from_=numbers[0].twilio_number)
                    except TwilioRestException:
                        pass
                    # TODO: Create OSMS object here


def send_call_received(sender, instance, created, **kwargs):
    if instance.status == "completed":
        numbers = TwilioNumber.objects.filter(user=instance.campaign.user)
        if numbers:
            contact = Notify.objects.get(user=instance.campaign.user.id)
            if contact.phone and contact.sms:
                body = 'You have received a call for "{}" from {}'.format(instance.campaign.name, instance.from_no)
                if instance.recording_url:
                    body += ' Listen to voice message {}'.format(instance.recording_short_url)
                else:
                    body += ' There is no voice message'
                if instance.campaign.user.balance.get('sms', 0) > 0:
                    sms = client.messages.create(body=body, to=contact.phone, from_=numbers[0].twilio_number)
                    # TODO: Create OSMS object here


# post_save.connect(create_out_voice, sender=VoiceCampaign)
#
# post_save.connect(create_out_email, sender=EmailCampaign)

post_save.connect(send_call_received, sender=IVoiceCall)
post_save.connect(send_sms_received, sender=ISMS)


class CampaignMMSImages(models.Model):
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='campaigns/mms')

    def __str__(self):
        return self.campaign.name


class CampaignAttachments(models.Model):
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE)
    attachment = models.FileField(upload_to='campaigns/attachments')

    def __str__(self):
        return self.campaign.name


class TemplateImages(models.Model):
    # TODO: bad naming
    image = models.ImageField(max_length=250, null=True, blank=True, upload_to='campaigns/email/images')
    campaign = models.ForeignKey(Campaign, null=True, blank=True, on_delete=models.SET_NULL)
    description = models.CharField(max_length=50, null=True)
    url = models.URLField(null=True, blank=True)
    attachment = models.FileField(max_length=250, null=True, blank=True,
                                  upload_to='campaigns/email/templates/attachments')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    number = models.IntegerField(default=1)
    user = models.ForeignKey(settings.ACCOUNT_USER_PROXY_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    digital_image = models.ForeignKey(DigitalImage, null=True, blank=True, on_delete=models.SET_NULL)
    digital_audio = models.ForeignKey(DigitalAudio, null=True, blank=True, on_delete=models.SET_NULL)
    digital_video = models.ForeignKey(DigitalVideo, null=True, blank=True, on_delete=models.SET_NULL)
    digital_attachment = models.ForeignKey(DigitalAttachment, null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.description if self.description else str(self.id)


def create_related_instances(sender, instance, created, **kwargs):
    if created and instance.template:
        for i in range(1, instance.template.number_of_max_uploads + 1):
            TemplateImages.objects.create(template=instance.template, number=i, campaign=instance)


# post_save.connect(create_related_instances, sender=Campaign)


class MappedKeywords(models.Model):
    """Class to store mapped keywords with campaign
    """
    keyword = models.CharField(max_length=250, null=True, blank=True)
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class RejectedNumber(models.Model):
    """Model to store unwanted numbers from which we don't to receive call or sms
    """
    reject_number = models.CharField(max_length=255, null=True, blank=True, unique=True)
    twilio_numbers = models.ManyToManyField(TwilioNumber, blank=True)
    reject_for_all = models.BooleanField(default=False)


post_save.connect(signal_send_sms, sender=OSMS)
