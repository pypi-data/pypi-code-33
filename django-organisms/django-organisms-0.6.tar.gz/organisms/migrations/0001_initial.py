# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Organism',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('taxonomy_id', models.PositiveIntegerField(help_text=b'Taxonomy ID assigned by NCBI', unique=True, db_index=True)),
                ('common_name', models.CharField(help_text=b"Organism common name, e.g. 'Human'", unique=True, max_length=60)),
                ('scientific_name', models.CharField(help_text=b"Organism scientific/binomial name, e.g. 'Homo sapiens'", unique=True, max_length=60)),
                ('slug', models.SlugField(help_text=b'URL slug created by calling slugify() on scientific_name in the management command when the organism is added', unique=True)),
            ],
        ),
    ]
