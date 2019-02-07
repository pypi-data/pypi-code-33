options = (
    ('celerytask-log-dir', {
        'type': 'string',
        'default': None,
        'help': ('celery task log directory; if unset, defaults to '
                 '<config.appdatahome>/logs'),
        'group': 'celerytask',
        'level': 2,
    }),
)
