from sqlalchemy import event

from geokret import after_flush_geokret
from badge import after_flush_badge
from move import after_flush_move
from move_comment import after_flush_move_comment
from news import after_flush_news
from news_comment import after_flush_news_comment
from news_subscription import after_flush_news_subscription
from user import after_flush_user


def register_database_events(db):
    event.listen(db.session, 'after_flush', after_flush_geokret)
    event.listen(db.session, 'after_flush', after_flush_badge)
    event.listen(db.session, 'after_flush', after_flush_move)
    event.listen(db.session, 'after_flush', after_flush_move_comment)
    event.listen(db.session, 'after_flush', after_flush_news)
    event.listen(db.session, 'after_flush', after_flush_news_comment)
    event.listen(db.session, 'after_flush', after_flush_news_subscription)
    event.listen(db.session, 'after_flush', after_flush_user)
