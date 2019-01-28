import time
import sys
import os

################################################################################################################
#
# A cache system for maintaining in memory a system of files under a set memory limit. The same cache can be used for
# maintaining the on-disk files (i.e., downloaded from the cloud). In the former case, the FileHold objects hold the
# data objects themselves, and when deleted from the cache, the objects themselves are removed. In the latter case,
# removing the object means deleting the file from disk.
#
# The cache maintains a stack (first in, first out) of files. Each file contains an expiration date.
#
# When an object checks the cache for a file (retrieval) several conditions are met:
# 1) The cache is searched for files beyond their expiration date and deleted. If the searched for file is one of the
#     removed files, the cache returns false. (Because the file is stale.)
# 2) The cache does not recalculate its memory limit for a retrieval. The file sizes are presumed to be static, and so
#     the cache cannot be moved over limit during a retrieval.
#
# When an object is added to the cache (deposit) several conditions are met:
# 1) Files on the stack beyond their expiration dates are removed.
# 2) If the file exists elsewhere on the cache, the cached file is removed.
# 3) The file to deposit file size is checked.
# 4) If no expiration date is provided, a time stamp very, very far in the future is used.
# 5) If the file is larger then the cache, the file is not added to the cache, and the routine returns.
# 6) Files from the bottom of the stack (deposited longest ago) are removed until the total stack plus new file is
#     below the cache file size limit.
# 7) The file is added to the top of the stack. (Last to be removed.)
#
################################################################################################################


class local_file_cache(object):

    def __init__(self, cache_size_mb, in_memory=False):
        self._in_memory = in_memory
        self._cache_size_mb = cache_size_mb
        self._file_holds = []
        self._current_cache_size = 0.0

    class FileHold():
        def __init__(self, filename, data, expiration):
            self.data = data
            self.filename = filename
            self.expiration = expiration
            self.size = sys.getsizeof(data)

    def retrieve(self, filename):
        self._remove_files_past_expiration()
        for f in self._file_holds:
            if f.filename == filename:
                return f.data

    def deposit(self, filename, data, expiration=None):
        self._remove_files_past_expiration()
        indices_to_remove = []
        for index in range(len(self._file_holds)):
            if self._file_holds[index].filename == filename:
                indices_to_remove.append(index)
        [self._delete_file_hold(index) for index in list(reversed(sorted(indices_to_remove)))]

        if expiration is None:
            expiration = time.time() + 3.14e7 # A year in seconds.
        f = local_file_cache.FileHold(filename, data, expiration)
        if f.size > self._cache_size_mb:
            return

        self._remove_files_beyond_cache_limit(f.size)
        self._file_holds.append(local_file_cache.FileHold(filename, data, expiration))

    def _remove_files_beyond_cache_limit(self, start):
        cumulative_size = start
        threshold = None
        for index in range(len(self._file_holds)-1, 0, -1):
            if cumulative_size + self._file_holds[index].size > self._cache_size_mb:
                threshold = index
                break
            cumulative_size += self._file_holds[index].size
        if threshold is not None:
            indices_to_remove = range(0, threshold + 1)
            [self._delete_file_hold(index) for index in list(reversed(sorted(indices_to_remove)))]

    def _remove_files_past_expiration(self):
        now = time.time()
        indices_to_remove = [i for i in range(len(self._file_holds)) if self._file_holds[i].expiration < now]
        [self._delete_file_hold(index) for index in list(reversed(sorted(indices_to_remove)))]
        self._current_cache_size = sum([f.size for f in self._file_holds])

    def _delete_file_hold(self, index):
        if self._in_memory:
            self._file_holds.pop(index)
        else:
            try:
                os.remove(self._file_holds[index].filename)
            except OSError:
                pass


