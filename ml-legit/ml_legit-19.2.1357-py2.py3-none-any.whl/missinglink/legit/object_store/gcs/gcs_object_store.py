# -*- coding: utf8 -*-
from .cloud_object_store import CloudObjectStore
from ...gcs_utils import do_delete_all, Downloader, Uploader


class GCSObjectStore(CloudObjectStore):
    def __init__(self, connection, bucket_name):
        super(GCSObjectStore, self).__init__(connection)
        self.__bucket_name = bucket_name
        self.__volume_id = self._connection.data_volume_config.volume_id

    def delete_all(self, max_files=None):
        return do_delete_all(self.__bucket_name, self.__volume_id, max_files)

    def __gen_upload_sync_args(self, obj):
        object_name = self._get_shafile_path(obj.sha)

        content_type = obj.content_type
        headers = self._get_content_headers(content_type)

        object_name = '%s/%s' % (self.__volume_id, object_name)

        return self.__bucket_name, object_name, obj.full_path, headers

    def __upload_async(self, obj, callback=None):
        args = self.__gen_upload_sync_args(obj)

        def on_finish(result):
            callback(obj)

        self._multi_process_control.execute(Uploader.upload_bucket, args=args, callback=on_finish if callback else None)

    def _get_loose_object_data(self, object_name):
        return Downloader.download_bucket(self.__bucket_name, object_name)

    def add_objects_async(self, objects, callback=None):
        for obj in objects:
            self.__upload_async(obj, callback=callback)
