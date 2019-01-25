import pickle

from tweakers.utils import session

from . import config


def ensure_user_data_dir_exists(func):
    def wrapper():
        config.stored_cookies_path.parent.mkdir(exist_ok=True)
        func()

    return wrapper


@ensure_user_data_dir_exists
def store_persistent_cookies():
    with open(config.stored_cookies_path, "wb") as f:
        pickle.dump(session.cookies, f)


def load_persistent_cookies():
    with open(config.stored_cookies_path, "rb") as f:
        cookies = pickle.load(f)
        session.cookies.update(cookies)


def cookies_exist():
    return config.stored_cookies_path.exists()
