# -*- coding: utf8 -*-
import json
import threading
from contextlib import closing
import requests
import importlib
from missinglink.core.config import Config
from missinglink.core.eprint import eprint
from missinglink.core.exceptions import AccessDenied, NotFound
import logging


logger = logging.getLogger(__name__)


class DownloadEntity(object):
    local_data = threading.local()

    @classmethod
    def __object_from_data(cls, data, creator):
        data_key = json.dumps(data, sort_keys=True)

        data_key += creator.__name__

        try:
            return cls.local_data.__data_sync_objects[data_key]
        except KeyError:
            cls.local_data.__data_sync_objects[data_key] = creator(data)
        except AttributeError:
            cls.local_data.__data_sync_objects = {data_key: creator(data)}

        return cls.local_data.__data_sync_objects[data_key]

    @classmethod
    def _import_storage(cls, storage_class):
        module_name, class_name = storage_class.rsplit('.', 1)
        m = importlib.import_module(module_name)
        return getattr(m, class_name)

    @classmethod
    def _get_storage(cls, current_data):
        current_data_clone = dict(current_data)
        storage_class = current_data_clone.pop('class')
        return cls._import_storage(storage_class).init_from_config(**current_data_clone)

    @classmethod
    def _get_config(cls, current_data):
        return Config(**current_data)

    @classmethod
    def _get_item_data(cls, repo, storage, metadata):
        if storage.has_item(metadata):
            logger.debug('already exists %s', metadata)
            return

        _, current_data = repo.object_store.get_raw(metadata)
        return current_data

    @classmethod
    def _get_config_from_init_config(cls, config_init_dict):
        if 'config' in config_init_dict:
            return config_init_dict['config']

        return cls.__object_from_data(config_init_dict, cls._get_config)

    @classmethod
    def _get_storage_from_init_config(cls, config_init_dict):
        storage_config_or_storage = config_init_dict.get('storage')

        if isinstance(storage_config_or_storage, dict):
            storage = cls.__object_from_data(storage_config_or_storage, cls._get_storage)
        else:
            storage = storage_config_or_storage

        return storage

    @classmethod
    def download(cls, config_init_dict, volume_id, metadata, headers):
        from .data_volume import with_repo

        config = cls._get_config_from_init_config(config_init_dict)

        storage = cls._get_storage_from_init_config(config_init_dict)

        session = requests.session()
        session.headers.update(headers)

        with with_repo(config, volume_id, read_only=True, session=session) as repo:
            with closing(storage):
                data = cls._get_item_data(repo, storage, metadata)
                if data is not None:
                    storage.add_item(metadata, data)
