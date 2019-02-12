from django.contrib import admin

from django_saml2_framework.models import AttributeMap, AttributeMapField
from django_saml2_framework.models import IdentityAttribute, IdentityMetadata, IdentityProvider
from django_saml2_framework.models import ServiceAttribute, ServiceMetadata, ServiceProvider


class ProviderAdminMixin(object):
    pass


class IdentityMetadataInline(admin.TabularInline):
    model = IdentityMetadata
    extra = 0


class IdentityAttributeInline(admin.TabularInline):
    model = IdentityAttribute
    extra = 0


@admin.register(IdentityProvider)
class IdentityProviderAdmin(ProviderAdminMixin, admin.ModelAdmin):
    list_display = ('name', 'entity', 'is_default')
    inlines = (IdentityMetadataInline, IdentityAttributeInline)


class ServiceMetadataInline(admin.TabularInline):
    model = ServiceMetadata
    extra = 0


class ServiceAttributeInline(admin.TabularInline):
    model = ServiceAttribute
    extra = 0


@admin.register(ServiceProvider)
class ServiceProviderAdmin(admin.ModelAdmin):
    list_display = ('name', 'entity', 'is_default')
    inlines = (ServiceMetadataInline, ServiceAttributeInline)


class AttributeMapFieldInline(admin.TabularInline):
    model = AttributeMapField
    extra = 0


@admin.register(AttributeMap)
class AttributeMapAdmin(admin.ModelAdmin):
    list_display = ('name', 'format')
    inlines = (AttributeMapFieldInline,)
