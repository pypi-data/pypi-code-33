# -*- coding: utf-8 -*-

from jetfactory import Jetpack
from .app import controller, models, services

pkg = Jetpack(
    controller=controller,
    services=services,
    models=models,
    meta={
        'version': (1, 0, 0),
        'name': 'guestbook',
        'description': 'Example Guestbook Package',
    }
)
