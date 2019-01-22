# Generated by Django 2.1.2 on 2018-10-29 00:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ambition_subject', '0032_auto_20181025_0218'),
    ]

    operations = [
        migrations.AlterField(
            model_name='followup',
            name='blood_transfusions_units',
            field=models.DecimalField(blank=True, decimal_places=3, max_digits=5, null=True, verbose_name='If YES, no. of units?    '),
        ),
        migrations.AlterField(
            model_name='historicalfollowup',
            name='blood_transfusions_units',
            field=models.DecimalField(blank=True, decimal_places=3, max_digits=5, null=True, verbose_name='If YES, no. of units?    '),
        ),
        migrations.AlterUniqueTogether(
            name='medicalexpensestwodetail',
            unique_together=set(),
        ),
    ]
