# -*- coding: utf8 -*-
import json
import logging
import os
from .path_utils import has_moniker


class MetadataJsonFile(object):
    @classmethod
    def validate_json_file(cls, metadata_json_file):
        from .data_sync import InvalidJsonFile

        with open(metadata_json_file) as metadata_file:
            try:
                data = json.load(metadata_file)
            except ValueError as ex:
                raise InvalidJsonFile(metadata_json_file, ex)

        return data

    @classmethod
    def validate_duplicate_keys(cls, metadata_json_file):
        from .data_sync import InvalidJsonFileDuplicateFields

        data = cls.validate_json_file(metadata_json_file)

        keys = data.keys()
        current_keys = {}
        duplicate_keys = []
        for key in keys:
            key_lower = key.lower()
            if key_lower in current_keys:
                duplicate_keys.append(key)
                continue

            current_keys[key_lower] = key

        if len(duplicate_keys) > 0:
            raise InvalidJsonFileDuplicateFields(metadata_json_file, 'duplicate keys %s' % (','.join(duplicate_keys)))

        return data


class MetadataFiles(object):
    metadata_ext = '.metadata.json'

    @classmethod
    def __meta_companion_file_name(cls, metadata_file_name):
        return metadata_file_name[:-len(cls.metadata_ext)]

    @classmethod
    def __is_meta_folder_file_name(cls, metadata_file_name):
        return os.path.basename(metadata_file_name).lower() == 'folder' + cls.metadata_ext

    @classmethod
    def convert_data_unsupported_type(cls, data):
        result = {}
        for key, val in data.items():
            if isinstance(val, (dict, list)):  # we convert arrays and dicts into string as we don't support them yet
                val = json.dumps(val)
                key += '_json'

            result[key] = val

        return result

    @classmethod
    def __handle_json_file(cls, metadata_json_file, on_data):
        data = MetadataJsonFile.validate_duplicate_keys(metadata_json_file)

        return on_data(data)

    @classmethod
    def __get_metadata_info(cls, data_path, rel_metadata_file_name):
        full_path_metadata = os.path.join(data_path, rel_metadata_file_name)

        if has_moniker(full_path_metadata):
            return rel_metadata_file_name, {}

        rel_path_key = rel_metadata_file_name[:-len(cls.metadata_ext)]

        def handle_data(data):
            processed_data = cls.convert_data_unsupported_type(data)

            return rel_path_key, processed_data

        return cls.__handle_json_file(full_path_metadata, handle_data)

    @classmethod
    def __get_folder_metadata_info(cls, data_path, rel_metadata_file_name):
        full_path_metadata = os.path.join(data_path, rel_metadata_file_name)

        rel_path = os.path.relpath(os.path.dirname(full_path_metadata), data_path)

        if rel_path == '.':
            rel_path = ''

        def handle_data(all_files_data):
            for filename, file_data in all_files_data.items():
                processed_file_data = cls.convert_data_unsupported_type(file_data)
                rel_path_key = os.path.join(rel_path, filename)

                yield rel_path_key, processed_file_data

        return cls.__handle_json_file(full_path_metadata, handle_data)

    @classmethod
    def __get_metadata(cls, data_path, data_files_info, metadata_rel_file_name):
        if cls.__is_meta_folder_file_name(metadata_rel_file_name):
            for rel_path_key, data in cls.__get_folder_metadata_info(data_path, metadata_rel_file_name):
                yield rel_path_key, data
        elif cls.__meta_companion_file_name(metadata_rel_file_name) in data_files_info:
            rel_path_key, data = cls.__get_metadata_info(data_path, metadata_rel_file_name)

            yield rel_path_key, data
        else:
            logging.debug("file %s doesn't have a data point file", metadata_rel_file_name)

    @classmethod
    def load_all_metadata(cls, data_path, data_files_info, metadata_files_list, no_progressbar=False):
        from tqdm import tqdm

        files_metadata = {}
        if len(metadata_files_list) == 0:
            return files_metadata

        for metadata_rel_file_name in tqdm(metadata_files_list, desc='Read metadata', unit=' files', ncols=80, disable=no_progressbar):
            for rel_path_key, data in cls.__get_metadata(data_path, data_files_info, metadata_rel_file_name):
                files_metadata.setdefault(rel_path_key, {}).update(data)

        return files_metadata
