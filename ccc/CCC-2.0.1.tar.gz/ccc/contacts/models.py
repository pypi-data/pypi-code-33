# -*- coding: utf-8 -*-
import logging
import random
import string
from uuid import uuid4

from django.conf import settings
from django.contrib.postgres.fields import JSONField
from django.contrib.sites.models import Site
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db import models
from django.db.models.signals import m2m_changed, post_save
from django.dispatch import receiver
from django.template import Context, Template
from django.template.defaultfilters import slugify
from django.urls import reverse as reverse_url
from model_utils.models import TimeStampedModel
from phonenumber_field.modelfields import PhoneNumberField
from sorl.thumbnail import get_thumbnail

from ccc.contacts.cloud_tasks import (fetch_social_profiles,
                                      send_business_card_url_task)
from ccc.contacts.utils import clean_phone

logger = logging.getLogger(__name__)


def random_generator(size=6, chars=string.ascii_letters + string.digits):
    return ''.join(random.choice(chars) for x in range(size))


def generateUUID():
    return str(uuid4())


LEAD_TYPE = (
    ('1', "SMS"),
    ('2', "MMS"),
    ('3', "VOICE"),
    ('4', "CSV UPLOAD"),
    ('5', "Card Scan"),
    ('6', "Manual"),
    ('7', "Survey"),
    ('8', "System user import"))

CONTACT_TYPE = (
    ('CS', 'Card Scan'),
    ('DBC', 'Digital Business Card')
)

TEMPLATE_PREFIX = 'contact'
TEMPLATE_FIELDS = (('phone', 'phone number'),
                   ('first_name', 'first name'),
                   ('last_name', 'last name'),
                   ('email', 'email address'),
                   ('company_name', 'company name'),
                   ('designation', 'designation'),
                   ('country', 'country'),
                   ('state', 'state'),
                   ('zip', 'zip code'))

SOURCE_TYPE = (
    ('M', 'mobile'),
    ('W', 'Website'),
)


