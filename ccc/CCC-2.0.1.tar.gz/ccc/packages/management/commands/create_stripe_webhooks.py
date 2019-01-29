"""
This custom command create programatically the webhooks(urls) in stripe, the endpoints were
will hear about Stripe information
"""
import stripe
from django.conf import settings
from django.contrib.sites.models import Site
from django.core.management.base import BaseCommand

from ccc.packages.webhooks.settings import STRIPE_WEB_HOOKS_ENDPOINTS

site = Site.objects.get_current().domain


def confirmation():
    return input('Please put the secret key of the stripe account when you want to push this webhooks:')


def push_to_stripe(webhook, key):
    """Create webhook in stripe"""
    stripe.api_key = key

    endpoint = "https://{}{}".format(site, webhook.get('url'))
    enabled_events = webhook.get('enabled_events')
    print(endpoint)
    stripe.WebhookEndpoint.create(
        url=endpoint,
        enabled_events=enabled_events
    )
    return endpoint, enabled_events


class Command(BaseCommand):
    help = "Create programatically all the stripe webhooks appending the Sites.domain."

    def handle(self, *args, **kwargs):
        self.stdout.write(
            self.style.ERROR(
                "Take care!. PLEASE before continue... Check that you are pushing the webhooks "
                "to the correct Stripe Account.\n \n "
                "The current os environment STRIPE (ACCOUNT) is -----> {} <------\n\n".format(
                    settings.STRIPE_SECRET_KEY)))

        stripe_key = confirmation()

        if len(stripe_key) > 5:
            _key = stripe_key.strip()

            for webhook in STRIPE_WEB_HOOKS_ENDPOINTS:
                try:
                    self.stdout.write(webhook.get('url'))
                    endpoint, enabled_events = push_to_stripe(webhook, _key)
                    self.stdout.write(
                        self.style.SUCCESS("{} \n SUCCESSFULL. endpoint:{} \n Enabled events:{} \n".format(
                            ":"*20, endpoint, enabled_events, "::"*20
                        ))
                    )
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR("{} \n ERROR. endpoint:{} \n Enabled events:{} \n".format(
                            ":" * 20, webhook.get('url'), webhook.get('enabled_events'), "::" * 20
                        ))
                    )
                    raise e


