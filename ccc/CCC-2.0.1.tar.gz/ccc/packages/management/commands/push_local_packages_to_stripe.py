"""
This command pushes the Packages information to Stripe, local packages information will be pushed to the Stripe.
Stripe also support webhooks for sync in two ways but this is an additional command very helpful that we can
call manually during development or in other scenarios when we are not sure if the data is sync or simply we
are running this during the setup data in a new instance the first time.
"""
from django.core.management.base import BaseCommand, CommandError
from ccc.packages.models import PackageType


class Command(BaseCommand):
    help = 'This command push the all current local packages to Stripe account.'

    def handle(self, *args, **options):
        for local_package in PackageType.objects.all():

            if local_package.is_active:
                local_package.push_to_stripe()

                self.stdout.write(
                    self.style.SUCCESS("Successfully pushed Package: {0} to Stripe SKU:'{1}'".format(
                        local_package.title, local_package.sku)))

            elif not local_package.is_active:
                self.stdout.write(
                    self.style.WARNING("Ignoring Package: {0} to Stripe SKU:'{1}'".format(
                        local_package.title, local_package.sku)))
