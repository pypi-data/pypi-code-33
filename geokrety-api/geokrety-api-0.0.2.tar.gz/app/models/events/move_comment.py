
from sqlalchemy import inspect

from app.views.pika_ import pika_
from geokrety_api_models import MoveComment


def _has_changes_that_need_recompute(instance):
    if inspect(instance).attrs.type.history.has_changes() or \
            inspect(instance).attrs.move.history.has_changes():
        return True


def after_flush_move_comment(session, flush_context):
    for instance in session.new:
        if not isinstance(instance, MoveComment):
            continue
        with pika_.pool.acquire() as cxn:
            cxn.channel.basic_publish(exchange='geokrety',
                                      routing_key="geokrety.move-comment.insert",
                                      body="geokret_id:{0.move.geokret.id} "
                                      "move_id:{0.move.id} "
                                      "move_type:{0.move.type} "
                                      "user_id:{0.move.author.id} "
                                      "move_comment_type:{0.type}".format(instance))

    for instance in session.dirty:
        if not isinstance(instance, MoveComment):
            continue
        if _has_changes_that_need_recompute(instance):
            with pika_.pool.acquire() as cxn:
                cxn.channel.basic_publish(exchange='geokrety',
                                          routing_key="geokrety.move-comment.update",
                                          body="geokret_id:{0.move.geokret.id} "
                                          "move_id:{0.move.id} "
                                          "move_type:{0.move.type} "
                                          "user_id:{0.move.author.id} "
                                          "move_comment_type:{0.type}".format(instance))
                if inspect(instance).attrs.move.history.has_changes():
                    for old_move_id in inspect(instance).attrs.move.history[2]:
                        cxn.channel.basic_publish(exchange='geokrety',
                                                  routing_key="geokrety.move-comment.update",
                                                  body="geokret_id:{0.move.geokret.id} "
                                                  "move_id:{1} "
                                                  "move_type:{0.move.type} "
                                                  "user_id:{0.move.author.id} "
                                                  "move_comment_type:{0.type}".format(instance, old_move_id))

    for instance in session.deleted:
        if not isinstance(instance, MoveComment):
            continue
        with pika_.pool.acquire() as cxn:
            cxn.channel.basic_publish(exchange='geokrety',
                                      routing_key="geokrety.move-comment.delete",
                                      body="geokret_id:{0.move.geokret.id} "
                                      "move_id:{0.move.id} "
                                      "move_type:{0.move.type} "
                                      "user_id:{0.move.author.id} "
                                      "move_comment_type:{0.type}".format(instance))
