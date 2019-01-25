#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Main Bundler module containing classes and methods to handle bundling."""
from os import path
try:
    from StringIO import StringIO
except ImportError:  # pragma: no cover python 3
    from io import BytesIO as StringIO
import threading
from time import sleep
import hashlib
from tarfile import TarInfo
from tarfile import open as taropen
from datetime import datetime
from mimetypes import guess_type
from six import PY2
from ..metadata import FileObj, metadata_encode


class HashFileObj(object):
    """File like object used for reading and hashing files."""

    def __init__(self, filedesc, hashval, upref):
        """Create the hash file object."""
        self.filedesc = filedesc
        self.hashval = hashval
        self.upref = upref

    def read(self, size=-1):
        """Read wrapper function."""
        buf = self.filedesc.read(size)
        if not PY2 and not isinstance(buf, bytes):  # pragma: no cover
            buf = bytes(buf, 'UTF-8')
        self.hashval.update(buf)
        self.upref._done_size += len(buf)
        return buf

    def hashdigest(self):
        """Return the hash digest for the file."""
        return self.hashval.hexdigest()


# pylint: disable=too-few-public-methods
class Bundler(object):
    """Class to handle bundling of files to stream a tarfile."""

    md_obj = None
    file_data = None

    def __init__(self, md_obj, file_data, **kwargs):
        """
        Constructor of the bundler class.

        Add the MetaData object `md_obj` and file `file_data` to create.
        The `file_data` object should be a list of hashes. That are fed
        to TarInfo objects except for fileobj which is passed to addfile
        method.

        **Note:** The ``arcname`` keyword argument MUST be provided when calling the
        ``tarfile.TarFile.gettarinfo()`` method.

        Example MetaData Obj::

            [
              {
                'name': 'archive file path',
                'fileobj': 'open file object for read',
                'size': 'size of the file',
                'mtime': 'modify time of the file'
              }
            ]
        """
        if not md_obj.is_valid():
            raise ValueError('MetaData is not valid yet.')
        self.md_obj = md_obj
        self.file_data = file_data
        hashstr = str(kwargs.get('hashfunc', 'sha1'))
        if hashstr not in hashlib.algorithms_available:
            raise ValueError(
                '{} is not a valid hashlib algorithm.'.format(hashstr))
        self._hashfunc = getattr(hashlib, hashstr)
        self._hashstr = hashstr
        self._done_size = 0
        self._complete = False
        # this is an estimate of the total size and is used as a divisor
        # to determine percent complete, so small number is okay
        self._total_size = 0.0001

    def _save_total_size(self):
        """Build the total size from the files and save the total."""
        tsize = 0.0001
        for file_data in self.file_data:
            tsize += file_data['size']
        self._total_size = tsize

    def _setup_notify_thread(self, callback, sleeptime=5):
        """Setup a notification thread calling callback with percent complete."""
        def notify():
            """Notify the callback with percent done while not complete."""
            while not self._complete:
                sleep(sleeptime)
                callback(float(self._done_size) / self._total_size)
        notifythread = threading.Thread(target=notify)
        notifythread.daemon = True
        notifythread.start()
        return notifythread

    @staticmethod
    def _strip_subdir(fname):
        """Remove the data subdir from the file path."""
        parts = fname.split('/')  # this is posix tar standard
        if parts[0] == 'data':
            del parts[0]
        parts = [x for x in parts if x]
        return '/'.join(parts)  # this is also posix tar standard

    def _build_file_info(self, file_data, hashsum):
        """Build the FileObj to and return it."""
        arc_path = file_data['name']
        mime_type = guess_type(arc_path, strict=True)[0]
        file_time = datetime.utcfromtimestamp(
            int(file_data['mtime'])).isoformat()
        info = {
            'size': file_data['size'],
            'mimetype': mime_type if mime_type is not None else 'application/octet-stream',
            'name': path.basename(arc_path),
            'mtime': file_time,
            'ctime': file_time,
            'destinationTable': 'Files',
            'subdir': self._strip_subdir(path.dirname(arc_path)),
            'hashtype': self._hashstr,
            'hashsum': hashsum
        }
        return FileObj(**info)

    def _tarinfo_from_file_data(self, file_data):
        """Return a tarinfo object from file_data."""
        tarinfo = TarInfo(file_data['name'])
        fileobj = file_data.pop('fileobj', None)
        for key, value in file_data.items():
            setattr(tarinfo, key, value)
        fileobj = HashFileObj(fileobj, self._hashfunc(), self)
        return tarinfo, fileobj

    def stream(self, fileobj, callback=None, sleeptime=5):
        """
        Stream the bundle to the fileobj.

        This method is a blocking I/O operation.
        The ``fileobj`` should be an open file like object with 'wb' options.
        An asynchronous callback method MAY be provided via the optional ``callback``
        keyword argument. Periodically, the callback method is provided with the current
        percentage of completion.
        """
        notifythread = None
        if callable(callback):
            self._save_total_size()
            notifythread = self._setup_notify_thread(callback, sleeptime)

        tarfile = taropen(None, 'w|', fileobj)
        for file_data in self.file_data:
            tarinfo, fileobj = self._tarinfo_from_file_data(file_data)
            tarfile.addfile(tarinfo, fileobj)
            self.md_obj.append(self._build_file_info(
                file_data, fileobj.hashdigest()))
        md_txt = metadata_encode(self.md_obj)
        md_txt = md_txt if PY2 else bytes(md_txt, 'UTF-8')
        md_fd = StringIO(md_txt)
        md_tinfo = TarInfo('metadata.txt')
        md_tinfo.size = len(md_txt)
        tarfile.addfile(md_tinfo, md_fd)
        tarfile.close()
        self._complete = True

        if callable(callback):
            notifythread.join()
# pylint: enable=too-few-public-methods
