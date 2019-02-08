from django.contrib import admin

from django_saml2_framework.models import ServiceProvider, IdentityProvider, IdentityMetadata, ServiceMetadata, IdentityAttribute, ServiceAttribute


class ProviderAdminMixin(object):
    pass
    # actions = ['generate_key']

    # def generate_key(self, request, queryset):
    #     for provider in queryset.all():
    #         provider.generate_key()

    # generate_key.short_description = "Generate new key pair"

class IdentityMetadataInline(admin.TabularInline):
    model = IdentityMetadata
    extra = 0

class ServiceMetadataInline(admin.TabularInline):
    model = ServiceMetadata
    extra = 0

class IdentityAttributeInline(admin.TabularInline):
    model = IdentityAttribute
    extra = 0

class ServiceAttributeInline(admin.TabularInline):
    model = ServiceAttribute
    extra = 0


@admin.register(IdentityProvider)
class IdentityProviderAdmin(ProviderAdminMixin, admin.ModelAdmin):
    list_display = ('name', 'entity', 'is_default')
    inlines = (IdentityMetadataInline, IdentityAttributeInline)

@admin.register(ServiceProvider)
class ServiceProviderAdmin(admin.ModelAdmin):
    list_display = ('name', 'entity', 'is_default')
    inlines = (ServiceMetadataInline, ServiceAttributeInline)
