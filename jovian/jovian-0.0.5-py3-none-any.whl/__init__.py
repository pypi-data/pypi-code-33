from time import sleep
from jovian.utils.anaconda import upload_conda_env
from jovian.utils.pip import upload_pip_env
from jovian.utils.api import create_gist
from jovian.utils.logger import log
from jovian.utils.constants import WEBAPP_URL


def commit(message, slug=None):
    """Save the notebook, capture the environment, and upload both to the cloud for sharing"""
    res = create_gist()
    slug, owner = res['slug'], res['owner']

    # Save & upload environment
    try:
        upload_conda_env(slug)
    except:
        try:
            upload_pip_env(slug)
        except:
            log('Failed to capture the Python environment', error=True)

    log('Committed successfully! ' + WEBAPP_URL +
        "/" + owner['username'] + "/" + slug)
