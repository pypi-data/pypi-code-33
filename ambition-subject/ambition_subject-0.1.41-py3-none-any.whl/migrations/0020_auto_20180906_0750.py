# Generated by Django 2.1 on 2018-09-06 05:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ambition_subject', '0019_auto_20180814_0417'),
    ]

    operations = [
        migrations.AlterField(
            model_name='historicalsubjectconsent',
            name='identity_type',
            field=models.CharField(choices=[('country_id', 'Country ID number'), ('drivers', "Driver's license"), ('passport', 'Passport'), ('hospital_no', 'Hospital number'), ('country_id_rcpt', 'Country ID receipt'), ('OTHER', 'Other')], max_length=25, verbose_name='What type of identity number is this?'),
        ),
        migrations.AlterField(
            model_name='subjectconsent',
            name='identity_type',
            field=models.CharField(choices=[('country_id', 'Country ID number'), ('drivers', "Driver's license"), ('passport', 'Passport'), ('hospital_no', 'Hospital number'), ('country_id_rcpt', 'Country ID receipt'), ('OTHER', 'Other')], max_length=25, verbose_name='What type of identity number is this?'),
        ),
    ]
