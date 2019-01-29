# Register your models here.
from django.contrib import admin

from ccc.template_design.models import (CampaignTemplateDesign,
                                        EmailAndWebAnalytics,
                                        LandingPageFormData, TemplateDesign)


class EmailTemplateDesignAdmin(admin.ModelAdmin):
    """Email Template Design Admin"""
    list_display = [
        'id',
        'name',
        'user',
        'template_type',
        'is_active',
        'is_public',
        'template',
        'updated_at',
        'preview']


class EmailAndWebAnalyticsAdmin(admin.ModelAdmin):
    """Email Template Design Admin"""
    list_display = ['data']


class LandingPageFormDataAdmin(admin.ModelAdmin):
    """Landing Page Form Data Admin"""
    list_display = ['template', 'data']


class CampaignTemplateDesignAdmin(admin.ModelAdmin):
    """Campaign template design"""
    list_display = ['template', 'campaign', 'template_type', 'updated_at']


admin.site.register(TemplateDesign, EmailTemplateDesignAdmin)
admin.site.register(EmailAndWebAnalytics, EmailAndWebAnalyticsAdmin)
admin.site.register(LandingPageFormData, LandingPageFormDataAdmin)
admin.site.register(CampaignTemplateDesign, CampaignTemplateDesignAdmin)
