
from sqlalchemy import inspect

from app.views.pika_ import pika_
from geokrety_api_models import Move


def _has_changes_that_need_recompute(instance):
    if inspect(instance).attrs.type.history.has_changes() or \
            inspect(instance).attrs.moved_on_datetime.history.has_changes() or \
            inspect(instance).attrs.geokret.history.has_changes():
        return True


def after_flush_move(session, flush_context):
    for instance in session.new:
        if not isinstance(instance, Move):
            continue
        with pika_.pool.acquire() as cxn:
            cxn.channel.basic_publish(exchange='geokrety',
                                      routing_key="geokrety.move.insert",
                                      body="geokret_id:{0.geokret.id} "
                                      "move_id:{0.id} "
                                      "move_type:{0.type} "
                                      "user_id:{0.author.id}".format(instance))

    for instance in session.dirty:
        if not isinstance(instance, Move):
            continue
        if _has_changes_that_need_recompute(instance):
            with pika_.pool.acquire() as cxn:
                cxn.channel.basic_publish(exchange='geokrety',
                                          routing_key="geokrety.move.update",
                                          body="geokret_id:{0.geokret.id} "
                                          "move_id:{0.id} "
                                          "move_type:{0.type} "
                                          "user_id:{0.author.id}".format(instance))
                if inspect(instance).attrs.geokret.history.has_changes():
                    for old_geokret_id in inspect(instance).attrs.geokret.history[2]:
                        cxn.channel.basic_publish(exchange='geokrety',
                                                  routing_key="geokrety.move.update",
                                                  body="geokret_id:{1} "
                                                  "move_id:{0.id} "
                                                  "move_type:{0.type} "
                                                  "user_id:{0.author.id}".format(instance, old_geokret_id))

    for instance in session.deleted:
        if not isinstance(instance, Move):
            continue
        with pika_.pool.acquire() as cxn:
            cxn.channel.basic_publish(exchange='geokrety',
                                      routing_key="geokrety.move.delete",
                                      body="geokret_id:{0.geokret.id} "
                                      "move_id:{0.id} "
                                      "move_type:{0.type} "
                                      "user_id:{0.author.id}".format(instance))
