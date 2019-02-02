import json
from celery import shared_task
from telegram import Update, Bot

from bots.models import TelegramBot
from telebaka_channel_helper.bot import post_update, post_updates
from telebaka_channel_helper.models import PlannedPost


@shared_task
def send_planned_posts():
    bots = PlannedPost.objects.values('bot').distinct()
    for bot in bots:
        bot_instance = TelegramBot.objects.get(pk=bot['bot'])
        bot = Bot(bot_instance.token)
        posts = PlannedPost.objects.filter(bot=bot_instance).order_by('?')
        if posts.count() > 100:
            group = posts[:10]
            post_updates(bot_instance, [Update.de_json(json.loads(post.update), bot) for post in group])
            group.delete()
        elif posts.count():
            post = posts.first()
            post_update(bot_instance, Update.de_json(json.loads(post.update), bot))
            post.delete()
