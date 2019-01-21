"""Peewee migrations -- 001_auto.py.

Some examples (model - class or model name)::

    > Model = migrator.orm['model_name']            # Return model in current state by name

    > migrator.sql(sql)                             # Run custom SQL
    > migrator.python(func, *args, **kwargs)        # Run python code
    > migrator.create_model(Model)                  # Create a model (could be used as decorator)
    > migrator.remove_model(model, cascade=True)    # Remove a model
    > migrator.add_fields(model, **fields)          # Add fields to a model
    > migrator.change_fields(model, **fields)       # Change fields
    > migrator.remove_fields(model, *field_names, cascade=True)
    > migrator.rename_field(model, old_field_name, new_field_name)
    > migrator.rename_table(model, new_table_name)
    > migrator.add_index(model, *col_names, unique=False)
    > migrator.drop_index(model, *col_names)
    > migrator.add_not_null(model, *field_names)
    > migrator.drop_not_null(model, *field_names)
    > migrator.add_default(model, field_name, default)

"""

import datetime as dt
import peewee as pw

try:
    import playhouse.postgres_ext as pw_pext
except ImportError:
    pass

SQL = pw.SQL


def migrate(migrator, database, fake=False, **kwargs):
    """Write your migrations here."""

    @migrator.create_model
    class Client(pw.Model):
        id = pw.AutoField()
        name = pw.CharField(max_length=128, unique=True)
        secret = pw.CharField(max_length=128)
        role = pw.CharField(max_length=16)

        class Meta:
            table_name = "client"

    @migrator.create_model
    class Job(pw.Model):
        id = pw.AutoField()
        client = pw.ForeignKeyField(backref='jobs', column_name='client_id', field='id', model=migrator.orm['client'])
        state = pw.CharField(index=True, max_length=32)
        added_moment = pw.DateTimeField()
        started_moment = pw.DateTimeField(null=True)
        ended_moment = pw.DateTimeField(null=True)
        timeout = pw.IntegerField(constraints=[SQL("DEFAULT 60")])
        error = pw.CharField(constraints=[SQL("DEFAULT ''")], max_length=256)
        continue_on_failure = pw.BooleanField(constraints=[SQL("DEFAULT False")])
        flash_images_json = pw.TextField()
        test_cases_json = pw.TextField()
        results_json = pw.TextField(null=True)

        class Meta:
            table_name = "job"



def rollback(migrator, database, fake=False, **kwargs):
    """Write your rollback migrations here."""

    migrator.remove_model('job')

    migrator.remove_model('client')
