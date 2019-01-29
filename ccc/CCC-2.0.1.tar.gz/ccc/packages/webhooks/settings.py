from django.urls import reverse_lazy

"""
STRIPE_WEB_HOOKS_ENDPOINTS:
This contains all the webhooks that we support. Adittionally this "constant" also is used by the
command util called "create_stripe_webhooks". this command create programmatically all our stripe webhooks.
Very util for development and deployment environment. Please, check the help text of that command.
"""

# https://dashboard.stripe.com/account/webhooks

STRIPE_WEB_HOOKS_ENDPOINTS = [
    {
        'url': reverse_lazy('srm:packages:stripe_webhook_succeeded'),
        'connected': True,
        'enabled_events': ['invoice.payment_succeeded']
    },
    {
        'url': reverse_lazy('srm:packages:stripe_webhook_failed'),
        'connected': True,
        'enabled_events': ['invoice.payment_failed']
    },
    {
        'url': reverse_lazy('srm:packages:stripe_webhook_subscription_deleted'),
        'connected': True,
        'enabled_events': ['customer.subscription.deleted']
    },
    {
        'url': reverse_lazy('srm:packages:stripe_webhook_invoice_created'),
        'connected': True,
        'enabled_events': ['invoice.created']
    },

]
