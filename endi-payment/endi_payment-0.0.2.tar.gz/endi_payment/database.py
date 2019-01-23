# -*- coding: utf-8 -*-
"""
Specific session stuff used to store the payment history logs
"""
from sqlalchemy import engine_from_config
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

HistorySessionFactory = sessionmaker()
ModelBase = declarative_base()


class CriticalIntegrityError(Exception):
    """
    Error raised when we can't ensure the integrity of the current managed datas
    anymore
    """
    pass


class LocalSessionContext(object):
    def __enter__(self):
        """
        Initialize a specific session
        """
        self.session = HistorySessionFactory()
        return self.session

    def __exit__(self, type, value, traceback):
        try:
            self.session.commit()
        except:
            self.session.rollback()
            raise CriticalIntegrityError(
                u"Erreur critique rencontrée lors de la journalisation "
                u"des évènements d'encaissement"
            )


def configure_specific_payment_engine(config):
    """
    Configure un bindind spécifique (avec un utilisateur différent) pour la
    manipulation des instances de Payment

    Garder pour le principe mais ne sera peut être jamais utilisé.
    """
    settings = config.get_settings()
    if 'endi_payment_db.url' in settings:
        from sqlalchemy.orm import Session
        prefix = 'endi_payment_db.'

        engine = engine_from_config(settings, prefix=prefix)
        main_engine = engine_from_config(settings)

        class CustomSession(Session):
            def __init__(self, *args, **kwargs):
                Session.__init__(self, *args, **kwargs)

            def get_bind(self, mapper=None, clause=None):
                from autonomie.models.task.invoice import Payment
                if mapper is not None and issubclass(mapper.class_, Payment):
                    return engine
                else:
                    return main_engine

        from autonomie_base.models.base import DBSESSION
        DBSESSION.configure(class_=CustomSession)


def includeme(config):
    """
    Pyramid Include's mechanism
    Setup the library specific session
    """
    settings = config.get_settings()

    if 'endi_payment_db.url' in settings:
        # On a une connexion particulière pour l'édition des journaux
        prefix = 'endi_payment_db.'
        endi_payment_engine = engine_from_config(settings, prefix=prefix)

    else:
        # On utilise l'engine sqlalchemy par défaut (celui d'endi)
        endi_payment_engine = endi_payment_engine(settings)

    from endi_payment.models import EndiPaymentHistory  # NOQA

    HistorySessionFactory.configure(bind=endi_payment_engine)
    ModelBase.metadata.bind = endi_payment_engine
    ModelBase.metadata.create_all(endi_payment_engine)

    from transaction import commit, begin
    commit()
    begin()
    return True
