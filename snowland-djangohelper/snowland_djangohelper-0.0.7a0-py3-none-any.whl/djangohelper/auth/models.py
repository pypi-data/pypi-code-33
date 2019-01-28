from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """
    用户表
    """
    USER_ROLE_CHOICES = (
        ('SU', 'SuperUser'),
        ('GA', 'GroupAdmin'),
        ('CU', 'CommonUser'),
    )
    telephone = models.CharField(max_length=15, unique=True)
    sex = models.CharField(max_length=2, default='F')
    realname = models.CharField(max_length=15, blank=True)

