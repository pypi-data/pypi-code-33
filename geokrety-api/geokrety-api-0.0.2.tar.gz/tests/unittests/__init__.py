
from sqlalchemy import inspect

from app import current_app
from app.models import db


def setUp():
    with current_app.app_context():
        inspector = inspect(db.engine)
        db.session.execute('SET FOREIGN_KEY_CHECKS = 0;')
        db.session.execute("""SELECT CONCAT('DROP TABLE ', TABLE_NAME, ';')
                            FROM INFORMATION_SCHEMA.tables
                            WHERE TABLE_SCHEMA = '{}'"""
                           .format(inspector.default_schema_name)
                           )
        db.session.execute('SET FOREIGN_KEY_CHECKS = 1;')
