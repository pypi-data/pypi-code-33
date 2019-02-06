import os
import pytest
import urllib
from tempfile import TemporaryDirectory
from clav.hash import checkhash
from clav.net import wget, download, polltcp
from clav.time import Timer

test_file_url = 'https://s2.q4cdn.com/965716280/files/doc_presentations/Q3-2014-earnings-call-slides.pdf'
test_file_name = os.path.basename(test_file_url)
test_file_hash = 'c46ea29cce0580bb6410fc87238e866da43071f176b72bdc9cd7e6dc8f0cd3d9bf59100f20596cf9d902a529f43ea4164719f38f37cd7f9f30524c0282f70cbd'
test_file_alg = 'sha512'
rando_file_url = 'https://s2.q4cdn.com/965716280/files/doc_downloads/updated/q3-2015-earnings-release.pdf'
url_404 = 'https://www.ritchiebros.com/where-is-thumbkin'
url_malformed = 'htp;/go.team.venture.w.f.F.c.C.a'
url_bad_dns = 'http://your.mother.was.a.snowblower'
blackhole_host = '1.1.1.1'
blackhole_port = 23
always_up_host = 'google.com'
always_up_port = 443

pytestmark = pytest.mark.smoke

@pytest.fixture
def temp_dir():
  with TemporaryDirectory() as name:
    yield name

class TestWget:

  def test_valid(self, temp_dir):
    path = f'{temp_dir}/{test_file_name}'
    wget(test_file_url, path)
    assert os.path.isfile(path)
    checkhash(path, test_file_alg, test_file_hash)

  def test_invalid(self, temp_dir):
    path = f'{temp_dir}/foo'
    with pytest.raises(wget.HTTPError):
      wget(url_404, path)
    with pytest.raises(ValueError):
      wget(url_malformed, path)
    # doesn't work with nameservers that resolve non-existing hosts to a default
    #with pytest.raises([wget.HTTPError, wget.URLError]):
    #  wget(url_bad_dns, path)

  def test_overwrite(self, temp_dir):
    path = f'{temp_dir}/{test_file_name}'
    assert wget(test_file_url, path) == False
    with pytest.raises(FileExistsError):
      wget(test_file_url, path)
    assert wget(test_file_url, path, overwrite=True) == True

class TestDownload:

  def test_valid(self, temp_dir):
    path = f'{temp_dir}/{os.path.basename(test_file_url)}'
    assert download(test_file_url, path, test_file_alg, test_file_hash) == True
    assert os.path.isfile(path)
    assert download(test_file_url, path, test_file_alg, test_file_hash) == False
    os.unlink(path)
    assert download(test_file_url, path) == True
    assert os.path.isfile(path)
    assert download(test_file_url, path) == False
    checkhash(path, test_file_alg, test_file_hash)

  def test_invalid(self, temp_dir):
    path = f'{temp_dir}/{test_file_name}'
    with pytest.raises(wget.HTTPError):
      download(url_404, path)
    with pytest.raises(ValueError):
      download(url_malformed, path)
    # doesn't work with nameservers that resolve non-existing hosts to a default
    #with pytest.raises([wget.HTTPError, wget.URLError]):
    #  download(url_bad_dns, path)
    with pytest.raises(checkhash.error):
      download(test_file_url, path, test_file_alg, 'samson simpson')

  def test_existing(self, temp_dir):
    path = f'{temp_dir}/{test_file_name}'
    assert download(rando_file_url, path) == True
    assert os.path.isfile(path)
    assert download(test_file_url, path, test_file_alg, test_file_hash) == True
    assert os.path.isfile(path)
    # assert download(test_file_url, path, test_file_alg, test_file_hash) == False
    # checkhash(path, test_file_alg, test_file_hash)

@pytest.mark.full
class TestPolltcp:

  sock_timeout = 1.0

  def test_valid(self):
    # FIXME this sucks
    r = polltcp(
      always_up_host, always_up_port, sock_timeout=self.sock_timeout,
      timeout=-1, pause=0, retries=0
    )
    assert r == True

  def test_sock_timeout(self):
    with Timer() as t:
      r = polltcp(
        blackhole_host, blackhole_port, sock_timeout=self.sock_timeout,
        timeout=-1, pause=0, retries=0
      )
    assert r == False
    assert int(t.time) == self.sock_timeout

  def test_timeout(self):
    with Timer() as t:
      r = polltcp(
        blackhole_host, blackhole_port, sock_timeout=self.sock_timeout,
        timeout=self.sock_timeout * 2, pause=0, retries=-1
      )
    assert r == False
    assert int(t.time) == self.sock_timeout * 2

  def test_pause_retries(self):
    sockto = float(self.sock_timeout)
    pause = sockto/2
    retries = 2
    with Timer() as t:
      r = polltcp(
        blackhole_host, blackhole_port, sock_timeout=sockto, timeout=-1,
        pause=pause, retries=retries
      )
    assert r == False
    expected = int(((1 + retries) * sockto) + (retries * pause))
    assert int(t.time) in range(expected, expected + 1)
