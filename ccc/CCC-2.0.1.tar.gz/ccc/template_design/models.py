import os
from io import BytesIO
from tempfile import NamedTemporaryFile

from django.conf import settings
from django.contrib.postgres.fields import JSONField
from django.core.files.base import ContentFile
from django.db import models
from premailer import transform
from screamshot.utils import casperjs_capture

from ccc.campaigns.models import Campaign
from ccc.constants import initial_web_template_data

TEMPLATE_TYPE = (('web', 'Web'), ('email', 'email'))


class TemplateDesign(models.Model):
    """Email Template Design Model"""
    name = models.CharField(max_length=255)
    name_slug = models.CharField(max_length=300, blank=True, null=True)
    email_body = models.TextField()
    user = models.ForeignKey(settings.ACCOUNT_USER_PROXY_MODEL, on_delete=models.CASCADE)
    preview = models.ImageField(upload_to='template_design/images', blank=True, null=True)
    template = models.FileField(upload_to='campaigns/email/templates', blank=True, null=True)
    template_type = models.CharField(max_length=25, choices=TEMPLATE_TYPE, default='email')
    json_data = JSONField(blank=True, default=initial_web_template_data)
    is_active = models.BooleanField(default=True)
    is_public = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("name", "user")

    def __str__(self):
        return self.name

    def update_thumbnail(self):
        """
        For updating thumbnail automatically with casperjs
        Not called, only for manual use yet.

        Needs CasperJS to be installed on the system:
        `npm install casperjs` or `sudo npm install -g casperjs`
        """
        template_content = transform(self.email_body)
        with NamedTemporaryFile(suffix='.html') as render_file:
            render_file.write(template_content.encode('utf-8'))
            render_file.seek(0)
            stream = BytesIO()
            casperjs_capture(stream, url='file://%s' % os.path.abspath(render_file.name))

        self.preview.save('thumbnail_%s.png' % self.pk, ContentFile(stream.getvalue()))

    def save(self, *args, **kwargs):
        self.name_slug = self.name.replace(" ","-")
        super(TemplateDesign, self).save(*args, **kwargs)


class EmailAndWebAnalytics(models.Model):
    """Email and web analytics model"""
    data = JSONField()
    created_date = models.DateTimeField(auto_now_add=True)

    @classmethod
    def get_count(cls, open_email_data):
        data = []
        remove_duplicate = []
        for email_statics in open_email_data:
            to_email = email_statics.data.get('to_email')
            if to_email not in remove_duplicate:
                remove_duplicate.append(to_email)
                obj_data = email_statics.data
                data.append(obj_data)
        return len(data)

    @classmethod
    def email_open_rate(cls, user_id, campaign_id=None):
        """Get email open rate"""
        if campaign_id:
            return cls.get_count(cls.objects.filter(data__sender_id=str(user_id), data__type='email',
                                                    data__campaign_id=str(campaign_id)))
        return cls.get_count(cls.objects.filter(data__sender_id=str(user_id), data__type='email'))

    @classmethod
    def get_all_email(cls, user_id=None):
        if user_id:
            return cls.objects.filter(data__sender_id=str(user_id), data__type='email')
        return cls.objects.filter(data__type='email')


class LandingPageFormData(models.Model):
    """Landing page form data"""
    template = models.ForeignKey(TemplateDesign, on_delete=models.CASCADE)
    data = JSONField()


class CampaignTemplateDesign(models.Model):
    """Campaign and template design relation"""
    template = models.ForeignKey(TemplateDesign, on_delete=models.CASCADE)
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE)
    template_type = models.CharField(max_length=25, choices=TEMPLATE_TYPE, default='email')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = (("template", "campaign", "template_type"))
