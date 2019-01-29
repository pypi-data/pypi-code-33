# -*- coding: utf-8 -*-

from jetfactory import Jetpack
from .controller import Controller
from .services import svc_pkgs

pkg = Jetpack(
    meta={
        'name': 'core',
        'summary': 'Core components',
        'description': 'Allows reading from and operating on the Jetfactory core'
    },
    controller=Controller,
    services=[svc_pkgs],
    models=[]
)
