import logging

from django.core.management import base as management_base, CommandError
from queue import Queue
from telegram import Update
from telegram.ext import Updater

from bots.models import TelegramBot
from bots.utils import get_plugins


class Command(management_base.BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('telegram_bot_pk', type=str)

    def handle(self, *args, telegram_bot_pk, **options):
        logging.basicConfig(level=logging.DEBUG,
                            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        try:
            telegram_bot = TelegramBot.objects.get(pk=telegram_bot_pk)
        except TelegramBot.DoesNotExist:
            raise CommandError(f'TelegramBot #{telegram_bot_pk} was not found')

        plugins = get_plugins()
        try:
            updater = Updater(telegram_bot.token)
            plugins[telegram_bot.plugin_name].bot.setup(updater.dispatcher)
        except KeyError:
            raise CommandError(f'Module {telegram_bot.plugin_name} was not found')

        class CustomQueue(Queue):
            def put(self, item, block=True, timeout=None):
                if isinstance(item, Update):
                    item.telegram_bot_pk = telegram_bot_pk
                return super(CustomQueue, self).put(item, block, timeout)

        updater.update_queue = updater.dispatcher.update_queue = CustomQueue()

        print('Starting polling...')
        if updater.bot.get_webhook_info().url:
            if input('Webhook is set for this token. Continue? [Y/n]') not in ['y', 'Y', '']:
                raise CommandError("Cancelled by user.")
        updater.start_polling(timeout=2)
        updater.idle()
