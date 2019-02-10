from miyadaiku.core.contents import bin_loader
from miyadaiku.core import config

from . __version__ import __version__

CSS_MIN = 'bootstrap.min.css'
CSS = 'bootstrap.css'

JS_MIN = 'bootstrap.min.js'
JS = 'bootstrap.js'

DEST_PATH = '/static/bootstrap4/'

def load_package(site):
    f = site.config.getbool('/', 'bootstrap4_compressed')

    css = CSS_MIN if f else CSS
    css_path = 'externals/css/'+css

    content = bin_loader.from_package(site, __name__, css_path, DEST_PATH+css)
    site.contents.add(content)
    site.config.add('/', {'bootstrap4_css_path': DEST_PATH+css})


    js = JS_MIN if f else JS
    js_path = 'externals/js/'+js
    
    content = bin_loader.from_package(site, __name__, js_path, DEST_PATH+js)
    site.contents.add(content)
    site.config.add('/', {'bootstrap4_js_path': DEST_PATH+js})

    site.add_template_module('bootstrap4', 'miyadaiku.themes.bootstrap4!macros.html')
