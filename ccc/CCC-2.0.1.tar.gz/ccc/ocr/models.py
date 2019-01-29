from uuid import uuid4

from django.db import models

from ccc.survey.models import Survey as SurveyModel


def generateUUID():
    return str(uuid4())


class ImageContacts(models.Model):
    """Model to store uploaded contact images
    """
    image = models.ImageField(upload_to='campaigns/ocr/images')
    phones = models.CharField(max_length=600, blank=True, null=True, default=None)
    emails = models.CharField(max_length=600, blank=True, null=True, default=None)
    converted_text = models.TextField(blank=True, null=True, default=None)
    campaign = models.ForeignKey("campaigns.Campaign", default=None, null=True, blank=True, on_delete=models.SET_NULL)
    survey = models.ForeignKey(SurveyModel, default=None, null=True, blank=True, on_delete=models.SET_NULL)
    unique_upload_id = models.CharField(max_length=100, default=generateUUID)
    is_processed = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
