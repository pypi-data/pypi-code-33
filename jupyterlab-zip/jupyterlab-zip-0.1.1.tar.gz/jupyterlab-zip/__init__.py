from notebook.utils import url_path_join
from .handler import ZipHandler


# Jupyter Extension points
def _jupyter_server_extension_paths():
    return [{'module': 'jupyterlab-zip'}]

def load_jupyter_server_extension(nbapp):
    nbapp.log.info("my module enabled!")
    web_app = nbapp.web_app
    host_pattern = '.*$'
    base_url = url_path_join(web_app.settings['base_url'], 'zip-lab')
    handlers = [
        (base_url, ZipHandler)
    ]
    web_app.add_handlers('.*', handlers)
