import os
import json
from functools import wraps
from sqlalchemy import create_engine
from .logging import error, info


def add_env_variables(func):
    @wraps(func)
    def add_env(*args, **kwargs):
        env = {}
        prefix = "IOEXPLORER_DATABASE"
        for var in ["NAME", "HOST", "PORT", "USERNAME", "PASSWORD"]:
            env_var = "_".join([prefix, var])
            try:
                env[var.lower()] = os.environ[env_var]
            except KeyError:
                error(
                    "The `{}` environment variable was not set. Exiting.".format(
                        env_var
                    )
                )
        return func(*args, _env=env, **kwargs)

    return add_env


def connect_to_db(func):
    @wraps(func)
    def connect_then_run(_env, **kwargs):
        engine = create_engine(
            "postgres://{username}:{password}@{host}:{port}/{name}".format(**_env),
            paramstyle="format",
        )
        conn = engine.connect()
        return func(conn=conn, engine=engine, _env=_env, **kwargs)

    return connect_then_run
