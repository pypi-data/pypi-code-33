"""
You can configure Lola with a `.lola.toml` configuration file.

Lola always looks for `.lola.toml` in the current working dir.

Code has precedence over configuration options.

Here is an example of a `.lola.toml` configuration file that shows all possible
configuration options::

    [lola]
    # the remote location for uploading all artifacts to
    remote_location = "gs://somewhere
    # the location of the credentials to use for the remote location
    remote_credentials = "path/to/service_account.json"

"""
from pathlib import Path
from typing import Any, Dict

import log
import tomlkit


def load_lola_config(
    user_params: Dict[str, Any], ignore_config=False
) -> Dict[str, Any]:
    default_config = {"remote_location": "", "remote_credentials": ""}

    user_config: Dict = {}
    user_config_file = Path.cwd() / ".lola.toml"
    if user_config_file.is_file() and not ignore_config:
        log.info(f"Loading {user_config_file}...")
        with user_config_file.open() as f:
            user_config = tomlkit.parse(f.read())["lola"]

    config = {**default_config, **user_config, **user_params}
    return config
