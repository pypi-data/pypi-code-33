# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-03-28 11:34
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('filer', '0003_thumbnailoption'),
    ]

    operations = [
        migrations.AlterField(
            model_name='image',
            name='subject_location',
            field=models.CharField(blank=True, default='', max_length=64, verbose_name='subject location'),
        ),
    ]
