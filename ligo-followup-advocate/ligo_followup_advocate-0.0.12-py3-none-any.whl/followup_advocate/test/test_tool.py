import json
import io
import os

import pkg_resources
import pytest

from ..tool import main


class MockGraceDb(object):

    def __init__(self, service):
        assert service == 'https://gracedb.invalid/api/'
        self.service_url = service

    def _open(self, graceid, filename):

        filename = os.path.join('data', graceid, filename)
        if filename.endswith('.fits.gz'):
            from astropy.utils.data import download_file
            url = ('https://dcc.ligo.org/public/0145/T1700453/001/'
                   'LALInference_v1.fits.gz')
            f = io.open(download_file(url, cache=False), 'rb')
            return f
        else:
            f = io.open(pkg_resources.resource_filename(__name__, filename))

            def get_json():
                return json.load(f)

            f.json = get_json
            return f

    def superevent(self, graceid):
        return self._open(graceid, 'superevent.json')

    def event(self, graceid):
        return self._open(graceid, 'event.json')

    def logs(self, graceid):
        return self._open(graceid, 'logs.json')

    def voevents(self, graceid):
        return self._open(graceid, 'voevents.json')

    def files(self, graceid, filename=None, raw=True):
        if filename is None:
            return self._open(graceid, 'files.json')
        else:
            return self._open(graceid, os.path.join('files', filename))


@pytest.fixture
def mock_gracedb(monkeypatch):
    return monkeypatch.setattr('ligo.gracedb.rest.GraceDb', MockGraceDb)


@pytest.fixture
def mock_webbrowser_open(mocker):
    return mocker.patch('webbrowser.open')


def test_compose(mock_gracedb):
    main(['--service', 'https://gracedb.invalid/api/', 'compose', 'S1234'])


def test_compose_mailto(mock_gracedb, mock_webbrowser_open):
    main(['--service', 'https://gracedb.invalid/api/', 'compose',
          '--mailto', 'S1234'])
    assert mock_webbrowser_open.called_once()
