# Generated by Django 2.1 on 2018-08-09 03:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ambition_subject', '0013_auto_20180717_1331'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bloodresult',
            name='tracking_identifier',
            field=models.CharField(max_length=30, unique=True),
        ),
        migrations.AlterField(
            model_name='historicalbloodresult',
            name='tracking_identifier',
            field=models.CharField(db_index=True, max_length=30),
        ),
        migrations.AlterField(
            model_name='historicalsubjectreconsent',
            name='tracking_identifier',
            field=models.CharField(db_index=True, max_length=30),
        ),
        migrations.AlterField(
            model_name='subjectreconsent',
            name='tracking_identifier',
            field=models.CharField(max_length=30, unique=True),
        ),
    ]
