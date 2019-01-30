from flask import current_app, _app_ctx_stack
from flask_philo_core import ConfigurationError
from flask_philo_core.views import BaseResourceView
from flask_philo_sqlalchemy.connection import create_pool


class SQLAlchemyView(BaseResourceView):
    def __init__(self):
        self.app = current_app._get_current_object()
        if 'FLASK_PHILO_SQLALCHEMY' not in self.app.config:
            raise ConfigurationError(
                'Not configuration found for Flask_Philo_SQLAlchemy')
        ctx = _app_ctx_stack.top
        if ctx is not None:
            if not hasattr(ctx, 'sqlalchemy_pool'):
                ctx.sqlalchemy_pool = create_pool()
        self.sqlalchemy_pool = ctx.sqlalchemy_pool
