from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django_paymentsos.models import PaymentsOSNotification


class TestFilter(admin.SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = 'test'

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'test'

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        return [('test', _('Yes')), ('live', _('No'))]

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        # Compare the requested value (either '80s' or '90s')
        # to decide how to filter the queryset.
        if self.value():
            return queryset.filter(x_payments_os_env=self.value())


class PaymentsOSNotificationAdmin(admin.ModelAdmin):
    list_display = (
        'payment_id', 'event_type', 'reconciliation_id', 'result_status', 'test', 'flag', 'date_created'
    )
    list_filter = ('event_type', 'result_status', TestFilter, 'flag')
    search_fields = ['payment_id', 'reconciliation_id']
    fieldsets = (
        (None, {
            'fields': (
                'payment_id', 'data_id', 'reconciliation_id', 'amount', 'notification_created', 'currency', 'modified',
                'statement_soft_descriptor', 'status', 'date_created')
        }),
        (_('Notification'), {
            'classes': ('collapse',),
            'fields': (
                'webhook_id', 'payment_id', 'account_id', 'app_id', 'x_zooz_request_id', 'x_payments_os_env', 'version',
                'event_type', 'signature', 'created')
        }),
        (_('Result'), {
            'classes': ('collapse',),
            'fields': (
                'result_status', 'category', 'sub_category', 'result_description')
        }),
        (_('Payment Method'), {
            'classes': ('collapse',),
            'fields': (
                'type', 'token', 'token_type', 'holder_name', 'expiration_date', 'last_4_digits',
                'pass_luhn_validation', 'fingerprint', 'bin_number', 'vendor', 'issuer', 'card_type', 'level',
                'country_code', 'method_created', 'billing_address')
        }),
        (_('Provider Data'), {
            'classes': ('collapse',),
            'fields': (
                'provider_name', 'response_code', 'provider_description', 'raw_response', 'transaction_id',
                'external_id')
        }),
        (_('Provider Specific Data'), {
            'classes': ('collapse',),
            'fields': (
                'device_fingerprint', 'additional_details')
        }),
        (_('Admin'), {
            'classes': ('collapse',),
            'fields': (
                'flag', 'flag_code', 'flag_info', 'raw')
        })
    )
    readonly_fields = list(d for t in fieldsets for d in t[1]['fields'])

    def test(self, obj):
        return obj.is_test

    test.short_description = 'Test'
    test.boolean = True


admin.site.register(PaymentsOSNotification, PaymentsOSNotificationAdmin)
