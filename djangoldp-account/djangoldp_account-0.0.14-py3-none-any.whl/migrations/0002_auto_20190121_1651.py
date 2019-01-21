# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2019-01-21 16:51
from __future__ import unicode_literals

from django.db import migrations, models

def migrate_data(apps, schema_editor):
    ChatProfile = apps.get_model('djangoldp_account', 'ChatProfile')
    for profile in ChatProfile.objects.all():
        profile.jabberID = profile.config.jabberID

class Migration(migrations.Migration):

    dependencies = [
        ('djangoldp_account', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='chatprofile',
            name='jabberID',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='chatprofile',
            name='jabberRoom',
            field=models.BooleanField(default=True),
        ),
        migrations.RunPython(migrate_data),
    ]