class Contact(models.Model):
    user = models.ForeignKey(settings.ACCOUNT_USER_PROXY_MODEL, blank=True, null=True, on_delete=models.SET_NULL)
    social_id = models.CharField(max_length=10, blank=True, null=True)
    # Personal Information
    phone = PhoneNumberField(blank=True, null=True)
    cell_number = PhoneNumberField(blank=True, null=True)
    first_name = models.CharField(max_length=150, blank=True, null=True)
    last_name = models.CharField(max_length=150, blank=True, null=True)
    profile_image = models.ImageField(upload_to='digital/cards', blank=True, null=True)
    email = models.CharField(max_length=255, blank=True, null=True)
    company_name = models.CharField(max_length=150, blank=True, null=True)
    designation = models.CharField(max_length=150, blank=True, null=True)
    note = models.TextField(blank=True, null=True)
    text_me = models.BooleanField(default=False)

    call_sid = models.CharField(max_length=50, blank=True, null=True)
    sms_sid = models.CharField(max_length=50, blank=True, null=True)
    lead_type = models.CharField(max_length=10, choices=LEAD_TYPE, blank=True, null=True)
    # Address
    street = models.CharField(max_length=150, blank=True, null=True)
    city = models.CharField(max_length=50, blank=True, null=True)
    state = models.CharField(max_length=150, blank=True, null=True)
    zip = models.CharField(max_length=50, blank=True, null=True)
    country = models.CharField(max_length=150, blank=True, null=True)
    google_map = models.BooleanField(default=False)
    # Campaigns
    campaigns = models.ManyToManyField("campaigns.Campaign")
    survey = models.ForeignKey("survey.Survey", null=True, blank=True, on_delete=models.SET_NULL)
    is_supplier = models.BooleanField(default=False)
    # Card Image is not in use for OCR images
    card_image = models.ImageField(upload_to='campaigns/cards', blank=True, null=True)
    card_front_image = models.ImageField(upload_to='campaigns/front_cards', blank=True, null=True)
    card_back_image = models.ImageField(upload_to='campaigns/back_cards', blank=True, null=True)
    card_image_uuid = models.CharField(max_length=100, default=None, unique=True, blank=True, null=True)

    contact_type = models.CharField(max_length=10, choices=CONTACT_TYPE, blank=True, null=True)
    source = models.CharField(max_length=10, choices=SOURCE_TYPE, blank=True, null=True, default='W')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def social_full_name(self):
        first_name = self.first_name.title() if self.first_name else ''
        last_name = self.last_name.title() if self.last_name else ''
        return first_name + last_name

    @property
    def get_full_name(self):
        first_name = self.first_name.title() if self.first_name else ''
        last_name = self.last_name.title() if self.last_name else ''
        return first_name + ' ' + last_name

    def __str__(self):
        if self.first_name:
            return self.first_name
        else:
            if self.phone:
                return self.phone.as_e164
            else:
                return "Contact #%s" % (self.pk or 'unsaved')

    @property
    def social_url(self):
        return reverse_url('crm:business_card', args=[self.social_id, self.social_full_name])

    @property
    def generate_social_id(self):
        while True:
            social_id = random_generator()
            if not Contact.objects.filter(social_id=social_id).exists():
                break
        return social_id

    def save(self, *args, **kw):
        orig = None
        if not self.social_id:
            self.social_id = self.generate_social_id
        if self.pk is not None:
            orig = Contact.objects.get(pk=self.pk)
        super(Contact, self).save(*args, **kw)
        if self.contact_type == 'DBC' and self.source == 'M':
            send_business_card_url_task(contact_id=self.id).execute()
        # When email is added or updated to existing contact
        if orig and self.email and orig.email != self.email:
            # Async task
            fetch_social_profiles(contact_id=self.id).execute()
            # Trigger email campaigns if any
            for campaign in self.campaigns.all():
                if campaign.user.balance.get('email', 0) > 0 and campaign.use_email:
                    from ccc.campaigns.cloud_tasks import campaign_send_email
                    # Todo
                    # eta = get_task_eta(campaign.user.time_zone, seconds=campaign.email_delay,
                    #                    campaign_trigger_date=campaign.email_campaign_trigger_date)
                    #
                    campaign_send_email(campaign_id=campaign.id, contact_id=self.id).execute()

    @property
    def template_context(self):
        ctx = {"%s__%s" % (self.TEMPLATE_PREFIX, field[0]): getattr(self, field[0])
               for field in self.TEMPLATE_FIELDS}
        for prop in self.properties.all():
            ctx["%s__%s" % (self.TEMPLATE_PREFIX, prop.slug)] = prop.value
        return ctx

    def notes(self):
        notes = ContactNote.objects.filter(contact=self.id).count()
        if notes:
            return notes
        else:
            return None

    class Meta:
        db_table = 'lead_contacts'

    @classmethod
    def match_or_create(cls, email, phone, user):
        """ Returns an existing or a new Contact object based on email/phone matching.
        Missing email and phone values are set, but not saved."""

        created = False
        existing_contact_by_email = None
        existing_contact_by_phone = None
        try:
            validate_email(email)
        except ValidationError:
            pass  # invalid email
        else:
            existing_contact_by_email = Contact.objects.filter(
                email=email, user=user).first()

        phone_number, country = clean_phone(str(phone))
        if phone_number:
            existing_contact_by_phone = Contact.objects.filter(
                phone=phone_number, user=user).first()

        if existing_contact_by_email:
            contact = existing_contact_by_email
        elif existing_contact_by_phone:
            contact = existing_contact_by_phone
        else:
            created = True
            contact = Contact()

        if email and not contact.email:
            contact.email = email

        if phone_number and not contact.phone:
            contact.phone = phone_number

        contact.user = user
        contact.lead_type = 4

        return contact, created


