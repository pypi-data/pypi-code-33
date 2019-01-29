# coding: utf-8
from adminsortable.admin import SortableAdmin
from django.contrib import admin

from ccc.packages.models import (Credit, PackageType, PurchasedPackage,
                                 TwilioNumber)


class PackageTypeAdmin(SortableAdmin):
    """Package type Admin"""
    list_display = ('id', 'title', 'type', 'local',  'cost', 'trial_days', 'is_active', 'creator', 'last_updated',)
    list_display_links = ('id', 'title')
    list_per_page = 50
    search_fields = ['title', 'cost']
    list_filter = ['type', 'is_active']

    fieldsets = (
        ('Package info', {'fields': ('title', 'sku', 'type', 'local', 'is_active')}),
        ('Package cost', {'fields': ('cost', 'recurring')}),
        ('Trial', {'fields': ('trial_days', 'package_type_after_trial')}),
        ('Package features', {
            'fields': ('phones', 'sms', 'mms', 'email', 'talktime', 'digital_att', 'teams', 'is_twilio_number_included', 'social_media', 'campaigns', 'team', 'rover_min', 'scanner', 'scanner_cost')
        }),
        ('Other info', {'fields': ('creator',)}),
    )


class PackageAdmin(admin.ModelAdmin):
    # sets values for how the admin site lists your products
    list_display = ('id', 'user', 'type', 'paid', 'approved', 'created_at')
    # which of the fields in 'list_display' tuple link to admin product page
    list_display_links = ('id', 'user', 'type')
    list_per_page = 50
    ordering = ['id']
    search_fields = ['type']
    # exclude = ('created_at', 'updated_at',)
    # sets up slug to be generated from product name


admin.site.register(PurchasedPackage, PackageAdmin)




admin.site.register(PackageType, PackageTypeAdmin)


class TwNumberAdmin(admin.ModelAdmin):
    # sets values for how the admin site lists your products
    list_display = ('twilio_number', 'twilio_number_sid', 'user', 'in_use', 'is_redirected',
                    'sms_enabled', 'mms_enabled', 'voice_enabled', 'voice_url', 'sms_url', 'last_updated',)

    # which of the fields in 'list_display' tuple link to admin product page
    list_display_links = ('twilio_number',)
    list_per_page = 50
    ordering = ['-last_updated', 'user']
    search_fields = ['twilio_number']
    # exclude = ('created_at', 'updated_at',)
    # sets up slug to be generated from product NAME


admin.site.register(TwilioNumber, TwNumberAdmin)


class CreditAdmin(admin.ModelAdmin):
    # sets values for how the admin site lists your products
    list_display = ('id', 'package', 'sms', 'talktime', 'mms', 'email', 'date_created')
    # which of the fields in 'list_display' tuple link to admin product page
    list_display_links = ('id',)
    list_per_page = 50
    ordering = ['id']
    # search_fields = ['user']
    # exclude = ('created_at', 'updated_at',)
    # sets up slug to be generated from product name


admin.site.register(Credit, CreditAdmin)
