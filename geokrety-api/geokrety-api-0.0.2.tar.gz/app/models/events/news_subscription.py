

from app.views.pika_ import pika_
from geokrety_api_models import NewsSubscription


def after_flush_news_subscription(session, flush_context):
    for instance in session.new:
        if not isinstance(instance, NewsSubscription):
            continue
        with pika_.pool.acquire() as cxn:
            cxn.channel.basic_publish(exchange='geokrety',
                                      routing_key="geokrety.news-subscription.insert",
                                      body="news_subscription_id:{0.id}".format(instance))

    for instance in session.deleted:
        if not isinstance(instance, NewsSubscription):
            continue
        with pika_.pool.acquire() as cxn:
            cxn.channel.basic_publish(exchange='geokrety',
                                      routing_key="geokrety.news-subscription.delete",
                                      body="news_subscription_id:{0.id}".format(instance))
