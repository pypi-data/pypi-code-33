# -*- coding: utf8 -*-

import logging
from collections import OrderedDict
from ...connection_mixin import ConnectionMixin
from ...dulwich.object_store import BaseObjectStore
from ...dulwich.objects import hex_to_filename, Blob


class CloudObjectStore(ConnectionMixin, BaseObjectStore):
    def __init__(self, connection):
        super(CloudObjectStore, self).__init__(connection)
        self.__volume_id = self._connection.data_volume_config.volume_id
        self._multi_process_control = None

    def set_multi_process_control(self, multi_process_control):
        self._multi_process_control = multi_process_control

    @classmethod
    def _get_shafile_path(cls, sha):
        # Check from object dir
        return hex_to_filename('objects', sha)

    def _get_loose_object_data(self, object_name):
        pass

    def _get_loose_object(self, metadata):
        logging.debug('get object %s', metadata)

        sha = metadata['@id']

        object_name = '%s/%s' % (self.__volume_id, self._get_shafile_path(sha))

        data = self._get_loose_object_data(object_name)

        blob = Blob()
        blob.set_raw_chunks([data], sha)
        return blob

    def get_raw(self, metadata):
        """Obtain the raw text for an object.

        :param metadata: metadata for the object.
        :return: tuple with numeric type and object contents.
        """
        ret = self._get_loose_object(metadata)
        if ret is not None:
            return ret.type_num, ret.as_raw_string()

        raise KeyError(metadata)

    @classmethod
    def _get_content_headers(cls, content_type=None):
        headers = OrderedDict()
        if content_type:
            headers['Content-Type'] = content_type

        return headers

    @property
    def packs(self):
        raise NotImplementedError(self.packs)

    def __iter__(self):
        raise NotImplementedError(self.__iter__)

    def contains_packed(self, sha):
        raise NotImplementedError(self.contains_packed)

    def contains_loose(self, sha):
        raise NotImplementedError(self.contains_loose)
