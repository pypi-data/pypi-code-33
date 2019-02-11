import contextlib
import json
from distutils.dist import Distribution

import babel.support
import mock
import pytest
import six

from morphi.messages import (
    frontend,
    manager,
    Manager
)


class TestMessagesFrontendCompileJson(object):
    @pytest.fixture(scope='function')
    def distribution(self):
        return Distribution(dict(
            name='TestProject'
        ))

    @pytest.fixture(scope='function')
    def cmd(self, distribution):
        cmd = frontend.CompileJson(distribution)
        cmd.initialize_options()

        cmd.locale = 'en'
        cmd.input_file = 'dummy'
        cmd.output_file = 'dummy'

        return cmd

    def test_output_dir_set_explicitly(self, cmd):
        cmd.output_dir = 'foo'
        cmd.finalize_options()

        assert 'foo' == cmd.output_dir

    def test_output_dir_from_directory(self, cmd):
        cmd.directory = 'foo'
        cmd.finalize_options()

        assert 'foo' == cmd.output_dir


class TestMessagesFrontendCompileJsonWriteJson(object):
    class MockMessage:
        def __init__(self, id, string, fuzzy=False):
            self.id = id
            self.string = string
            self.fuzzy = fuzzy

        def __lt__(self, other):
            return self.id < other.id

    class MockCatalog:
        def __init__(self, locale, plural_forms, mock_data):
            self.locale = locale
            self.plural_forms = plural_forms
            self.mock_data = mock_data

        def __len__(self):
            return len(self.mock_data)

        def __getitem__(self, item):
            return self.mock_data[item]

    @pytest.fixture
    def catalog(self):
        return self.MockCatalog(locale='es', plural_forms='1-many', mock_data=[
            self.MockMessage(id='foo', string='FOO'),
            self.MockMessage(id='bar', string='BAR', fuzzy=True),
        ])

    @pytest.fixture(scope='function')
    def distribution(self):
        return Distribution(dict(
            name='TestProject'
        ))

    @pytest.fixture(scope='function')
    def cmd(self, distribution):
        cmd = frontend.CompileJson(distribution)
        cmd.initialize_options()

        cmd.locale = 'en'
        cmd.input_file = 'dummy'
        cmd.output_file = 'dummy'

        return cmd

    def test_write_fuzzy(self, catalog, cmd):
        with contextlib.closing(six.StringIO()) as f:
            cmd._write_json(f, catalog, use_fuzzy=True)
            data = json.loads(f.getvalue())

        assert {
            '': {
                'language': 'es',
                'plural-forms': '1-many'
            },
            'foo': 'FOO',
            'bar': 'BAR',
        } == data

    def test_elide_fuzzy(self, catalog, cmd):
        with contextlib.closing(six.StringIO()) as f:
            cmd._write_json(f, catalog, use_fuzzy=False)
            data = json.loads(f.getvalue())

        assert {
            '': {
                'language': 'es',
                'plural-forms': '1-many'
            },
            'foo': 'FOO'
        } == data


class TestMessagesManagerManager(object):
    class NullManager(Manager):
        def _translations_loader(self, *args, **kwargs):
            return babel.support.NullTranslations()

    @pytest.fixture(scope='function')
    def manager(self):
        return self.NullManager()

    @pytest.fixture(scope='function')
    def _(self, manager):
        return manager.gettext

    @pytest.fixture(scope='function')
    def _n(self, manager):
        return manager.ngettext

    def test_gettext(self, _):
        assert 'a' == _('a')
        assert 'hello world' == _('hello {name}', name='world')

    def test_lazy_gettext(self, manager):
        _ = manager.lazy_gettext
        assert 'a' == str(_('a'))

    @pytest.mark.parametrize('num, expected', (
            (0, '0 are hello'),
            (1, '1 is hello'),
            (2, '2 are hello'),
    ))
    def test_lazy_ngettext(self, manager, num, expected):
        _n = manager.lazy_ngettext
        assert expected == str(_n('{num} is {word}',
                                  '{num} are {word}',
                                  num, word='hello'))

    @pytest.mark.parametrize('num, expected', (
            (0, '0 are hello'),
            (1, '1 is hello'),
            (2, '2 are hello'),
    ))
    def test_ngettext(self, _n, num, expected):
        assert expected == _n('{num} is {word}',
                              '{num} are {word}',
                              num, word='hello')


