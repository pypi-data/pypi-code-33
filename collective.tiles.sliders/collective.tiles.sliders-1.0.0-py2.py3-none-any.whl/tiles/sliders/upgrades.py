# -*- coding: utf-8 -*-
from collective.tiles.sliders import config
from plone.app.upgrade.utils import loadMigrationProfile


def reload_gs_profile(context):
    if config.HAS_MOSAIC:
        loadMigrationProfile(context, config.BASE_PROFILE)
    else:
        loadMigrationProfile(context, config.INSTALL_PROFILE)
