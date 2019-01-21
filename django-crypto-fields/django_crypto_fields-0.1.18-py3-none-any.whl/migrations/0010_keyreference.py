# Generated by Django 2.0b1 on 2017-11-10 21:10

from django.db import migrations, models
import edc_base.utils


class Migration(migrations.Migration):

    dependencies = [("django_crypto_fields", "0009_auto_20170903_1532")]

    operations = [
        migrations.CreateModel(
            name="KeyReference",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("key_path", models.CharField(max_length=250)),
                ("key_filenames", models.TextField(null=True)),
                (
                    "created",
                    models.DateTimeField(default=edc_base.utils.get_utcnow, null=True),
                ),
            ],
        )
    ]
