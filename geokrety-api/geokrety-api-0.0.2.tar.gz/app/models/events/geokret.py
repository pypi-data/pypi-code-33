import json

from sqlalchemy import inspect

from app.views.pika_ import pika_
from geokrety_api_models import Geokret

MONITORED_ATTRIBUTES = [
    'tracking_code',
    '_name',
    '_description',
    'type',
    'missing',
    'distance',
    'caches_count',
    'pictures_count',
    'updated_on_datetime',
    'owner_id',
    'holder_id',
    'last_position_id',
    'last_move_id',
]


def _has_changes_that_need_event(instance):
    instance_attrs = inspect(instance).attrs
    for attribute in MONITORED_ATTRIBUTES:
        if hasattr(instance_attrs, attribute) and \
                getattr(instance_attrs, attribute).history.has_changes():
            return True


def after_flush_geokret(session, flush_context):
    for instance in session.new:
        if not isinstance(instance, Geokret):
            continue
        payload = {
            'geokrety': [instance.id]
        }
        with pika_.pool.acquire() as cxn:
            cxn.channel.basic_publish(exchange='geokrety',
                                      routing_key="geokrety.geokret.insert",
                                      body=json.dumps(payload))

    for instance in session.dirty:
        if not isinstance(instance, Geokret):
            continue
        payload = {
            'geokrety': [instance.id]
        }
        with pika_.pool.acquire() as cxn:
            if _has_changes_that_need_event(instance):
                cxn.channel.basic_publish(exchange='geokrety',
                                          routing_key="geokrety.geokret.update",
                                          body=json.dumps(payload))

    for instance in session.deleted:
        if not isinstance(instance, Geokret):
            continue
        payload = {
            'geokrety': [instance.id]
        }
        with pika_.pool.acquire() as cxn:
            cxn.channel.basic_publish(exchange='geokrety',
                                      routing_key="geokrety.geokret.delete",
                                      body=json.dumps(payload))
