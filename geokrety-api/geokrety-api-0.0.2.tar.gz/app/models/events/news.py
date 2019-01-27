

from app.views.pika_ import pika_
from geokrety_api_models import News


def after_flush_news(session, flush_context):
    for instance in session.new:
        if not isinstance(instance, News):
            continue
        with pika_.pool.acquire() as cxn:
            cxn.channel.basic_publish(exchange='geokrety',
                                      routing_key="geokrety.news.insert",
                                      body="news_id:{0.id}".format(instance))

    for instance in session.dirty:
        if not isinstance(instance, News):
            continue
        with pika_.pool.acquire() as cxn:
            cxn.channel.basic_publish(exchange='geokrety',
                                      routing_key="geokrety.news.update",
                                      body="news_id:{0.id}".format(instance))

    for instance in session.deleted:
        if not isinstance(instance, News):
            continue
        with pika_.pool.acquire() as cxn:
            cxn.channel.basic_publish(exchange='geokrety',
                                      routing_key="geokrety.news.delete",
                                      body="news_id:{0.id}".format(instance))
