import mock

from morphi.helpers import jinja


class TestJinjaHelper(object):
    def test_configure_jinja_environment_can_install(self):
        jinja_environment = mock.Mock()
        manager = mock.Mock()

        jinja.configure_jinja_environment(jinja_environment, manager)

        jinja_environment.add_extension.assert_called_with('jinja2.ext.i18n')
        jinja_environment.install_gettext_translations.assert_called_with(manager.translations)
        jinja_environment.globals.update.assert_called_with(find_mo_filename=manager._mo_finder)

    def test_configure_jinja_environment_cannot_install(self, caplog):
        jinja_environment = mock.Mock()
        delattr(jinja_environment, 'install_gettext_translations')
        manager = mock.Mock()

        jinja.configure_jinja_environment(jinja_environment, manager)

        jinja_environment.add_extension.assert_called_with('jinja2.ext.i18n')
        jinja_environment.globals.update.assert_called_with(find_mo_filename=manager._mo_finder)

        assert 1 == len(caplog.records)
        assert 'install_gettext_translations' in caplog.records[0].message
