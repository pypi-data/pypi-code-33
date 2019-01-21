# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2018-11-09 05:36
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bee_django_crm', '0013_preusercontract_finish_at'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='preuserfee',
            options={'ordering': ['-paid_at', '-created_at'], 'permissions': (('add_crm_preuser_fee', '\u53ef\u4ee5\u6dfb\u52a0\u7528\u6237\u7f34\u8d39'), ('view_crm_preuser_fee', '\u53ef\u4ee5\u67e5\u770b\u7528\u6237\u7f34\u8d39'), ('can_check_crm_preuser_fee', '\u53ef\u4ee5\u5ba1\u6838\u7528\u6237\u7f34\u8d39'), ('can_after_checked_fee', '\u5ba1\u6838\u7f34\u8d39\u540e\u53ef\u4ee5\u540e\u7eed\u64cd\u4f5c'))},
        ),
    ]
