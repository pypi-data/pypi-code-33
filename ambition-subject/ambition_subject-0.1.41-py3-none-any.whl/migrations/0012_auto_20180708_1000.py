# Generated by Django 2.0.7 on 2018-07-08 07:43

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ambition_subject', '0011_auto_20180708_0943'),
    ]

    operations = [
        migrations.AddField(
            model_name='followup',
            name='antibiotic',
            field=models.ManyToManyField(blank=True, to='ambition_lists.Antibiotic',
                                         verbose_name='Were any of the following antibiotics given?'),
        ),
        migrations.AddField(
            model_name='followup',
            name='antibiotic_other',
            field=models.CharField(blank=True, max_length=50, null=True,
                                   verbose_name='If other antibiotics, please specify:'),
        ),
        migrations.AddField(
            model_name='followup',
            name='blood_transfusions',
            field=models.CharField(choices=[('Yes', 'Yes'), ('No', 'No')], max_length=5, null=True,
                                   verbose_name='Has the patient had any blood transfusions since week two? '),
        ),
        migrations.AddField(
            model_name='followup',
            name='blood_transfusions_units',
            field=models.DecimalField(
                decimal_places=3, max_digits=5, null=True, verbose_name='If YES, no. of units?    '),
        ),
        migrations.AddField(
            model_name='followup',
            name='days_hospitalized',
            field=models.DecimalField(decimal_places=3, max_digits=5, null=True,
                                      verbose_name='Over the ten weeks spent in the study how many days did the patient spend in hospital?'),
        ),
        migrations.AddField(
            model_name='historicalfollowup',
            name='antibiotic_other',
            field=models.CharField(blank=True, max_length=50, null=True,
                                   verbose_name='If other antibiotics, please specify:'),
        ),
        migrations.AddField(
            model_name='historicalfollowup',
            name='blood_transfusions',
            field=models.CharField(choices=[('Yes', 'Yes'), ('No', 'No')], max_length=5, null=True,
                                   verbose_name='Has the patient had any blood transfusions since week two? '),
        ),
        migrations.AddField(
            model_name='historicalfollowup',
            name='blood_transfusions_units',
            field=models.DecimalField(
                decimal_places=3, max_digits=5, null=True, verbose_name='If YES, no. of units?    '),
        ),
        migrations.AddField(
            model_name='historicalfollowup',
            name='days_hospitalized',
            field=models.DecimalField(decimal_places=3, max_digits=5, null=True,
                                      verbose_name='Over the ten weeks spent in the study how many days did the patient spend in hospital?'),
        ),
        migrations.AlterField(
            model_name='historicalmedicalexpenses',
            name='someone_spent_last_4wks',
            field=models.DecimalField(decimal_places=2, help_text='On D1 record data for the four weeks prior to recruitment. On W10 record data for the ten weeks since recruitment.', max_digits=15, null=True, validators=[
                                      django.core.validators.MinValueValidator(0)], verbose_name='Over the last 4/10 weeks, how much has someone else spent on activities relating to your health?'),
        ),
        migrations.AlterField(
            model_name='historicalmedicalexpenses',
            name='subject_spent_last_4wks',
            field=models.DecimalField(decimal_places=2, help_text='On D1 record data for the four weeks prior to recruitment. On W10 record data for the ten weeks since recruitment.', max_digits=15, null=True, validators=[
                                      django.core.validators.MinValueValidator(0)], verbose_name='Over the last 4/10 weeks, how much have you spent on activities relating to your health?'),
        ),
        migrations.AlterField(
            model_name='historicalmedicalexpenses',
            name='total_spent_last_4wks',
            field=models.DecimalField(decimal_places=2, help_text='On D1 record data for the four weeks prior to recruitment. On W10 record data for the ten weeks since recruitment.', max_digits=16, null=True, validators=[
                                      django.core.validators.MinValueValidator(0)], verbose_name='How much in total has been spent on your healthcare in the last 4/10 weeks?'),
        ),
        migrations.AlterField(
            model_name='medicalexpenses',
            name='someone_spent_last_4wks',
            field=models.DecimalField(decimal_places=2, help_text='On D1 record data for the four weeks prior to recruitment. On W10 record data for the ten weeks since recruitment.', max_digits=15, null=True, validators=[
                                      django.core.validators.MinValueValidator(0)], verbose_name='Over the last 4/10 weeks, how much has someone else spent on activities relating to your health?'),
        ),
        migrations.AlterField(
            model_name='medicalexpenses',
            name='subject_spent_last_4wks',
            field=models.DecimalField(decimal_places=2, help_text='On D1 record data for the four weeks prior to recruitment. On W10 record data for the ten weeks since recruitment.', max_digits=15, null=True, validators=[
                                      django.core.validators.MinValueValidator(0)], verbose_name='Over the last 4/10 weeks, how much have you spent on activities relating to your health?'),
        ),
        migrations.AlterField(
            model_name='medicalexpenses',
            name='total_spent_last_4wks',
            field=models.DecimalField(decimal_places=2, help_text='On D1 record data for the four weeks prior to recruitment. On W10 record data for the ten weeks since recruitment.', max_digits=16, null=True, validators=[
                                      django.core.validators.MinValueValidator(0)], verbose_name='How much in total has been spent on your healthcare in the last 4/10 weeks?'),
        ),
    ]
