"""
Here all the signals related with the Package module.
"""
import logging
logger = logging.getLogger(__name__)


def signal_push_package_to_stripe(sender, **kwargs):
    """Signal: Push the package info to stripe account"""
    package = kwargs.get('instance')
    # Synchronize (update or create) the package in Stripe. if package.is_active
    package.push_to_stripe()
    logger.info("signal_push_package_to_stripe({}) executed!".format(package.title))


def signal_delete_package_in_stripe(sender, **kwargs):
    """Signal: Delete the package in Stripe."""
    package = kwargs.get('instance')
    package.delete_in_stripe()


def signal_delete_twilio_number(sender, **kwargs):
    """Release/delete twilio number phone from the account."""
    tw_number = kwargs.get('instance')
    tw_number.release_twilio_number()
