from miyadaiku.core.contents import bin_loader
from miyadaiku.core import config

from . __version__ import __version__

TETHER_MIN = 'tether.min.js'
TETHER = 'tether.js'
DEST_PATH = '/static/tether/'

def load_package(site):
    f = site.config.getbool('/', 'tether_compressed')
    tether = TETHER_MIN if f else TETHER
    src_path = 'externals/js/'+tether
    
    content = bin_loader.from_package(site, __name__, src_path, DEST_PATH+tether)
    site.contents.add(content)
    site.config.add('/', {'tether_path': DEST_PATH+tether})

    site.add_template_module('tether', 'miyadaiku.themes.tether!macros.html')
