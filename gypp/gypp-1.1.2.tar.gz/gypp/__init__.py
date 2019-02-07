import os
import yaml
from . import passwords_yaml

DEFAULT_SOURCES = os.path.expanduser("~/.config/gypp/gypp.yml")

def getPasswordEntry(source_name, key, sources_file=DEFAULT_SOURCES):
    """
    Retrieve a password entry given key to source and key within source.

    Args:
        source_name: Entry in
        key: Entry in password file to retrieve
        config_file: YAML file containing a list of pointers to password files

    Returns:
        Password entry dictionary
    """
    with open(os.path.expanduser(sources_file)) as fsources:
        config_entries = yaml.safe_load(fsources)
        sources = config_entries.get("sources",{})
        password_file = sources[source_name]
        return passwords_yaml.PasswordsYAML(password_file).entry(key)
