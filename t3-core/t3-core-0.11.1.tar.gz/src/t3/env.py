from os import environ
from os.path import join
from functools import lru_cache

from dotenv import load_dotenv


@lru_cache()
def load_env(dot_env_path, filename='.env'):
    load_dotenv(dotenv_path=join(dot_env_path, filename))
    return environ
