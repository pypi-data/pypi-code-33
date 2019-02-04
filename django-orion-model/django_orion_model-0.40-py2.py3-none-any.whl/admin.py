from django.contrib import admin

# Register your models here.
from django.contrib.postgres import fields
from django_json_widget.widgets import JSONEditorWidget

from django_orion_model.models import ServicePath, ContextBroker, OrionEntity, Service



@admin.register(OrionEntity)
class OrionEntityAdmin(admin.ModelAdmin):
    formfield_overrides = {
        fields.JSONField: {'widget': JSONEditorWidget},
    }


@admin.register(ContextBroker)
class ContextBrokerAdmin(admin.ModelAdmin):
    pass


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    pass


@admin.register(ServicePath)
class ServicePathAdmin(admin.ModelAdmin):
    pass
