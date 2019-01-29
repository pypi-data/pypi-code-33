from django.urls import reverse_lazy
from rest_framework import serializers

from ccc.campaigns.models import CampaignEmailTemplate
from ccc.template_design.models import TemplateDesign


class EmailTemplateSerializer(serializers.ModelSerializer):
    """Email Template Serializer"""

    class Meta:
        model = CampaignEmailTemplate
        fields = '__all__'


class TemplateDesignSerializer(serializers.ModelSerializer):
    """Premium Email Template Serializer"""
    edit_url = serializers.SerializerMethodField()

    class Meta:
        model = TemplateDesign
        fields = ('id', 'name', 'preview', 'edit_url')

    def get_edit_url(self, obj):
        return reverse_lazy('srm:template_design:design_template_email_update', args=[obj.id])
