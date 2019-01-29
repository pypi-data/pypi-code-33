from django.conf.urls import url

from ccc.billing.views import (ChangeBillingInfoView, ChangeCardView,
                               PaymentDetailView, all_users, dash, delete_card,
                               payment_history, payment_history_search,
                               payments, stripe_pay, stripe_store)

app_name = 'billings'

urlpatterns = [
    url(r'^card-details/$', stripe_pay, name='stripe_pay'),
    url(r'^card-file/$', stripe_store, name='stripe_store'),
    url(r'^payments/$', payments, name='payments'),
    url(r'^delete-card/$', delete_card, name='delete_card'),
    url(r'^admin-dashboard/$', dash, name='dash'),
    url(r'^all-users/$', all_users, name='all'),
    url(r'^payments/(?P<pk>[0-9]+)/$', PaymentDetailView.as_view(), name='payment_detail_url'),
    url(r'^change_card/$', ChangeCardView.as_view(), name='change_card_view'),
    url(r'^change_billing_info/$', ChangeBillingInfoView.as_view(), name='change_billing_info_view'),
    url(r'^payment-history/$', payment_history, name='payment-history'),
    url(r'^payment-history/search/$', payment_history_search, name="payment_history_search"),
]
