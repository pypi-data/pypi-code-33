"""
Listing all webhooks defined in the stripe account.
"""
from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Listing all webhooks defined in the stripe account"

    def handle(self, *args, **kwargs):
        import stripe
        stripe.api_key = settings.STRIPE_SECRET_KEY

        for w in stripe.WebhookEndpoint.list():
            self.stdout.write(
                self.style.SUCCESS("{}".format(w.url)))

