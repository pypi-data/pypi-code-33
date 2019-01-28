import logging

from drongo_modules.core.module import Module

from . import models

__all__ = ['Media']


class Media(Module):
    """Drongo module that manages media"""

    FILESYSTEM = 'filesystem'

    __default_config__ = {
        'base_url': '/api/media',
        'storage': FILESYSTEM,
        'database': 'main',
        'enable_tinypng': False,
        'tinypng_key': None
    }

    logger = logging.getLogger('drongo_modules.core.media')

    def init(self, config):
        self.logger.info('Initializing [media] module.')
        self.app.context.modules.media = self

        #  Load and configure the media storage
        storage = config.storage
        self.storage = None

        if storage == self.FILESYSTEM:
            from .storage._filesystem import services
            self.services = services

        else:
            raise NotImplementedError

        models.init(self.app.context.modules.database[config.database])
        self.services.MediaServiceBase.init(config)
        self.init_api()

    def init_api(self):
        from .api import MediaAPI
        self.api = MediaAPI(
            app=self.app,
            module=self,
            base_url=self.config.base_url
        )

    def save_media(self, container, uploaded_file, protected=False):
        return self.services.SaveMediaService(
            container=container,
            uploaded_file=uploaded_file,
            protected=protected
        ).call()

    def delete_media(self, container, key):
        return self.services.MediaDeleteService(
            container=container,
            key=key
        ).call()

    def issue_token(self, container, key):
        return self.services.MediaIssueTokenService(
            container=container,
            key=key
        ).call()
