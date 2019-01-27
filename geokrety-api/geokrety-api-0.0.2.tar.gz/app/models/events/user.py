
from sqlalchemy import inspect

from app.views.pika_ import pika_
from geokrety_api_models import User

MONITORED_ATTRIBUTES = [
    '_name',
    'is_admin',
    '_password',
    'email',
    'daily_mails',
    'ip',
    'language',
    'latitude',
    'longitude',
    'observation_radius',
    'country',
    'hour',
    'statpic_id',
    'last_mail_datetime',
    'last_login_datetime',
    'last_update_datetime',
    'secid',
]


def _has_changes_that_need_event(instance):
    instance_attrs = inspect(instance).attrs
    for attribute in MONITORED_ATTRIBUTES:
        if hasattr(instance_attrs, attribute) and \
                getattr(instance_attrs, attribute).history.has_changes():
            return True


def after_flush_user(session, flush_context):
    for instance in session.new:
        if not isinstance(instance, User):
            continue
        with pika_.pool.acquire() as cxn:
            cxn.channel.basic_publish(exchange='geokrety',
                                      routing_key="geokrety.user.insert",
                                      body=u"user_id:{0.id} username:{0.name}".format(instance))

    for instance in session.dirty:
        if not isinstance(instance, User):
            continue
        with pika_.pool.acquire() as cxn:
            if _has_changes_that_need_event(instance):
                cxn.channel.basic_publish(exchange='geokrety',
                                          routing_key="geokrety.user.update",
                                          body=u"user_id:{0.id} username:{0.name}".format(instance))

    for instance in session.deleted:
        if not isinstance(instance, User):
            continue
        with pika_.pool.acquire() as cxn:
            cxn.channel.basic_publish(exchange='geokrety',
                                      routing_key="geokrety.user.delete",
                                      body=u"user_id:{0.id} username:{0.name}".format(instance))
