from __future__ import absolute_import, division, print_function

import contextlib
import os

import dials_data.datasets
from six.moves.urllib.request import urlopen
from six.moves.urllib.parse import urlparse

fcntl, msvcrt = None, None
try:
    import fcntl
except ImportError:
    pass
try:
    import msvcrt
except ImportError:
    pass


@contextlib.contextmanager
def _file_lock(file_handle):
    """
    Cross-platform file locking. Open a file for writing or appending.
    Then a file lock can be obtained with:

    with open(filename, 'w') as fh:
      with _file_lock(fh):
        (..)
    """
    if not fcntl and not msvcrt:
        raise NotImplementedError("File locking not supported on this platform")
    lock = False
    try:
        if fcntl:
            flags = fcntl.LOCK_EX
            fcntl.lockf(file_handle, fcntl.LOCK_EX)
        else:
            file_handle.seek(0)
            msvcrt.locking(file_handle, msvcrt.LK_LOCK, 1)
            # note: says is only blocking for 10 sec
        lock = True
        yield
    finally:
        if lock:
            if fcntl:
                fcntl.lockf(file_handle, fcntl.LOCK_UN)
            else:
                file_handle.seek(0)
                msvcrt.locking(file_handle, msvcrt.LK_UNLCK, 1)


@contextlib.contextmanager
def download_lock(target_dir):
    """
    Obtains a (cooperative) lock on a lockfile in a target directory, so only a
    single (cooperative) process can enter this context manager at any one time.
    If the lock is held this will block until the existing lock is released.
    """
    with target_dir.join(".lock").open(mode="w", ensure=True) as fh:
        with _file_lock(fh):
            yield


def _download_to_file(url, pyfile):
    """
    Downloads a single URL to a file.
    """
    with contextlib.closing(urlopen(url)) as socket:
        file_size = int(socket.info().get("Content-Length"))
        # There is no guarantee that the content-length header is set
        received = 0
        block_size = 8192
        # Allow for writing the file immediately so we can empty the buffer
        with pyfile.open(mode="wb", ensure=True) as f:
            while True:
                block = socket.read(block_size)
                received += len(block)
                f.write(block)
                if not block:
                    break

    if file_size > 0 and file_size != received:
        raise EnvironmentError(
            "Error downloading {url}: received {received} bytes instead of expected {file_size} bytes".format(
                file_size=file_size, received=received, url=url
            )
        )


def file_hash(path):
    """Returns the SHA256 digest of a file."""
    return path.computehash(hashtype="sha256")


def fetch_dataset(
    dataset,
    ignore_hashinfo=False,
    verify=False,
    read_only=False,
    verbose=False,
    pre_scan=True,
):
    """Return a the location of a local copy of the test dataset repository.
       If this repository is not available or out of date then attempt to download/update it transparently.

       :param verbose:          Show everything as it happens.
       :param pre_scan:         If all files are present and all file sizes match
                                then skip file integrity check and exit quicker.
       :param read_only:        Only use existing data, never download anything.
                                Implies pre_scan=True.
    """
    target_dir = dials_data.datasets.repository_location().join(dataset)
    target_dir.ensure(dir=1)

    definition = dials_data.datasets.definition[dataset]
    integrity_info = definition.get("hashinfo")
    if not integrity_info or ignore_hashinfo:
        integrity_info = dials_data.datasets.create_integrity_record(dataset)

    if "verify" not in integrity_info:
        integrity_info["verify"] = [{} for source in definition["data"]]
    filelist = [
        {
            "url": source["url"],
            "file": target_dir.join(os.path.basename(urlparse(source["url"]).path)),
            "verify": hashinfo,
        }
        for source, hashinfo in zip(definition["data"], integrity_info["verify"])
    ]

    if pre_scan or read_only:
        if all(
            item["file"].check()
            and item["verify"].get("size")
            and item["verify"]["size"] == item["file"].size()
            for item in filelist
        ):
            return True
        if read_only:
            return False

    for source in filelist:  # parallelize this
        if source.get("type", "file") == "file":
            valid = False
            if source["file"].check(file=1):
                # verify
                valid = True
                if source["verify"]:
                    if source["verify"]["size"] != source["file"].size():
                        valid = False
                        print("size")
                    elif source["verify"]["hash"] != file_hash(source["file"]):
                        valid = False
                        print(
                            "hash", source["verify"]["hash"], file_hash(source["file"])
                        )

            if not valid:
                print("Downloading {}".format(source["url"]))
                _download_to_file(source["url"], source["file"])

            # verify
            valid = True
            fileinfo = {
                "size": source["file"].size(),
                "hash": file_hash(source["file"]),
            }
            if source["verify"]:
                if source["verify"]["size"] != fileinfo["size"]:
                    valid = False
                elif source["verify"]["hash"] != fileinfo["hash"]:
                    valid = False
            else:
                source["verify"]["size"] = fileinfo["size"]
                source["verify"]["hash"] = fileinfo["hash"]

    return integrity_info


class DataFetcher:
    """A class that offers access to regression datasets.

       To initialize:
           df = DataFetcher()
       Then
           df('insulin')
       returns a py.path object to the insulin data. If that data is not already
       on disk it is downloaded automatically.

       To specify where data is stored:
           df = DataFetcher('/location/where/data/can/be/stored')
       To disable all downloads:
           df = DataFetcher(read_only=True)

       Do not use this class directly in tests! Use the dials_data fixture.
    """

    def __init__(self, target_dir=None, read_only=False):
        self._cache = {}
        self._target_dir = dials_data.datasets.repository_location()
        self._read_only = read_only

    def __repr__(self):
        return "<%sDataFetcher: %s>" % (
            "R/O " if self._read_only else "",
            self._target_dir.strpath,
        )

    def result_filter(self, result):
        """
        An overridable function to mangle lookup results.
        Used in tests to transform negative lookups to test skips.
        """
        return result

    def __call__(self, test_data):
        if test_data not in self._cache:
            if self._read_only:
                data_available = fetch_dataset(test_data, pre_scan=True, read_only=True)
            else:
                with download_lock(self._target_dir):
                    # Need to acquire lock as files may be downloaded/written.
                    data_available = fetch_dataset(
                        test_data, pre_scan=True, read_only=False
                    )
            if data_available:
                self._cache[test_data] = self._target_dir.join(test_data)
            else:
                self._cache[test_data] = False
        return self.result_filter(self._cache[test_data])
