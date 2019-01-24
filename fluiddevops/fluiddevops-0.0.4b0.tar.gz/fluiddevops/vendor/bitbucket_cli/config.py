from __future__ import print_function
import os
import stat
import configparser


def get_default(config, section, key, default=""):
    try:
        return config.get(section, key)
    except configparser.NoSectionError:
        return default
    except configparser.NoOptionError:
        return default


CONFIG_FILE = os.path.expanduser("~/.bitbucket")
config = configparser.ConfigParser()
config.read([CONFIG_FILE])

USERNAME = get_default(config, "auth", "username")
PASSWORD = get_default(config, "auth", "password", None)
SCM = get_default(config, "options", "scm", "hg")
PROTOCOL = get_default(config, "options", "protocol", "https")


def init_config(username, password, scm="hg", protocol="https"):
    global config, CONFIG_FILE
    config["auth"] = {}
    config["options"] = {}

    config["auth"]["username"] = username
    config["auth"]["password"] = password
    config["options"]["scm"] = scm
    config["options"]["protocol"] = protocol
    with open(CONFIG_FILE, "x") as fp:
        config.write(fp)
    os.chmod(CONFIG_FILE, stat.S_IRUSR)
    return CONFIG_FILE


if PASSWORD and (os.stat(CONFIG_FILE).st_mode & stat.S_IROTH):
    print(
        "****************************************************\n"
        "  Warning: config file is readable by other users.\n"
        "  If you are storing your password in this file,\n"
        "  it may not be secure\n"
        "****************************************************"
    )
