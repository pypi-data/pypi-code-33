

from app.views.pika_ import pika_
from geokrety_api_models import NewsComment


def after_flush_news_comment(session, flush_context):
    for instance in session.new:
        if not isinstance(instance, NewsComment):
            continue
        with pika_.pool.acquire() as cxn:
            cxn.channel.basic_publish(exchange='geokrety',
                                      routing_key="geokrety.news-comment.insert",
                                      body="news_comment_id:{0.id}".format(instance))

    for instance in session.dirty:
        if not isinstance(instance, NewsComment):
            continue
        with pika_.pool.acquire() as cxn:
            cxn.channel.basic_publish(exchange='geokrety',
                                      routing_key="geokrety.news-comment.update",
                                      body="news_comment_id:{0.id}".format(instance))

    for instance in session.deleted:
        if not isinstance(instance, NewsComment):
            continue
        with pika_.pool.acquire() as cxn:
            cxn.channel.basic_publish(exchange='geokrety',
                                      routing_key="geokrety.news-comment.delete",
                                      body="news_comment_id:{0.id}".format(instance))
