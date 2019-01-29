__version__ = "0.0.4"

from minty import Base
from minty.cqrs import MiddlewareBase

import sqlalchemy


def DatabaseTransactionMiddleware(infrastructure_name):
    class _DatabaseTransactionMiddleware(MiddlewareBase):
        def __call__(self, func, event):
            session = self.infrastructure_factory.get_infrastructure(
                context=event.context, infrastructure_name=infrastructure_name
            )
            try:
                func()
                session.commit()
            except Exception as e:
                session.rollback()
                raise e

    return _DatabaseTransactionMiddleware


class DatabaseSessionInfrastructure(Base):
    """Infrastructure for handling SQLAlchemy sessions"""

    def __init__(self, prefix: str):
        """Initialize a new database session infrastructure factory

        :param prefix: Prefix to use for sqlalchemy.engine_from_config, which
            uses it to retrieve a specific configuration from a configuration.
        :type prefix: str
        """

        self.prefix = prefix

    def __call__(self, config: dict):
        """Create a database session from the specified configuration

        Uses `sqlalchemy.engine_from_config` and the prefix configured in
        `__init__` to create a `sqlalchemy.Session`.

        :param config: Configuration
        :type config: dict
        :return: A SQLAlchemy session, bound to an engine that's been set up
            according to `config`
        :rtype: sqlalchemy.Session
        """

        engine = sqlalchemy.engine_from_config(
            configuration=config,
            prefix=self.prefix,
            poolclass=sqlalchemy.pool.NullPool,
        )
        session = sqlalchemy.orm.Session(bind=engine)
        return session

    def clean_up(self, session):
        """Close the SQLAlchemy Session"""

        session.close()
