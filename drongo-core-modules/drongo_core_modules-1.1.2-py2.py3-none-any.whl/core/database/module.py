import logging

from drongo_modules.core.module import Module


class Database(Module):
    # Database types
    MONGO = 'mongo'
    MYSQL = 'mysql'
    POSTGRES = 'postgres'
    REDIS = 'redis'

    logger = logging.getLogger('drongo_modules.core.database')

    def init(self, config):
        self.logger.info('Initializing [database] module.')

        setattr(
            self.app.context.modules.database,
            config.get('_id'),
            self
        )

        self._type = config.get('type')
        if self._type == self.MONGO:
            from .databases._mongo import MongoDatabase
            klass = MongoDatabase

        elif self._type == self.REDIS:
            from .databases._redis import RedisDatabase
            klass = RedisDatabase

        elif self._type == self.MYSQL:
            from .databases._mysql import MysqlDatabase
            klass = MysqlDatabase

        elif self._type == self.POSTGRES:
            from .databases._postgres import PostgresDatabase
            klass = PostgresDatabase

        else:
            self.logger.error('Unknown database type!')
            raise NotImplementedError

        self._inst = klass(self.app, config)

        self.logger.info(
            'Initialized database [{name}] of type [{type}]'.format(
                name=config._id,
                type=config.type
            )
        )

    @property
    def type(self):
        return self._type

    @property
    def instance(self):
        return self._inst
