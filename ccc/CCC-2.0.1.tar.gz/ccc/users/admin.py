from django.contrib import admin

from ccc.users.models import ActivationCode, AuditEntry, ResetCode, UserProfile


class AuditEntryAdmin(admin.ModelAdmin):
    list_display = ['action', 'username', 'ip', "created_at"]


class UserAdmin(admin.ModelAdmin):
    change_form_template = 'loginas/change_form.html'


admin.site.register(UserProfile, UserAdmin)
admin.site.register(AuditEntry, AuditEntryAdmin)
admin.site.register(ActivationCode)
admin.site.register(ResetCode)
