from django.contrib import admin

from .models import Credit, ExternalBundle, ExternalCredit, Limit


#
# Declare admin models
#

class CreditAdmin(admin.ModelAdmin):
    list_display = ['id', 'limit', 'external', 'time_credit', 'volume_credit']


class ExternalBundleAdmin(admin.ModelAdmin):
    list_display = ['id', 'parser', 'external_key', 'service', 'time_credit', 'volume_credit']


class ExternalCreditAdmin(admin.ModelAdmin):
    list_display = ['label', 'external_code', 'bundle_key', 'account_name', 'is_converted', 'error_message']


class LimitAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'service', 'is_active', 'renewal_date', 'expiry_date', 'volume_total', 'time_total']
    list_filter = ['service', 'renewal_date', 'user']

#
# Register admin models
#

admin.site.register(Credit, CreditAdmin)
admin.site.register(ExternalBundle, ExternalBundleAdmin)
admin.site.register(ExternalCredit, ExternalCreditAdmin)
admin.site.register(Limit, LimitAdmin)
