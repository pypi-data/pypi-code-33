from django.db import models


class PlannedPost(models.Model):
    bot = models.ForeignKey('bots.TelegramBot', on_delete=models.CASCADE)
    update = models.TextField()
