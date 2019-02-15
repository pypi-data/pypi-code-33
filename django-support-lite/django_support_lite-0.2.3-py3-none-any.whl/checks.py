import os

from django.conf import settings
from django.core import checks


@checks.register()
def check_settings(app_configs=None, **kwargs):
    errors = [
        checks.Error(
            'Setting {} shoud be set.'.format(setting)
        )
        for setting in [
            'DSL_LAYOUT_NAME',
            'DSL_UPLOAD_DIRECTORY',
            'DSL_UPLOAD_URL_PREFIX',
            'DSL_TICKETS_PER_PAGE',
            'DSL_EMAIL_ENABLE',
        ]
        if not hasattr(settings, setting)
    ]

    if hasattr(settings, 'DSL_EMAIL_ENABLE') and settings.DSL_EMAIL_ENABLE:
        if not hasattr(settings, 'DSL_EMAIL_SENDER'):
            errors.append(
                checks.Error(
                    'Setting {} shoud be set.'.format('DSL_EMAIL_SENDER')
                )
            )

        if not hasattr(settings, 'DSL_EMAIL_MANAGER'):
            errors.append(
                checks.Error(
                    'Setting {} shoud be set.'.format('DSL_EMAIL_MANAGER')
                )
            )

    return errors

@checks.register()
def check_upload_directory(app_configs=None, **kwargs):
    if os.path.exists(settings.DSL_UPLOAD_DIRECTORY):
        return []

    return [
        checks.Error('Upload directory not exist.'),
    ]
