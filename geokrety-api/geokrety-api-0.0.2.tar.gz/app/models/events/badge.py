
from app.views.pika_ import pika_
from geokrety_api_models import Badge


def after_flush_badge(session, flush_context):
    for instance in session.new:
        if not isinstance(instance, Badge):
            continue
        with pika_.pool.acquire() as cxn:
            cxn.channel.basic_publish(exchange='geokrety',
                                      routing_key="geokrety.badge.insert",
                                      body=u"badge_id:{0.id}"
                                      u"name:{0.name}".format(instance))

    for instance in session.dirty:
        if not isinstance(instance, Badge):
            continue
        with pika_.pool.acquire() as cxn:
            cxn.channel.basic_publish(exchange='geokrety',
                                      routing_key="geokrety.badge.update",
                                      body=u"badge_id:{0.id}"
                                      u"name:{0.name}".format(instance))

    for instance in session.deleted:
        if not isinstance(instance, Badge):
            continue
        with pika_.pool.acquire() as cxn:
            cxn.channel.basic_publish(exchange='geokrety',
                                      routing_key="geokrety.badge.delete",
                                      body=u"badge_id:{0.id}"
                                      u"name:{0.name}".format(instance))
