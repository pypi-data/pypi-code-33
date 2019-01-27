from datetime import datetime

from backend.entity import Entity, db


class User(db.Model, Entity):
    __tablename__ = 'user'
    id = db.Column(db.BigInteger, db.Sequence('co_user_id_seq'), primary_key=True)
    phone_number = db.Column(db.String(20), nullable=False, index=True)
    username = db.Column(db.String(60), nullable=False, index=True)
    fullname = db.Column(db.String(100), nullable=False, index=True)
    business_name = db.Column(db.Text, nullable=False, index=True, server_default=' ', default=' ')
    hash_password = db.Column(db.LargeBinary(60), nullable=False)
    enabled = db.Column(db.Boolean, nullable=False, default=False)
    account_non_expired = db.Column(db.Boolean, nullable=False, default=False)
    account_non_locked = db.Column(db.Boolean, nullable=False, default=False)
    credentials_non_expired = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime(timezone=False), default=datetime.now)
    update_at = db.Column(db.DateTime(timezone=False), onupdate=datetime.now)

    __json_hidden__ = ['hash_password', 'enabled', 'account_non_expired', 'account_non_locked',
                       'credentials_non_expired']

    def __init__(self, obj=None):
        Entity.__init__(self, obj)
