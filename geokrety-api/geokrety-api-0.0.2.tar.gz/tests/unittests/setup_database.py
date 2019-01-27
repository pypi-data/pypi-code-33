import os

from app import current_app as app
from app.models import db

_basedir = os.path.abspath(os.path.dirname(__file__))


class Setup(object):

    @staticmethod
    def create_app():
        app.config.from_object('config.TestingConfig')
        app.secret_key = 'super secret key'
        with app.test_request_context():
            db.create_all()
        return app.test_client()

    @staticmethod
    def truncate_db():
        with app.test_request_context():
            meta = db.metadata
            db.session.execute('SET FOREIGN_KEY_CHECKS = 0;')
            for table in reversed(meta.sorted_tables):
                db.session.execute(table.delete())
            db.session.execute('SET FOREIGN_KEY_CHECKS = 1;')
            db.session.commit()
