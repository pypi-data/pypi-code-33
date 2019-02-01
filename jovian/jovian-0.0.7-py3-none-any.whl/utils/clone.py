import os
from requests import get
from jovian.utils.api import get_gist


def clone(slug):
    """Download the files for a gist"""
    gist = get_gist(slug)
    os.makedirs(slug, exist_ok=True)
    for f in gist['files']:
        with open(slug + '/' + f['filename'], 'wb') as fp:
            fp.write(get(f['rawUrl']).content)
