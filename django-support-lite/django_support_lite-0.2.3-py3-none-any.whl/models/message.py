from django.contrib.auth.models import User
from django.db import models

from django_support_lite.models.ticket import Ticket


class Message(models.Model):
    id = models.AutoField(primary_key=True)
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField(max_length=100000)
    created_at = models.DateTimeField(auto_now_add=True)
