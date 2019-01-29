"""Utilities to read, write and manage the credentials file"""
from pathlib import Path
from getpass import getpass
import json
import stat
import shutil
from jovian.utils.logger import log
from jovian.utils.constants import WEBAPP_URL

CREDS = {}

CONFIG_DIR = Path.home()/'.jovian'
CREDS_FNAME = 'credentials.json'
CREDS_PATH = CONFIG_DIR/CREDS_FNAME


def config_exists():
    """Check if config directory exists"""
    return CONFIG_DIR.exists()


def init_config():
    """Create the config directory"""
    CONFIG_DIR.mkdir(exist_ok=True)


def purge_config():
    """Remove the config directory"""
    return shutil.rmtree(str(CONFIG_DIR), ignore_errors=True)


def creds_exist():
    """Check if credentials file exits"""
    return CREDS_PATH.exists()


def read_creds():
    """Read the credentials file"""
    with open(str(CREDS_PATH), 'r') as f:
        return json.load(f)


def write_creds(creds):
    """Write the given credentials to file"""
    init_config()
    with open(str(CREDS_PATH), 'w') as f:
        json.dump(creds, f)
    CREDS_PATH.chmod(stat.S_IREAD | stat.S_IWRITE)


def write_key(key, write_to_file=True):
    """Write the API key to memory, and the credentials file"""
    global CREDS
    CREDS['API_KEY'] = key
    if write_to_file:
        write_creds(CREDS)


def request_key():
    """Ask the user to provide the API key"""
    log("Please enter your API key (from " + WEBAPP_URL + " ):")
    api_key = getpass()
    return api_key


def read_or_request_key():
    """Read credentials file, and ask the user for API Key, if required"""
    if creds_exist():
        return read_creds()['API_KEY'], 'read'
    else:
        return request_key(), 'request'
