from django.contrib import admin

from ccc.billing.models import Customer, PaymentHistory, CurrentBalance


class PaymentAdmin(admin.ModelAdmin):

    # sets values for how the admin site lists your products
    list_display = (
        'user',
        'cost',
        'payer_id',
        'mode',
        'payment_id',
        'current',
        'recharge',
        'completed',
        'datetime',
        'package')
    # which of the fields in 'list_display' tuple link to admin product page
    list_display_links = ('user', 'payment_id')
    list_per_page = 50
    ordering = ['datetime']
    search_fields = ['payer_id', 'payment_id']
    #exclude = ('created_at', 'updated_at',)
    # sets up slug to be generated from product name


admin.site.register(PaymentHistory, PaymentAdmin)
admin.site.register(Customer)
admin.site.register(CurrentBalance)
