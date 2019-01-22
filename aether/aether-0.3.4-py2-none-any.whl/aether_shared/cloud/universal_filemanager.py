import os
import random
import string
import tempfile
import urllib
import aether_shared.sharedconfig as cfg

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

########################################################################################################################
#
# The Universal Filemanager handles accessing of files whether they are local or in the cloud through the same
#  interface. To do so, the filemanager uses the concept of the stub. A stub is a relative pathname, which the
#  filemanager can interpret to point to the absolute location of the file, whether in a local data directory, the
#  cloud, or through a URL.
#
# Here are the rules for retrieve_stub:
# A stub may be either an http:// url; a gs:// url; or a filename stub is considered to be a local path.

# A http:// url is downloaded into a local temporary filename, and the direct filename to that temporary file
#  is returned.
# A gs:// url is parsed into its bucket and blob, then downloaded into a local temporary file, and the direct file-
#  name is returned.
# A filename stub is presumed to be in the google cloud storage (if Operation.CLOUD), in which case it is downloaded
#  into a local file which is returned, or presumed to be local (if Operation.LOCAL), in which case the filestub
#  is prepended with the working directory of local storage on the disk, and returned.
#
# The end goal is to return direct filenames to the new resources on the disk. Note that this makes no account for
# caching the files or awareness that the file has been downloaded at all.
#
# To retain knowledge of cached data files, a cache will be maintained as a stack, with each resource logged in
# order of use and its expiration date. The cache will clear files from its stack first in last out, whenever new
# files are added to the cache and checked for validation each time a new file is added to the cache (since this
# marks each operation in which a cache object may be used).
#
########################################################################################################################

import os
import time
import aether_shared.sharedconfig as cfg

class disk_cache_ttl(object):

    class reference(object):
        def __init__(self, url, file_obj):
            self.url = url
            self.file_obj = file_obj
            self.disk_size = os.path.getsize(file_obj.name)
            self.date_added = time.time()
            self.date_accessed = time.time()

    def __init__(self,
                 max_disk_cache_size_gb=cfg.max_disk_cache_size_gb,
                 max_time_before_expiration_s=cfg.max_time_before_expiration_s,
                 ):
        self.cache = {}
        self.current_disk_cache_size = 0
        self.max_disk_cache_size = max_disk_cache_size_gb * 1024 * 1024 * 1024
        self.max_time_before_expiration_s = max_time_before_expiration_s

    def update(self, url, file_obj):
        """Update cache, removing oldest as necessary."""
        if url in self.cache:
            self.remove_url(url)

        ref = disk_cache_ttl.reference(url, file_obj)
        self._remove_cache_items_past_expiration()
        self._remove_oldest_until_below_threshold(self.max_disk_cache_size - ref.disk_size)

        self.cache[url] = ref
        self.current_disk_cache_size += ref.disk_size
        logger.info("Adding to cache: {} referencing {}, new size {}".format(
            self.cache[url].file_obj.name, url, self.current_disk_cache_size))

    def get(self, url):
        """Get an object from the cache and update its access date, or return None if not found."""
        self._remove_cache_items_past_expiration()

        if url in self.cache:
            self.cache[url].date_accessed = time.time()
            logger.info("Found in cache: {} referencing {}".format(
                self.cache[url].file_obj.name, url))
            return self.cache[url].file_obj
        return None

    def remove_url(self, url):
        if url not in self.cache:
            logger.warn("Requested url for deletion not found in cache: {}".format(url))
            return

        self.current_disk_cache_size -= self.cache[url].disk_size
        logger.info("Removing from cache: {} referencing {}: size {}".format(
            self.cache[url].file_obj.name, url, self.current_disk_cache_size))
        del self.cache[url]

    def _remove_oldest_until_below_threshold(self, max_threshold):
        """Remove the oldest entries until the cache size is below threshold."""
        while self.current_disk_cache_size > max_threshold and len(self.cache) > 0:
            oldest_entry = None
            for url in self.cache.keys():
                if oldest_entry is None:
                    oldest_entry = url
                elif self.cache[url].date_accessed < self.cache[oldest_entry].date_accessed:
                    oldest_entry = url
            self.remove_url(oldest_entry)

    def _remove_cache_items_past_expiration(self):
        for url in self.cache.keys():
            delta = time.time() - self.cache[url].date_accessed
            if delta > self.max_time_before_expiration_s:
                self.remove_url(url)