class ContactGroup(models.Model):
    user = models.ForeignKey(settings.ACCOUNT_USER_PROXY_MODEL, related_name='contact_groups',
                             on_delete=models.CASCADE)
    name = models.CharField(max_length=255)

    contacts = models.ManyToManyField(
        Contact, related_name='groups', blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        unique_together = ('user', 'name')
        verbose_name = 'contact group'
        verbose_name_plural = ' contact groups'


class ContactProperty(models.Model):
    contact = models.ForeignKey(Contact, related_name='properties', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    value = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def slug(self):
        return slugify(self.name).replace('-', '_')

    class Meta:
        unique_together = ('contact', 'name')

    def __str__(self):
        return "%s: %s" % (self.name, self.value)


class ContactNote(models.Model):
    note = models.TextField()
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.note


class ContactCheckin(TimeStampedModel):
    contact = models.ForeignKey("Contact", related_name="checkins", on_delete=models.CASCADE)
    campaign = models.ForeignKey("campaigns.Campaign", related_name="checkins", on_delete=models.CASCADE)
    sms = models.TextField(null=True, blank=True)
    delay = models.PositiveIntegerField(default=0, help_text="In seconds")


class ContactSocialProfile(TimeStampedModel):
    contact = models.ForeignKey("Contact", related_name="social_profiles", on_delete=models.CASCADE)
    website = models.URLField(max_length=255, null=True, blank=True)
    bio = models.TextField(null=True, blank=True)
    title = models.CharField(max_length=255, null=True, blank=True)
    gender = models.CharField(max_length=15, null=True, blank=True)
    skype = models.CharField(max_length=15, null=True, blank=True)
    twitter = models.URLField(max_length=255, null=True, blank=True)
    foursquare = models.URLField(max_length=255, null=True, blank=True)
    linkedin = models.URLField(max_length=255, null=True, blank=True)
    facebook = models.URLField(max_length=255, null=True, blank=True)
    instagram = models.URLField(max_length=255, null=True, blank=True)
    whatsup_num = models.CharField(max_length=255, null=True, blank=True)
    snapchat_user = models.URLField(max_length=255, null=True, blank=True)
    google_plus = models.URLField(max_length=255, null=True, blank=True)
    youtube = models.URLField(max_length=255, null=True, blank=True)
    pinterest = models.URLField(max_length=255, null=True, blank=True)
    meetup = models.URLField(max_length=255, null=True, blank=True)
    blog = models.URLField(max_length=255, null=True, blank=True)
    location = models.CharField(max_length=255, null=True, blank=True)
    organization = models.CharField(max_length=255, null=True, blank=True)
    ageRange = models.CharField(max_length=15, null=True, blank=True)
    fullName = models.CharField(max_length=255, null=True, blank=True)
    avatar = models.URLField(null=True, blank=True)
    updated = models.DateField(null=True, blank=True)
    dataAddOns = JSONField(null=True, blank=True)
    details = JSONField(null=True, blank=True)
    data = JSONField(null=True, blank=True)

    def __str__(self):
        return "{} - {}".format(self.contact, self.title)


class CompanySocialProfile(TimeStampedModel):
    contact = models.ForeignKey("Contact", related_name="company_social_profiles", on_delete=models.CASCADE)
    website = models.CharField(max_length=255, null=True, blank=True)
    bio = models.TextField(null=True, blank=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    founded = models.CharField(max_length=15, null=True, blank=True)
    twitter = models.URLField(max_length=255, null=True, blank=True)
    linkedin = models.URLField(max_length=255, null=True, blank=True)
    facebook = models.URLField(max_length=255, null=True, blank=True)
    location = models.CharField(max_length=255, null=True, blank=True)
    locale = models.CharField(max_length=5, null=True, blank=True)
    logo = models.URLField(null=True, blank=True)
    updated = models.DateField(null=True, blank=True)
    dataAddOns = JSONField(null=True, blank=True)
    category = models.CharField(max_length=255, null=True, blank=True)
    employees = models.CharField(max_length=20, null=True, blank=True)
    details = JSONField(null=True, blank=True)
    data = JSONField(null=True, blank=True)

    def __str__(self):
        return "{} - {}".format(self.contact, self.name)


class RemoveDomainSearch(TimeStampedModel):
    """Remove Domain from search orgnization"""
    domain_name = models.CharField(max_length=255)


@receiver(post_save, sender=Contact)
def contact_fetch_social_profiles(sender, instance, created, **kwargs):
    if created:
        fetch_social_profiles(contact_id=instance.id).execute()


def fusion_campaign_trigger(instance, campaign, HOSTNAME, PROTOCOL):
    """SRM Fusion Support """
    from ccc.campaigns.models import OMMS, OSMS
    from ccc.campaigns.cloud_tasks import voice_call, campaign_send_email

    from ccc.campaigns.utils.sending import (
        follow_up_campaign_send_sms,
        follow_up_campaign_send_mms,
        follow_up_campaign_send_email,
        follow_campaign_make_call
    )

    HOSTNAME = Site.objects.get_current().domain
    PROTOCOL = "https"

    fu_campaigns = campaign.fucampaign_set.all()
    balance = campaign.user.balance
    phone = instance.phone
    if phone and balance.get('talktime', 0) > 0 and instance.lead_type != '3':
        call_relative_url = reverse_url('send_voice', kwargs={'c_id': campaign.id})
        call_url = '%s://%s%s' % (PROTOCOL, HOSTNAME, call_relative_url)
        try:
            campaign.voicecampaign_set.latest('id')
        except Exception as ex:
            logger.info('Voice campaign dose not exist for campaign={}, error={}'.format(
                campaign.id, ex.args))
        else:
            if campaign.use_voice:
                voice_call(url=call_url, to_phone=phone,
                           from_phone=campaign.phone.twilio_number).execute()
            for fu_campaign in fu_campaigns.filter(send_voice=True, onleadcapture=True):
                follow_campaign_make_call(fu_campaign, instance)
    text = ''
    if phone and balance.get('sms', 0) > 0:
        try:
            sms_campaign = campaign.smscampaign_set.latest('id')
        except Exception as ex:
            logger.info('SMS campaign dose not exist for campaign={}, error={}'.format(
                campaign.id, ex.args))
        else:
            if campaign.use_sms and sms_campaign.text:
                text = Template(sms_campaign.text).render(Context(instance.template_context))
                if text:
                    OSMS.objects.create(
                        from_no=campaign.phone.twilio_number,
                        campaign=campaign,
                        to=phone,
                        text=text,
                        countdown=campaign.sms_delay,
                    )
                    for fu_campaign in fu_campaigns.filter(send_sms=True, onleadcapture=True):
                        follow_up_campaign_send_sms(fu_campaign, instance)
    text = ''
    if phone and balance.get('mms', 0) > 0:
        try:
            mms_camp = campaign.mmscampaign_set.latest('id')
        except Exception as ex:
            logger.info('MMS campaign dose not exist for campaign={}, error={}'.format(
                campaign.id, ex.args))
        else:
            media = []
            if mms_camp:
                if mms_camp.image1:
                    thumnail = get_thumbnail(mms_camp.image1, '300x200', quality=99)
                    media.append('https:' + thumnail.url)
                if mms_camp.image2:
                    thumnail = get_thumbnail(mms_camp.image2, '300x200', quality=99)
                    media.append('https:' + thumnail.url)
                if mms_camp.video:
                    media.append('https:' + mms_camp.video.url)
                text = mms_camp.text
                if campaign.use_mms and (text or media):
                    OMMS.objects.create(from_no=campaign.phone.twilio_number, to=phone,
                                        campaign=campaign,
                                        text=text,
                                        media=media,
                                        countdown=campaign.mms_delay)
                for fu_campaign in fu_campaigns.filter(send_mms=True, onleadcapture=True):
                    follow_up_campaign_send_mms(fu_campaign, instance)
    if instance.email and balance.get('email', 0) > 0:
        if campaign.use_email:
            campaign_send_email(campaign_id=campaign.id, contact_id=instance.id).execute()
            for fu_campaign in fu_campaigns.filter(send_email=True, onleadcapture=True):
                follow_up_campaign_send_email(fu_campaign, instance)


# This triggers when a contact is added to a campaign
def handle_contact_added_to_campaign(sender, instance, action, reverse, model, pk_set, **kwargs):
    contact_ids = kwargs.get('contact_ids', [instance.id])
    if action == 'post_add':
        from ccc.campaigns.cloud_tasks import campaign_trigger
        from ccc.campaigns.models import Campaign
        for campaign_id in pk_set:
            hostname = Site.objects.get_current().domain
            protocol = "https"
            if kwargs.get('source') == 'fusion' or 'fusion' in hostname:
                return fusion_campaign_trigger(instance, Campaign.objects.get(pk=campaign_id), hostname, protocol)
            if not isinstance(contact_ids, list):
                contact_ids = [instance.id]
            if Campaign.objects.filter(phone__isnull=False, pk=campaign_id).exists():
                campaign_trigger(contact_ids=contact_ids, campaign_id=campaign_id).execute()


m2m_changed.connect(handle_contact_added_to_campaign, sender=Contact.campaigns.through)
