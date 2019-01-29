# -*- coding: utf-8 -*-

from peewee import Model, CharField


class VisitorModel(Model):
    class Meta:
        table_name = 'visitor'
        indexes = (
            (('name', 'ip_addr'), True),
        )

    name = CharField()
    ip_addr = CharField()
    location = CharField(null=True)