class universal_filemanager(object):

    def __init__(self,
                 cloud_storage_client,
                 use_disk_cache=cfg.use_disk_cache,
                 use_search_local_for_urls=cfg.use_search_local_for_urls):
        self._cloud_storage_client = cloud_storage_client

        self.use_search_local_for_urls = use_search_local_for_urls
        self.use_disk_cache = use_disk_cache
        if use_disk_cache:
            self.disk_cache = disk_cache_ttl()

    def _stub_as_filename(self, stub):
        stub = stub.replace("://", "/")
        if stub.split("/")[0] == "https":
            stub = "/".join(["http"] + stub.split("/")[1:])
        return stub

    def stub_exists(self, stub):
        if stub.startswith("gs://"):
            bucket = stub[5:].split("/")[0]
            blobname = "/".join(stub[5:].split("/")[1:])
            return self._cloud_storage_client.blob_exists(bucket, blobname)
        elif stub.startswith("user://"):
            bucket = cfg._cloud_filesystem_user_bucket
            blobname = stub[7:]
            return self._cloud_storage_client.blob_exists(bucket, blobname)

    def retrieve_stubs(self, stubs):
        return [self.retrieve_stub(s) for s in stubs]

    def retrieve_stub(self, stub):
        if self.use_disk_cache:
            file = self.disk_cache.get(stub)
            if file is not None:
                logger.debug("Retrieving from cache url {}".format(stub))
                return file

        if self.use_search_local_for_urls:
            local_filename = cfg._local_filesystem_directory + self._stub_as_filename(stub)
            if os.path.isfile(local_filename):
                return open(local_filename, "r")

        if stub.startswith("http://") or stub.startswith("https://"):
            try:
                logger.debug("Downloading url {}".format(stub))
                temporary_file = tempfile.NamedTemporaryFile(delete=True)
                urllib.URLopener().retrieve(stub, temporary_file.name)
                if self.use_disk_cache:
                    self.disk_cache.update(stub, temporary_file)
                return temporary_file
            except Exception:
                logger.error("Failed to download url {}".format(stub), exc_info=True)
                return None

        elif stub.startswith("gs://"):
            try:
                logger.debug("Downloading gs url {}".format(stub))
                temporary_file = tempfile.NamedTemporaryFile(delete=True)
                bucket = stub[5:].split("/")[0]
                blobname = "/".join(stub[5:].split("/")[1:])
                self._cloud_storage_client.download_blob(bucket, blobname, temporary_file.name)
                if self.use_disk_cache:
                    self.disk_cache.update(stub, temporary_file)
                return temporary_file
            except Exception:
                logger.error("Failed to download gs url {}.".format(stub), exc_info=True)
                return None

        elif stub.startswith("user://"):
            try:
                logger.debug("Downloading from user cloud filesystem url {}".format(stub))
                temporary_file = tempfile.NamedTemporaryFile(delete=True)

                bucket = cfg._cloud_filesystem_user_bucket
                blobname = stub[7:]
                self._cloud_storage_client.download_blob(bucket, blobname, temporary_file.name)
                if self.use_disk_cache:
                    self.disk_cache.update(stub, temporary_file)
                return temporary_file
            except Exception:
                logger.error("Failed to download user url {}.".format(stub), exc_info=True)
                return None
        # else:
        #     logger.debug("Loading from local filesystem {}".format(stub))
        #     local_stub_location = cfg._local_filesystem_directory + stub
        #
        #     if os.path.isfile(local_stub_location):
        #         return open(local_stub_location, "r")
        #     else:
        #         logger.error("File does not exist locally {}.".format(local_stub_location))
        #         return None

    def upload_stub(self, local_file, stub):
        if stub.startswith("user://"):
            try:
                logger.debug("Uploading to user cloud filesystem url {}".format(stub))

                bucket = cfg._cloud_filesystem_user_bucket
                blobname = stub[7:]
                self._cloud_storage_client.upload_blob(bucket, local_file.name, blobname)
                return True
            except Exception:
                logger.error("Failed to upload user url {}.".format(stub), exc_info=True)
                return False

        if stub.startswith("gs://"):
            try:
                logger.debug("Uploading to gs url {}".format(stub))
                bucket = stub[5:].split("/")[0]
                blobname = "/".join(stub[5:].split("/")[1:])
                self._cloud_storage_client.upload_blob(bucket, local_file.name, blobname)
                return True
            except Exception:
                logger.error("Failed to upload gs url {}.".format(stub), exc_info=True)
                return False
        else:
            logger.error("Attempting to upload unknown or unaccepted protocol {}.".format(stub))
            return False

    @staticmethod
    def _alphanumeric_id_generator(length=16, chars=string.ascii_uppercase + string.digits):
        return ''.join(random.choice(chars) for _ in range(length))
