import mock

import pytest

from morphi.libs import packages


class TestPackagesEnclosePackagePathExists(object):
    @mock.patch('pkg_resources.get_provider', autospec=True, spec_set=True)
    def test_enclose_package_path_exists(self, get_provider):
        enclosure = packages.enclose_package_path_exists('foobar')
        get_provider.assert_called_with('foobar')
        assert get_provider.return_value.has_resource == enclosure

    def test_enclose_package_path_exists_functional(self):
        """verify the enclosure performs as expected"""
        path_exists = packages.enclose_package_path_exists('logging')
        assert path_exists('__init__.py') is True
        assert path_exists('nosuchfile.py') is False


@mock.patch('pkg_resources.get_provider', autospec=True, spec_set=True)
class TestPackagesPackageOpen:
    def test_open_fails(self, get_provider):
        provider = get_provider.return_value
        provider.has_resource.return_value = False

        with pytest.raises(IOError):
            with packages.package_open('foobar', '/foo'):
                pass

    def test_open(self, get_provider):
        provider = get_provider.return_value
        provider.has_resource.return_value = True
        provider.get_resource_string.return_value = b'asdf'

        with packages.package_open('foobar', '/foo') as f:
            data = f.read()

        assert b'asdf' == data
