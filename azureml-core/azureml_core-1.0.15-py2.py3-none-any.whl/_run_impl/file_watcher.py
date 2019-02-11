# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import os
import uuid
import multiprocessing

from threading import Thread, Event

from azureml._file_utils import get_block_blob_service_credentials

from azureml._history.async_request import AsyncRequest
from azureml._history.utils.task_queue import TaskQueue


class AwaitableUpload():
    def __init__(self, fullpath, files_watched, upload_info, logger):
        self.fullpath = fullpath
        self.files_watched = files_watched
        self.upload_info = upload_info
        self.logger = logger.getChild("AwaitableUpload")

    def result(self):
        last_uploaded_byte = self.files_watched[self.fullpath]
        (blob_service, container_name, blob_name) = self.upload_info[self.fullpath]
        chunk_size_bytes = os.environ.get("AZUREML_UPLOAD_CHUNK_SIZE_BYTES", 4 * 1000 * 1024)

        try:
            with open(self.fullpath, 'rb') as data:
                data.seek(last_uploaded_byte)
                read_bytes = data.read(chunk_size_bytes)
                if not read_bytes:
                    return
                blob_service.append_blob_from_bytes(container_name, blob_name, read_bytes)
                last_uploaded_byte += len(read_bytes)
                self.files_watched[self.fullpath] = last_uploaded_byte
        except Exception as ex:
            self.logger.debug("Failed to update blob with error:\n{}".format(ex))
            return


class UploadTask(AsyncRequest):
    def __init__(self, fullpath, files_watched, upload_info, files_uploading, logger):
        ident = str(uuid.uuid4())
        self.fullpath = fullpath
        self.upload = AwaitableUpload(fullpath, files_watched, upload_info, logger)
        self.files_uploading = files_uploading
        super(UploadTask, self).__init__(request=self.upload, ident=ident, handler=None, logger=logger)

    def wait(self):
        self.upload.result()
        self.files_uploading.remove(self.fullpath)

    def result(self):
        return self.wait()


class FileWatcher(Thread):
    def __init__(self, logspath, origin, container, artifacts_client, logger, parallelism=None):
        # Note: tried to use the Daemon base class, but it
        # doesn't provide the event mechanism to break away
        # from sleep earlier than the specified interval when
        # finish is called
        super(FileWatcher, self).__init__(daemon=True)
        self.logspath = logspath
        self.origin = origin
        self.container = container
        self.artifacts_client = artifacts_client
        self.logger = logger.getChild("FileWatcher")
        self._event = Event()
        if parallelism is None:
            parallelism = multiprocessing.cpu_count()
        self.parallelism = parallelism

    def create_artifacts(self, new_files):
        try:
            paths = [fullpath for (leaf_file, fullpath) in new_files]
            posix_paths = [os.path.normpath(path).replace(os.sep, '/') for path in paths]
            posix_to_local = dict(zip(posix_paths, paths))
            # Create artifact to get sas URL
            res = self.artifacts_client.create_empty_artifacts(self.origin,
                                                               self.container,
                                                               posix_paths)

            artifact_keys = list(res.artifacts.keys())
            artifacts = [res.artifacts[artifact_name] for artifact_name in artifact_keys]
            returned_paths = [posix_to_local[artifact.path] for artifact in artifacts]
            artifact_uris = [res.artifact_content_information[name].content_uri for name in artifact_keys]
            return (artifact_uris, returned_paths, True)
        except Exception as ex:
            self.logger.debug("Exception creating artifacts:\n{}".format(ex))
            return ([], [], False)

    def create_blobs(self, artifact_uris, files_watched, upload_info, full_paths):
        from azure.storage.blob import AppendBlobService
        try:
            for artifact_uri, fullpath in zip(artifact_uris, full_paths):
                sas_token, account_name, container_name, blob_name = get_block_blob_service_credentials(artifact_uri)
                # Create the blob service and blob to upload file to
                blob_service = AppendBlobService(account_name=account_name, sas_token=sas_token)
                blob_service.create_blob(container_name, blob_name)
                self.logger.debug("uploading data to container: {} blob: {} path: {}".format(container_name,
                                                                                             blob_name,
                                                                                             fullpath))
                files_watched[fullpath] = 0
                upload_info[fullpath] = (blob_service, container_name, blob_name)
            return True
        except Exception as ex:
            self.logger.debug("Exception creating blobs:\n{}".format(ex))
            return False

    def walk_files(self, files_watched, files_uploading, upload_info, tq, current_stat):
        leaf_files = [(leaf_file, os.path.join(root, leaf_file)) for root, dirs, files
                      in os.walk(self.logspath) for leaf_file in files]
        # Ignore hidden files
        visible_files = [(leaf_file, fullpath) for (leaf_file, fullpath)
                         in leaf_files if not leaf_file.startswith(".")]
        new_files = [(leaf_file, fullpath) for (leaf_file, fullpath)
                     in leaf_files if fullpath not in files_watched]
        if new_files:
            # For all new files do a batch create
            (artifact_uris, full_paths, success) = self.create_artifacts(new_files)
            # Exit on error, stop watcher
            if not success:
                self.logger.debug("Exiting File Watcher due to errors with creating artifacts\n")
                return
            # For new files create all blobs in storage
            success = self.create_blobs(artifact_uris, files_watched, upload_info, full_paths)
            # Exit on error, stop watcher
            if not success:
                self.logger.debug("Exiting File Watcher due to errors with creating blobs\n")
                return

        try:
            # Iterate over all files and create a task to upload a chunk of data
            for (leaf_file, fullpath) in visible_files:
                # Check if file size has changed, ignore files that haven't changed
                filesize = os.stat(fullpath).st_size
                if files_watched[fullpath] >= filesize:
                    continue
                current_stat[fullpath] = filesize
                if fullpath not in files_uploading:
                    files_uploading.add(fullpath)
                    # start an async task to upload the file
                    tq.add(UploadTask(fullpath, files_watched, upload_info, files_uploading, self.logger))
        except Exception as ex:
            self.logger.debug("Exiting File Watcher due to errors creating upload tasks:\n{}".format(ex))
            return
        sleep_interval_sec = 10
        self._event.wait(timeout=sleep_interval_sec)

    def uploaded_to_stat(self, files_watched, last_stat):
        for file_watched in files_watched:
            if file_watched in last_stat and last_stat[file_watched] > files_watched[file_watched]:
                return False
        return True

    def run(self):
        files_watched = {}
        # Take a stat of the current directory
        current_stat = {}
        files_uploading = set()
        upload_info = {}
        tq = TaskQueue("UploadQueue", self.logger, num_workers=self.parallelism)
        while not self._event.is_set():
            self.walk_files(files_watched, files_uploading, upload_info, tq, current_stat)
        self.logger.debug("FileWatcher received exit event, getting current_stat")
        # Walk until files have uploaded at least to last stat
        # If more data has been uploaded since the last stat from some other process we won't continue to upload
        self.walk_files(files_watched, files_uploading, upload_info, tq, current_stat)
        self.logger.debug("FileWatcher retrieved current_stat, will upload to current_stat")
        dummy_stat = {}
        while (not self.uploaded_to_stat(files_watched, current_stat)):
            self.logger.debug("FileWatcher uploading files to current_stat...")
            self.walk_files(files_watched, files_uploading, upload_info, tq, dummy_stat)
        self.logger.debug("FileWatcher finished uploading to current_stat, finishing task queue")
        # Finish the task queue
        tq.finish()
        self.logger.debug("FileWatcher task queue finished, exiting")

    def finish(self):
        self.logger.debug("FileWatcher called finish, setting event")
        self._event.set()
