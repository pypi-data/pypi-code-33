import logging


log = logging.getLogger(__name__)


def configure_jinja_environment(jinja_environment, manager):
    jinja_environment.add_extension('jinja2.ext.i18n')

    attr_name = 'install_gettext_translations'
    if hasattr(jinja_environment, attr_name):
        getattr(jinja_environment, attr_name)(manager.translations)

    else:
        log.warning('While configuring the jinja environment, '
                    '`install_gettext_translations` was not found!')

    jinja_environment.globals.update(find_mo_filename=manager._mo_finder)
