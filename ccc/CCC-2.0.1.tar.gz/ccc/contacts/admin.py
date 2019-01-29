# -*- coding: utf-8 -*-
from django.contrib import admin

from ccc.contacts.models import (CompanySocialProfile, Contact, ContactCheckin,
                                 ContactGroup, ContactProperty,
                                 ContactSocialProfile, RemoveDomainSearch, ContactNote)


class ContactPropertyInline(admin.TabularInline):
    model = ContactProperty
    extra = 0


class ContactAdmin(admin.ModelAdmin):
    search_fields = ['phone', ]
    list_display = ['user', 'phone', 'first_name', 'last_name', 'email',
                    'company_name', 'lead_type', 'contact_type', 'social_id',
                    'updated_at']
    list_filter = ['user', 'lead_type', 'contact_type']
    inlines = [ContactPropertyInline]


class ContactPropertyAdmin(admin.ModelAdmin):
    list_display = ['contact', 'name', 'value', 'created_at']


class ContactCheckinAdmin(admin.ModelAdmin):
    list_display = ['contact', 'campaign', 'created']


class ContactSocialProfileAdmin(admin.ModelAdmin):
    list_display = ['contact', 'website', 'bio', 'title', 'gender', 'twitter', 'linkedin', 'facebook', 'location',
                    'organization', 'avatar']


class CompanySocialProfileAdmin(admin.ModelAdmin):
    list_display = ['contact', 'website', 'bio', 'name', 'founded', 'twitter', 'linkedin', 'facebook', 'location',
                    'locale', 'logo', 'category', 'employees']


class RemoveDomainSearchAdmin(admin.ModelAdmin):
    list_display = ['domain_name']


class ContactGroupAdmin(admin.ModelAdmin):
    list_display = ['user', 'name', 'created_at', 'updated_at']
    search_fields = ['user', 'name']


admin.site.register(Contact, ContactAdmin)
admin.site.register(ContactProperty, ContactPropertyAdmin)
admin.site.register(ContactCheckin, ContactCheckinAdmin)
admin.site.register(ContactSocialProfile, ContactSocialProfileAdmin)
admin.site.register(ContactGroup, ContactGroupAdmin)
admin.site.register(CompanySocialProfile, CompanySocialProfileAdmin)
admin.site.register(RemoveDomainSearch, RemoveDomainSearchAdmin)
admin.site.register(ContactNote)
