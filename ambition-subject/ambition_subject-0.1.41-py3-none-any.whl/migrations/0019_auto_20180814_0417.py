# Generated by Django 2.1 on 2018-08-14 02:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ambition_subject', '0018_auto_20180814_0313'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='subjectconsent',
            options={'get_latest_by': 'consent_datetime', 'ordering': ('created',)},
        ),
    ]
