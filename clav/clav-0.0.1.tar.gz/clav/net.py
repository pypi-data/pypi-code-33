import logging
import os
import socket
import urllib.request
import urllib.error
from socket import AF_INET, SOCK_STREAM
from clav import time
from clav.hash import checkhash, HashError
from clav.random import rrange

def wget(url, path, overwrite=False):
  '''
  Download a file.

  :param str url: url to file
  :param str path: local save path
  :param bool overwrite: when path exists, overwrite if True, raises
    FileExistsError if False
  '''
  res = False
  if os.path.isfile(path):
    if overwrite:
      res = True
    else:
      raise FileExistsError("File exists: " + path)
  urllib.request.urlretrieve(url, path)
  return res

wget.HTTPError = urllib.error.HTTPError
wget.URLError = urllib.error.URLError

def download(url, path, alg=None, sum=None):
  '''
  Download a file with a known hash. If a file exists but doesn't
  match the hash, it is unlinked and re-downloaded. If the downloaded
  file doesn't match its expected hash, an exception is raised.

  :param str url: url to file
  :param str path: local save path
  :param str alg: hashlib algorithm name
  :param str sum: file hash
  :returns: True if the file was downloaded, False if the file already exists
  :rtype bool:
  :raises download.error: if the file doesn't match the expected hash
  '''
  log = logging.getLogger(f'{__name__}.{download.__name__}')
  if alg and not sum or sum and not alg:
    raise ValueError('alg and sum are mutually inclusive')
  def remove_failed_download(reraise=False):
    if os.path.isfile(path):
      try:
        os.unlink(path)
      except Exception:
        msg = f'Exception while removing failed download: {path}'
        log.warning(msg, exc_info=True)
        if reraise:
          raise
  if os.path.isfile(path):
    if alg is None:
      return False
    try:
      checkhash(path, alg, sum)
      return False
    #except checkhash.error:
    except HashError:
      remove_failed_download(reraise=True)
  try:
    wget(url, path)
    if alg:
      checkhash(path, alg, sum)
    return True
  except:
    remove_failed_download()
    raise

download.error = checkhash.error

def polltcp(host, port, sock_timeout=5, timeout=30, pause=2, retries=-1):
  '''
  Poll a host's port.

  :param str host: host address
  :param str port: host port
  :param float sock_timeout: socket connect timeout
  :param float timeout: max seconds this function may spend polling
  :param float pause: seconds between polls
  :param int retries: number of retries
  :returns: True if port was polled successfully, else False
  :rtype bool:
  '''
  def test():
    sock = socket.socket(AF_INET, SOCK_STREAM)
    sock.settimeout(sock_timeout)
    try:
      sock.connect((host, int(port)))
      sock.close()
      return True
    except (socket.error, socket.timeout, ConnectionError):
      return False
  return time.poll(test, timeout=timeout, pause=pause, retries=retries)

def ephemeral_port(host='0.0.0.0'):
  'Return a free ephemeral TCP port number for address host.'

  # IANA:  49152-65535
  # Linux: 32768-61000
  for _ in rrange(49152, 61000):
    try:
      with socket(AF_INET, SOCK_STREAM) as s:
        s.bind((host, _))
      return _
    except OSError:
      continue
  else:
    raise RuntimeError('No free ephemeral ports') # well good night Irene
