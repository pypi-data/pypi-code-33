from django.db import models

from django_support_lite.models.message import Message


class Image(models.Model):
    id = models.AutoField(primary_key=True)
    message = models.ForeignKey(Message, on_delete=models.CASCADE)
    path = models.CharField(max_length=1024)