class TestMessagesManagerFindMoFilename(object):
    @pytest.fixture(scope='function')
    def gettext_find(self):
        with mock.patch(
            'morphi.messages.manager.gettext_find',
            autospec=True, spec_set=True, side_effect=lambda *args, **kwargs: None
        ) as gettext_find:
            yield gettext_find

    @pytest.fixture(scope='function')
    def path_exists_enclosure(self):
        with mock.patch(
                'morphi.libs.packages.enclose_package_path_exists',
                autospec=True, spec_set=True,
                return_value=mock.Mock(side_effect=lambda path: False)
        ) as enclosure:
            yield enclosure

    @pytest.fixture(scope='function')
    def path_exists(self, path_exists_enclosure):
        yield path_exists_enclosure.return_value

    @pytest.fixture(scope='function')
    def expected(self, path_exists):
        DEFAULT_DOMAIN = babel.support.Translations.DEFAULT_DOMAIN

        yield [
            mock.call(DEFAULT_DOMAIN, 'localedir', ['es'], False,
                      path_exists=None, extension='ext'),
            mock.call(DEFAULT_DOMAIN, 'locale', ['es'], False, path_exists=None, extension='ext'),
            mock.call(DEFAULT_DOMAIN, 'i18n', ['es'], False, path_exists=None, extension='ext'),
            mock.call(DEFAULT_DOMAIN, 'localedir', ['es'], False,
                      path_exists=path_exists, extension='ext'),
            mock.call(DEFAULT_DOMAIN, 'locale', ['es'], False,
                      path_exists=path_exists, extension='ext'),
            mock.call(DEFAULT_DOMAIN, 'i18n', ['es'], False,
                      path_exists=path_exists, extension='ext'),

            mock.call('domain', 'localedir', ['es'], False, path_exists=None, extension='ext'),
            mock.call('domain', 'locale', ['es'], False, path_exists=None, extension='ext'),
            mock.call('domain', 'i18n', ['es'], False, path_exists=None, extension='ext'),
            mock.call('domain', 'localedir', ['es'], False,
                      path_exists=path_exists, extension='ext'),
            mock.call('domain', 'locale', ['es'], False, path_exists=path_exists, extension='ext'),
            mock.call('domain', 'i18n', ['es'], False, path_exists=path_exists, extension='ext'),

            mock.call('package_name', 'localedir', ['es'], False,
                      path_exists=None, extension='ext'),
            mock.call('package_name', 'locale', ['es'], False, path_exists=None, extension='ext'),
            mock.call('package_name', 'i18n', ['es'], False, path_exists=None, extension='ext'),
            mock.call('package_name', 'localedir', ['es'], False,
                      path_exists=path_exists, extension='ext'),
            mock.call('package_name', 'locale', ['es'], False,
                      path_exists=path_exists, extension='ext'),
            mock.call('package_name', 'i18n', ['es'], False,
                      path_exists=path_exists, extension='ext'),
        ]

    def test_find_mo_filename(self, gettext_find, expected):
        manager.find_mo_filename(domain='domain', localedir='localedir', languages=['es'],
                                 package_name='package_name', extension='ext')

        # attempted_domain, attempted_dirname, languages, all, path_exists=path_exists
        assert expected == gettext_find.call_args_list

    def test_single_languages_are_listified(self, gettext_find, expected):
        manager.find_mo_filename(domain='domain', localedir='localedir', languages='es',
                                 package_name='package_name', extension='ext')

        # attempted_domain, attempted_dirname, languages, all, path_exists=path_exists
        assert expected == gettext_find.call_args_list

    def test_invalid_package_resource_path_throws_no_error(self, path_exists_enclosure):
        path_exists_enclosure.return_value.side_effect = ValueError

        manager.find_mo_filename(domain='domain', localedir='localedir', languages=['es'],
                                 package_name='package_name', extension='ext')

    def test_file_found(self, path_exists, gettext_find):
        def find_package_i18n_es_path_exists(domain, dirname, languages, all,
                                             path_exists, extension):
            return (
                'foo/bar/baz'
                if (
                    domain == 'package_name' and
                    dirname == 'i18n' and
                    path_exists is not None
                )
                else None
            )

        gettext_find.side_effect = find_package_i18n_es_path_exists

        filename = manager.find_mo_filename(domain='domain', localedir='localedir', languages='es',
                                            package_name='package_name', extension='ext')
        assert 'foo/bar/baz' == filename


class TestMessagesManagerGetMoData(object):
    @pytest.fixture
    def find_mo_filename(self):
        with mock.patch('morphi.messages.manager.find_mo_filename',
                        autospec=True, spec_set=True) as find_mo_filename:
            find_mo_filename.return_value = 'foo/bar/baz'
            yield find_mo_filename

    @pytest.fixture
    def open(self):
        with mock.patch('morphi.messages.manager.open',
                        mock.mock_open(read_data='mock open')) as open:
            yield open

    @pytest.fixture
    def package_open(self):
        with mock.patch('morphi.libs.packages.package_open',
                        mock.mock_open(read_data='mock package open')) as open:
            yield open

    def test_no_file_found(self, find_mo_filename):
        find_mo_filename.return_value = None
        assert manager.get_mo_data() is None

    def test_filesystem_opener(self, find_mo_filename, open, package_open):
        data = manager.get_mo_data()
        open.assert_called_with('foo/bar/baz', 'rb')
        assert not package_open.called
        assert 'mock open' == data

    def test_package_opener(self, find_mo_filename, open, package_open):
        data = manager.get_mo_data(package_name='foobar')
        assert not open.called
        package_open.assert_called_with('foobar', 'foo/bar/baz')
        assert 'mock package open' == data

    def test_filesystem_fallback_for_package_opener(self, find_mo_filename, open, package_open):
        package_open.side_effect = NotImplementedError

        data = manager.get_mo_data(package_name='foobar')
        package_open.assert_called_with('foobar', 'foo/bar/baz')
        open.assert_called_with('foo/bar/baz', 'rb')
        assert 'mock open' == data


class TestMessagesManagerGettextFind(object):
    pass


class TestMessagesManagerLoadTranslations(object):
    @pytest.fixture
    def get_mo_data(self):
        with mock.patch(
            'morphi.messages.manager.get_mo_data', autospec=True, spec_set=True
        ) as get_mo_data:
            yield get_mo_data

    def test_load_fails(self, get_mo_data):
        get_mo_data.return_value = None
        translation = manager.load_translations()
        assert isinstance(translation, babel.support.NullTranslations)

    @mock.patch('babel.support.Translations', autospec=True, spec_set=True)
    def test_load(self, Translations, get_mo_data):
        get_mo_data.return_value = b'asdf'
        manager.load_translations()
        assert Translations.called
