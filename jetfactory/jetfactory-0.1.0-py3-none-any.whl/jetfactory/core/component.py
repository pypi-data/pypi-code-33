# -*- coding: utf-8 -*-


class BaseComponent:
    pkg = None
    log = None
    path = None

    @classmethod
    def _pkg_bind(cls, pkg):
        cls.pkg = pkg
        cls.path = pkg.path
        cls.log = pkg.log
