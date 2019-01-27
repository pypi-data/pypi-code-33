# -*- coding: utf-8 -*-

from flask import current_app
try:
    from flask import _app_ctx_stack as stack
except ImportError:  # pragma: no cover
    from flask import _request_ctx_stack as stack

import pika
import pika_pool


class PikaFlask(object):

    def __init__(self, app=None):
        self.app = app
        if app is not None:  # pragma: no cover
            self.init_app(app)

    def init_app(self, app):
        app.config.setdefault(
            'RABBITMQ_URL', 'amqp://guest:guest@localhost:5672/?socket_timeout=10&connection_attempts=2')

    @property
    def pool(self):
        ctx = stack.top
        if ctx is not None:
            params = pika.URLParameters(current_app.config['RABBITMQ_URL'])
            if not hasattr(ctx, 'pika_flask'):
                ctx.pika_flask = pika_pool.QueuedPool(
                    create=lambda: pika.BlockingConnection(parameters=params),
                    max_size=10,
                    max_overflow=10,
                    timeout=10,
                    recycle=3600,
                    stale=45,
                )
                with ctx.pika_flask.acquire() as cxn:
                    cxn.channel.exchange_declare(exchange='geokrety',
                                                 exchange_type='topic',
                                                 durable=True)
        return ctx.pika_flask


pika_ = PikaFlask()
