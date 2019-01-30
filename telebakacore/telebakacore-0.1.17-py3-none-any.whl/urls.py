from django.db import DatabaseError
from django.urls import path, include

from bots.models import TelegramBot
from bots.utils import get_plugins

app_name = 'bots'

urlpatterns = []

plugins = get_plugins()
try:
    for telegram_bot in TelegramBot.objects.all():
        if telegram_bot.url_prefix:
            urlpatterns.append(path(f'{telegram_bot.url_prefix}/',
                                    include(plugins[telegram_bot.plugin_name].urls, namespace=str(telegram_bot.pk))))
except DatabaseError as e:
    print(e)
