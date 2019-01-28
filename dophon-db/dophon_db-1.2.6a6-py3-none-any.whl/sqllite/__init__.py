from . import db_init


class SqliteManager():
    pass


singleton = SqliteManager()


def init():
    db_init.init_config()
    for k, v in db_init.cache_config.items():
        setattr(singleton, k.replace('sqlite_', ''), v)
    return singleton
