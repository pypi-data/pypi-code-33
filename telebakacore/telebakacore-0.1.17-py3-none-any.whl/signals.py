from django.conf import settings
from django.core.management import call_command
from django.db.models.signals import post_save
from django.dispatch import receiver

from bots.models import TelegramBot


@receiver(post_save, sender=TelegramBot)
def post_telegram_bot_save(sender, instance: TelegramBot, **kwargs):
    if not settings.DEBUG:
        call_command('set_webhooks')
