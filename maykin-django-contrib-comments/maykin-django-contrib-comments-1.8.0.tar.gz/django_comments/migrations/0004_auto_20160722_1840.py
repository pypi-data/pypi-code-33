# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('django_comments', '0003_add_submit_date_index'),
    ]

    state_operations = [
        migrations.operations.AlterField(
            model_name='comment',
            name='object_pk',
            field=models.PositiveIntegerField(verbose_name="object ID")
        )
    ]

    db_operations = [
        migrations.RunSQL([
            'ALTER TABLE "django_comments" ALTER COLUMN "object_pk" TYPE integer USING object_pk::integer;',
            'ALTER TABLE "django_comments" ADD CONSTRAINT "django_comments_object_pk_5c9578d83bf85384_check" CHECK ("object_pk" >= 0);',
        ])
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=db_operations, state_operations=state_operations
        )
    ]
