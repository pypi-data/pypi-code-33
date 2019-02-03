import pathlib
import json
from json import JSONDecodeError


pytradecli_dir = pathlib.Path.home() / ".pytradecli"
config_file = pytradecli_dir / "config.json"

if not pytradecli_dir.exists():
    pytradecli_dir.mkdir()


def load_config_json():
    if config_file.exists():
        with config_file.open("r") as f:
            try:
                return json.load(f)
            except JSONDecodeError:
                return None


def save_token(token):
    save_config("token", token)


def load_token():
    return load_config("token")


def save_api_host(api_host):
    save_config("api_host", api_host)


def load_api_host():
    return load_config("api_host")


def save_config(key, value):
    config_data = load_config_json()
    if not config_data:
        config_data = {}
    config_data[key] = value
    with config_file.open("w") as f:
        json.dump(config_data, f)


def load_config(key):
    config_data = load_config_json()
    if config_data:
        return config_data.get(key)
    else:
        return None
