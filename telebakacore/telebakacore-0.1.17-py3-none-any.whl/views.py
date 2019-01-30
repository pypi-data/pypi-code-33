import json

from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from jsonview.decorators import json_view
from raven.contrib.django.raven_compat.models import client
from telegram import Update

from bots.bots import dispatchers
from bots.models import TelegramBot


class WebhookView(View):
    @method_decorator(json_view)
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(WebhookView, self).dispatch(request, *args, **kwargs)

    def post(self, request, *args, pk, **kwargs):
        dispatcher = dispatchers[pk]
        update = Update.de_json(json.loads(request.body), dispatcher.bot)
        update.telegram_bot_pk = pk
        try:
            dispatcher.process_update(update)
        except Exception:
            client.captureException()
        return {}
