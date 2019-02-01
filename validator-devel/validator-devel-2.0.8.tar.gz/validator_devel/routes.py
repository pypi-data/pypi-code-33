import pkg_resources


from .views import (
    index, module, module_websocket_handler, module_html, module_prepare_download,
    folder_prepare_download, home, download, edit_module
)
from .templating import get_validator_path


def get_static_path():
    return pkg_resources.resource_filename("validator_devel", "static")


def setup_routes(app):

    # Validator handler.
    app.router.add_static('/module/validator/', path=get_validator_path(), name='validator')

    app.router.add_get('/ws', module_websocket_handler)
    app.router.add_get('/module/{module_key}/download', module_prepare_download)
    app.router.add_get('/module/{module_key}/edit', edit_module)
    app.router.add_get('/module/{module_key}', module_html)
    app.router.add_get('/module', module)

    app.router.add_get('/folder/{folder}/download', folder_prepare_download)
    app.router.add_get('/download/{uuid}', download)

    # Frontend handler.
    app.router.add_static('/', path=get_static_path(), name='static')
