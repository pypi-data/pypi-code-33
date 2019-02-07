from onepanel.utilities.file import get_file_tree
from onepanel.utilities.time import UTC

from os.path import join

import os.path
import datetime


class FileDifference:
    class State:
        MODIFIED = 'modified'
        NEW = 'new'
        DELETED = 'deleted'
    
    def __init__(self, source_path, destination_path, state):
        """
        :param source_path: The source path of the file, assumed to be a filesystem path
        :type source_path: str
        :param destination_path: The destination path of the file, format is dependent on service used, like S3.
        :type destination_path: str
        :param state: The state of the file difference, NEW|MODIFIED|DELETED. We assume that the difference
                      is from source to destination. E.g. source file is NEW relative to destination.
        :type state: str (one of the constants in FileDifference.State)
        """
        self.source_path = source_path
        self.destination_path = destination_path
        self.state = state


class FileSynchronizer:
    LOCAL = 0
    REMOTE = 1

    @staticmethod
    def local_file_stats(filepath):
        return {
            'last_modified': datetime.datetime.fromtimestamp(os.path.getmtime(filepath), UTC),
            'size': os.path.getsize(filepath)
        }
    
    @staticmethod
    def s3_file_stats(api_content):
        return {
            'last_modified': api_content['LastModified'],
            'size': api_content['Size']
        }

    @staticmethod
    def content_modification_difference(a, b):
        """
        Files are different if a has been modified after b, or, if equal,
        if the file sizes are different.
        :param a:
        :param b:
        :return:
        """
        if a['last_modified'] > b['last_modified']:
            return True

        return a['size'] != b['size']

    def __init__(self, filepath, s3_prefix, s3_wrapper, master=LOCAL):
        """
        :param filepath:
        :type filepath str
        :param s3_prefix:
        :type s3_prefix str
        :param s3_wrapper:
        :type s3_wrapper onepanel.lib.s3.wrapper.Wrapper
        :param master: Determines if the local files or the remote files are considered to be
                       the "master" and the opposite side should change its files to match it.
        :type master int one of the constants in FileSynchronizer
        """
        self.filepath = filepath
        self.s3_prefix = s3_prefix
        self.master = master
        self.s3_wrapper = s3_wrapper

    def find_difference(self, comparator=None):
        """ Finds the differences in files between the file_path and s3_prefix using
        the provided master.
        :return: a map of the file differences. Key is file path locally, value is a FileDifference
        :type {}
        """

        if comparator is None:
            comparator = FileSynchronizer.content_modification_difference

        differences = {}

        s3_keys = self.s3_wrapper.list_files(self.s3_prefix)
        files = get_file_tree(self.filepath)

        # +1 to remove filepath separator
        local_filepath_length = len(self.filepath) + 1

        for filepath in files:
            path = join(self.s3_prefix, filepath[local_filepath_length:])
            if path in s3_keys:
                modified = comparator(FileSynchronizer.local_file_stats(filepath),
                                      FileSynchronizer.s3_file_stats(s3_keys[path]))

                if modified:
                    differences[filepath] = FileDifference(filepath, path, FileDifference.State.MODIFIED)

                del s3_keys[path]
            else:
                differences[filepath] = FileDifference(filepath, path, FileDifference.State.NEW)

        s3_prefix_length = len(self.s3_prefix)
        for remote_path in s3_keys.keys():
            local_path = join(self.filepath, remote_path[s3_prefix_length:])
            differences[local_path] = FileDifference(local_path, remote_path, FileDifference.State.DELETED)

        return differences

    def synchronize(self, file_differences, hook):
        for difference in file_differences:
            hook(difference)
            self.synchronize_single(difference)

    def synchronize_single(self, file_difference):
        """
        Synchronizes the file between local and remote. Uses the master specified in the constructor.

        :param file_difference:
        :type file_difference FileDifference
        :return: result of the sync
        """

        if self.master == FileSynchronizer.LOCAL:
            self._synchronize_local_master(file_difference)
        else:
            self._synchronize_remote_master(file_difference)

    def _synchronize_local_master(self, file_difference):
        if file_difference.state == FileDifference.State.NEW:
            self.s3_wrapper.upload_file(file_difference.source_path, file_difference.destination_path)
            pass
        elif file_difference.state == FileDifference.State.MODIFIED:
            self.s3_wrapper.upload_file(file_difference.source_path, file_difference.destination_path)
        elif file_difference.state == FileDifference.State.DELETED:
            self.s3_wrapper.delete_file(file_difference.destination_path)

    def _synchronize_remote_master(self, file_difference):
        raise NotImplementedError("Not implemented.")
