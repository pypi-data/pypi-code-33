from django.contrib import admin

from .admin_site import encryption_admin
from .models import Crypt


@admin.register(Crypt, site=encryption_admin)
class CryptModelAdmin(admin.ModelAdmin):

    date_hierarchy = "modified"

    fields = sorted([field.name for field in Crypt._meta.fields])

    readonly_fields = [field.name for field in Crypt._meta.fields]

    list_display = ("algorithm", "hash", "modified", "hostname_modified")

    list_filter = ("algorithm", "modified", "hostname_modified")

    search_fields = ("hash",)
