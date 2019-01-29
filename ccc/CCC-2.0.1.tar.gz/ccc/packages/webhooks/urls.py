from django.conf.urls import url

from ccc.packages.webhooks import stripe

urlpatterns_stripe_webhooks = [
    url(r'^stripe_webhook_payment_succeeded/$', stripe.PaymentSucceededView.as_view(),
        name='stripe_webhook_succeeded'),

    url(r'^stripe_webhook_payment_failed/$', stripe.PaymentFailedView.as_view(),
        name='stripe_webhook_failed'),

    url(r'^stripe_webhook_subscription_deleted/$', stripe.SubscriptionDeletedView.as_view(),
        name='stripe_webhook_subscription_deleted'),

    url(r'^stripe_webhook_invoice_created/$', stripe.InvoiceCreatedView.as_view(),
        name='stripe_webhook_invoice_created'),
]
