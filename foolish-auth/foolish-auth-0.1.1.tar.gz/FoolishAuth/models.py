# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import AbstractBaseUser


class User(AbstractBaseUser):
    username = models.CharField(
        max_length=150,
        null=False,
        unique=True)

    USERNAME_FIELD = 'username'

    class Meta:
        managed = False
        verbose_name = '用户'
        verbose_name_plural = '用户'

    def save(self, *args, **kwargs):
        # do not really save
        pass


