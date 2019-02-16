# -*- coding: utf8 -*-
import json
import logging
import time

from concurrent.futures import ThreadPoolExecutor
from missinglink.core.avro_utils import AvroWriter

from .metadata_db import MetadataOperationError
from .metadata_db.limit_visitor import LimitVisitor
from .scam import QueryParser, visit_query
from .download_entity import DownloadEntity
from .metadata_files import MetadataFiles

try:
    # noinspection PyPep8Naming
    import cPickle as pickle
except ImportError:
    import pickle

import random
import string
import tempfile
from contextlib import closing
import sys
import os
from uuid import uuid4
import datetime
from six import wraps
from missinglink.core.api import ApiCaller
from missinglink.core.json_utils import normalize_item, dict_normalize
from missinglink.core.multi_process_control import get_multi_process_control
from .path_utils import get_batch_of_files_from_paths, safe_make_dirs, DestPathEnum, enumerate_paths_with_info
from missinglink.core.print_status import PrintStatus
from missinglink.core.eprint import eprint


def wrap_exceptions(fn):
    @wraps(fn)
    def decorated(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except AssertionError:
            raise
        except Exception as ex:
            logging.exception('failed')
            eprint('\n' + str(ex))
            sys.exit(1)

    return decorated


epoch = datetime.datetime.utcfromtimestamp(0)


class InvalidJsonFile(Exception):
    def __init__(self, filename, ex):
        self.filename = filename
        self.ex = ex

    def __str__(self):
        return '<%s(%r)> (%s)' % (self.__class__.__name__, self.filename, self.ex)


class InvalidJsonFileDuplicateFields(InvalidJsonFile):
    pass


def _download_entity(config_init_dict, volume_id, metadata, headers):
    return DownloadEntity.download(config_init_dict, volume_id, metadata, headers)


def chop_microseconds(delta):
    return delta - datetime.timedelta(microseconds=delta.microseconds)


def status_with_timing(message, callback, fp=sys.stdout, on_summery_data=None):
    start_time = datetime.datetime.utcnow()
    status_line = PrintStatus(fp=fp)
    with closing(status_line):
        status_line.print_status(message)

        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(callback)

            while future.running():
                total_time = chop_microseconds(datetime.datetime.utcnow() - start_time)
                status_line.print_status("%s %s" % (message, total_time))

                time.sleep(0.1)

            result = future.result()
            total_time = chop_microseconds(datetime.datetime.utcnow() - start_time)

            if on_summery_data is not None:
                summery_data = on_summery_data(result)
                summery_data = '%s, %s' % (total_time, summery_data)
            else:
                summery_data = str(total_time)

            status_line.print_status('%s Done (%s)' % (message, summery_data))

    return result


def disk_result(resume_token, method, result_callback=None):
    def wrap_f(f):
        def wrap(*args, **kwargs):
            import tempfile

            def loader():
                cache_result = pickle.load(cache_file)
                if result_callback is not None:
                    result_callback(cache_result)

                return cache_result

            name = '{func_name}_{python_version}'.format(func_name=method, python_version=sys.hexversion)
            full_path = os.path.join(tempfile.gettempdir(), 'ml_cache', resume_token, name)

            try:
                with open(full_path, 'rb') as cache_file:
                    return status_with_timing('Loading cache file', loader)
            except (IOError, OSError):
                pass
            except Exception as ex:
                logging.debug('failed to load %s %s', full_path, ex)

            result = f(*args, **kwargs)

            full_path_tmp = full_path + '.tmp'
            try:
                safe_make_dirs(os.path.dirname(full_path_tmp))
                with open(full_path_tmp, 'wb') as cache_file:
                    pickle.dump(result, cache_file, pickle.HIGHEST_PROTOCOL)
                    os.rename(full_path_tmp, full_path)
            except Exception as ex:
                logging.info('failed to save %s %s', full_path_tmp, ex)

            return result

        return wrap

    return wrap_f


class DiskStorage(object):
    def __init__(self, dest_pattern, save_meta):
        self.__dest_pattern = dest_pattern
        self.__save_meta = save_meta

    def close(self):
        pass

    @classmethod
    def _atomic_rename_tmp(cls, full_file_name):
        full_json_filename_tmp = cls._make_tmp_filename(full_file_name)

        try:
            os.rename(full_json_filename_tmp, full_file_name)
        except OSError:
            pass

    @classmethod
    def _make_tmp_filename(cls, full_json_filename):
        return full_json_filename + '.tmp'

    def add_item(self, metadata, data):
        full_filename = DestPathEnum.get_full_path(self.__dest_pattern, metadata)
        safe_make_dirs(os.path.dirname(full_filename))

        full_json_filename = full_filename + '.metadata.json'

        if self.__save_meta:
            item_meta = {key: val for key, val in metadata.items() if not key.startswith('@')}
            with open(self._make_tmp_filename(full_json_filename), 'w') as f:
                json.dump(item_meta, f)

            self._atomic_rename_tmp(full_json_filename)

        with open(self._make_tmp_filename(full_filename), 'wb') as f:
            f.write(data)

        self._atomic_rename_tmp(full_filename)

    def has_item(self, metadata):
        full_filename = DestPathEnum.get_full_path(self.__dest_pattern, metadata)
        return os.path.isfile(full_filename)

    @property
    def storage_params(self):
        return {
            'dest_pattern': self.__dest_pattern,
            'save_meta': self.__save_meta,
        }

    # noinspection PyUnusedLocal
    @classmethod
    def init_from_config(cls, dest_pattern, save_meta, **kwargs):
        return cls(dest_pattern, save_meta)


class DataSync(object):
    resume_prefix = 'resume-'

    def __init__(self, ctx, repo, no_progressbar, resume_token=None, processes=None):
        self.__ctx = ctx
        self.__repo = repo
        self.__no_progressbar = no_progressbar
        self.__multi_process_control = None
        self.__resume_token = resume_token or self.generate_resume_token()

        data_volume_config = self.__repo.data_volume_config

        self.__processes = processes or data_volume_config.object_store_config.get('processes', -1)

        if not self.__resume_token.startswith(self.resume_prefix):
            self.__resume_token = self.resume_prefix + self.__resume_token

    def get_multi_process_control(self, use_threads=None):
        self.__init_multi_process_if_needed(use_threads)
        return self.__multi_process_control

    def __init_multi_process_if_needed(self, use_threads=None):
        if self.__multi_process_control is None:
            self.__multi_process_control = get_multi_process_control(self.__processes, use_threads=use_threads)
            self.__repo.set_multi_process_control(self.__multi_process_control)

    def close(self):
        logging.debug('%s closing', self.__class__)
        if self.__multi_process_control is not None:
            self.__multi_process_control.close()

        logging.debug('%s closed', self.__class__)

    @property
    def repo(self):
        return self.__repo

    @property
    def resume_token(self):
        return self.__resume_token

    def _upload_file_for_processing(self, file_obj, file_description, file_type=None):
        volume_id = self.__repo.data_volume_config.volume_id

        file_type = file_type or 'json'
        data_object_name = '%s/temp/%s_%s.%s' % (volume_id, file_description, uuid4().hex, file_type)

        content_typse = {
            'json': 'application/json'
        }

        default_mime_type = 'application/octet-stream'
        headers = {'Content-Type': content_typse.get(file_type, default_mime_type)}

        put_url = self._get_temp_secure_url(volume_id, data_object_name, headers)

        self._upload_file(file_obj, put_url, file_description, headers)

        return data_object_name

    def _process_index(self, object_name, isolation_token):
        index = self.__repo.open_index()

        def get_changeset():
            return index.get_changeset('gs://' + object_name, isolation_token)

        change_set = status_with_timing('Server process index', get_changeset)

        total_modify_files = 0
        total_new_files = 0

        files_to_upload = tempfile.TemporaryFile('w+')

        for name, op in change_set:
            if op == 'm':
                total_modify_files += 1
            elif op == 'i':
                total_new_files += 1
            else:
                continue

            data = name + '\n'

            files_to_upload.write(data)

        total_files_to_upload = total_modify_files + total_new_files
        files_to_upload.seek(0)

        return files_to_upload, total_files_to_upload

    def __prepare_index_file(self, index_entities_file, file_type):
        return self._upload_file_for_processing(index_entities_file, 'Index', file_type=file_type)

    def __upload_full_index(self, index_entities_file, isolation_token, file_type=None):
        object_name = self.__prepare_index_file(index_entities_file, file_type=file_type)

        index = self.__repo.open_index()

        def set_entries_operation():
            return index.set_entries_from_url('gs://' + object_name, isolation_token)

        return status_with_timing('Server process index', set_entries_operation)

    def _get_files_to_upload_from_file(self, index_entities_file_obj, isolation_token, file_type=None):
        object_name = self.__prepare_index_file(index_entities_file_obj, file_type=file_type)

        files_to_upload, total_files_to_upload = self._process_index(object_name, isolation_token)

        return files_to_upload, total_files_to_upload

    def upload_and_update_metadata(self, avro_metadata_file_obj, isolation_token=None, file_type=None):
        object_name = self._upload_file_for_processing(avro_metadata_file_obj, 'Metadata', file_type=file_type)

        def add_data():
            return self.__repo.metadata.add_data_using_url('gs://' + object_name, isolation_token)

        status_with_timing('Server process metadata', add_data)

    @classmethod
    def __append_index_file(cls, data_path, file_info):
        file_name = file_info['path']

        mtime = file_info['mtime']
        ctime = file_info.get('ctime', mtime)

        mtime = (mtime - epoch).total_seconds()
        ctime = (ctime - epoch).total_seconds()

        if file_info['sys'] == 'local':
            rel_path = os.path.relpath(file_name, data_path)

        else:  # file_info['sys'] == 's3':
            rel_path = file_name

        params = {
            'ctime': ctime,
            'mtime': mtime,
            'size': file_info['size'],
            'sha': file_info['sha'],
            'mode': 0
        }

        if 'url' in file_info:
            params['url'] = file_info['url']

        return {rel_path: params}

    def __create_combined_index_and_metadata(self, data_path):
        import humanize
        status_line = PrintStatus()

        def on_result(result):
            data_files_info, metadata_files_list = result

            total_files_size = sum(x['size'] for x in data_files_info.values())

            status_line.print_status(
                'Total files {:,} ({}) (metadata found: {:,})', len(data_files_info),
                humanize.naturalsize(total_files_size), len(metadata_files_list))

        @disk_result(self.resume_token, '__create_combined_index_and_metadata', on_result)
        def with_disk_result():
            total_files = 0
            total_files_size = 0
            total_metadata = 0

            data_files_list = set()
            metadata_files_list = set()
            data_files_info = {}

            with closing(status_line):
                for file_info in enumerate_paths_with_info(data_path):
                    rel_file_name = file_info['rel_file_name']
                    total_files_size += file_info['size']

                    if rel_file_name.endswith(MetadataFiles.metadata_ext):
                        total_metadata += 1
                        metadata_files_list.add(rel_file_name)
                    else:
                        total_files += 1
                        data_files_list.add(rel_file_name)
                        data_files_info[rel_file_name] = file_info

                    status_line.print_status(
                        'Total files {:,} ({}) (metadata found: {:,})', total_files,
                        humanize.naturalsize(total_files_size), total_metadata)

            return data_files_info, metadata_files_list

        return with_disk_result()

    def create_combined_index_and_metadata(self, data_path):
        @disk_result(self.resume_token, 'create_combined_index_and_metadata')
        def with_disk_result():
            data_files_info, metadata_files_list = self.__create_combined_index_and_metadata(data_path)

            files_metadata = MetadataFiles.load_all_metadata(
                data_path, data_files_info, metadata_files_list, self.__no_progressbar)

            return files_metadata, data_files_info

        return with_disk_result()

    @wrap_exceptions
    def upload_in_batches(self, files_info, total_files=None, callback=None, isolation_token=None):
        use_threads = None

        if not self.__repo.direct_bucket_upload:
            # in no direct bucket upload we upload to our bucket thru secure urls
            # the process of getting secure urls will lock the processes of multiprocess (I don't know why)
            # As a fallback we use the threaded upload
            use_threads = True

        multi_process_control = self.get_multi_process_control(use_threads)
        try:
            total_files = total_files or len(files_info)
            batch_size = max(min(total_files // 100, 250), 250)  # FIXME: hardcoded

            for files_info_batch in get_batch_of_files_from_paths(files_info, batch_size):
                self.__repo.stage(files_info_batch, callback=callback, isolation_token=isolation_token)

            multi_process_control.join()
        except Exception:
            logging.exception('execute failed')
            multi_process_control.terminate()
            raise

    def download_all(self, query, root_folder, dest_pattern, batch_size, processes, save_meta=True, isolation_token=None, use_threads=None):
        from tqdm import tqdm

        def create_callback(progress_bar, total_files):
            ctx = {'total_downloaded': 0}

            def handle_item(item):
                import humanize
                file_name = DestPathEnum.get_full_path(dest_pattern, item)
                rel_path = os.path.relpath(file_name, root_folder)
                phase = item.get('phase', 'all')
                phase_meta.setdefault(phase, {})[rel_path] = item

                progress_bar.update(int(item['@size']))

                ctx['total_downloaded'] += 1
                progress_bar.set_postfix_str('%s/%s' % (humanize.intcomma(ctx['total_downloaded']), humanize.intcomma(total_files)))

            return handle_item

        multi_process_control = get_multi_process_control(processes, use_threads=use_threads)
        download_iter = self.create_download_iter(query, batch_size, isolation_token=isolation_token)

        phase_meta = {}

        storage = DiskStorage(dest_pattern, save_meta)

        total_data_points_size = download_iter.total_data_points_size
        with tqdm(total=total_data_points_size, desc="Downloading", unit='B', unit_scale=True, ncols=80, disable=self.__no_progressbar) as bar:
            item_callback = create_callback(bar, download_iter.total_data_points)
            try:
                for normalized_item in download_iter.fetch_all():
                    self.__download_normalized_item(multi_process_control, storage, normalized_item, item_callback)
            except MetadataOperationError as ex:
                eprint(str(ex))
            except KeyboardInterrupt:
                multi_process_control.terminate()
            finally:
                multi_process_control.join()

            return phase_meta

    def __download_normalized_item(self, process_control, storage, normalized_item, callback=None):
        volume_id = self.__repo.data_volume_config.volume_id

        def wrap_callback_func(current_item):
            def wrapper(_):
                if callback is not None:
                    callback(current_item)

            return wrapper

        def fullname(o):
            return o.__module__ + "." + o.__class__.__name__

        config_init_dict = {'config': self.__ctx.obj.config} if process_control.using_threads else self.__ctx.obj.config.init_dict

        if process_control.using_threads:
            config_init_dict['storage'] = storage
        else:
            storage_params = storage.storage_params
            storage_params['class'] = fullname(storage)
            config_init_dict['storage'] = storage_params

        return process_control.execute(
            _download_entity,
            args=(config_init_dict, volume_id, normalized_item, self.__ctx.obj.session.headers),
            callback=wrap_callback_func(normalized_item))

    class DownloadIterResults(object):
        max_server_results = 1000  # TODO: server should return EOF oin last packet

        def __init__(self, repo, query, batch_size, silent=False, isolation_token=None):
            self.__query = query
            self.__repo = repo
            self.__query_offset = 0
            self.__total_data_points = None
            self.__total_data_points_size = None
            self.__current_iter = None
            self.__is_async = batch_size == -1
            self.__silent = silent
            self.__batch_size = batch_size
            self.__isolation_token = isolation_token

            if (self.__batch_size or 0) < 0:
                self.__batch_size = None

            if self.__query:
                tree = QueryParser().parse_query(self.__query)

                self.__limit_visitor = LimitVisitor()
                visit_query(self.__limit_visitor, tree)
            else:
                self.__limit_visitor = None

        def __get_next_results(self):
            def do_query():
                query_offset = None if not self.__query_offset else self.__query_offset
                return self.__repo.metadata.query(self.__query, is_async=self.__is_async, start_index=query_offset, isolation_token=self.__isolation_token, return_schema=True)

            if not self.__silent:
                def on_summery_data(results):
                    import humanize
                    _, query_current_total_data_points, query_total_size = results

                    return '%s, %s Rows' % (humanize.naturalsize(query_total_size), humanize.intcomma(query_current_total_data_points))

                current_results, current_total_data_points, total_size = status_with_timing('Execute Query', do_query, fp=sys.stderr, on_summery_data=on_summery_data)
            else:
                current_results, current_total_data_points, total_size = do_query()

            def iter_items():
                next_results = current_results
                has_limit = self.__limit_visitor and self.__limit_visitor.limit
                while True:
                    has_items = False
                    items_in_this_batch = 0
                    for metadata in next_results:
                        self.__query_offset += 1
                        items_in_this_batch += 1
                        has_items = True
                        yield normalize_item(metadata)

                    if self.__is_async:  # In async query we call all the results in one batch
                        break

                    if not has_items:
                        break

                    if self.max_server_results > items_in_this_batch:
                        break

                    if has_limit and self.__query_offset >= self.__limit_visitor.limit:
                        break

                    next_results, _, _ = do_query()

            return iter_items(), current_total_data_points, total_size

        @property
        def total_data_points_size(self):
            self.__prepare_iter_if_needed()

            return self.__total_data_points_size

        @property
        def total_data_points(self):
            self.__prepare_iter_if_needed()

            return self.__total_data_points

        def __prepare_iter_if_needed(self):
            if self.__current_iter is not None:
                return

            self.__current_iter, self.__total_data_points, self.__total_data_points_size = self.__get_next_results()

        def fetch_all(self):
            self.__prepare_iter_if_needed()

            for item in self.__current_iter:
                yield item

    def create_download_iter(self, query, batch_size=None, silent=False, isolation_token=None):
        return self.DownloadIterResults(self.__repo, query, batch_size, silent, isolation_token)

    def download_items(self, normalized_metadata_items, storage, multi_process_control):
        if len(normalized_metadata_items) == 0:
            return

        futures = []
        for normalized_item in normalized_metadata_items:
            async_result = self.__download_normalized_item(multi_process_control, storage, normalized_item)
            futures.append((async_result, normalized_item))

        for async_result, normalized_item in futures:
            async_result.wait()

    def save_metadata(self, root_dest, metadata):
        from tqdm import tqdm

        with tqdm(total=len(metadata), desc="saving metadata", unit=' files', ncols=80, disable=self.__no_progressbar) as bar:
            for key, val in metadata.items():
                if key is None:
                    key = 'unknown'

                json_metadata_file = os.path.join(root_dest, key + '.metadata.json')

                with open(json_metadata_file, 'w') as f:
                    json.dump(val, f)

                bar.update()

    def _create_avro_index_file_from_data(self, data_path, f, files_info):
        with closing(AvroWriter(f, key_name='name')) as avro_writer:
            for val in files_info.values():
                data = self.__append_index_file(data_path, val)
                avro_writer.append_data(data)

    @classmethod
    def _create_avro_metadata_file_from_data(cls, f, metadata_files):
        dict_normalize(metadata_files)

        with closing(AvroWriter(f)) as avro_writer:
            for rel_file_name, file_metadata in metadata_files.items():
                avro_writer.append_data({rel_file_name: file_metadata})

    def __get_files_to_upload(self, files_info, combined_avro_index_files, isolation_token):
        files_to_upload, total_files_to_upload = self._get_files_to_upload_from_file(combined_avro_index_files, isolation_token, file_type='avro')

        def enum_file_names():
            for file_name in files_to_upload:
                file_name = file_name.strip()

                yield file_name

        files_to_upload = [files_info[rel_file_name] for rel_file_name in enum_file_names()]

        return files_to_upload

    def upload_index_and_metadata(self, data_path, isolation_token=None):
        def with_disk_result():
            metadata_files, files_info = self.create_combined_index_and_metadata(data_path)

            same_files_count = 0

            if len(files_info) == 0:
                return [], same_files_count

            if len(metadata_files) > 0:
                combined_avro_meta_files = tempfile.TemporaryFile('wb+')
                self._create_avro_metadata_file_from_data(combined_avro_meta_files, metadata_files)
                self.upload_and_update_metadata(combined_avro_meta_files, isolation_token, file_type='avro')

            combined_avro_index_files = tempfile.TemporaryFile('wb+')
            self._create_avro_index_file_from_data(data_path, combined_avro_index_files, files_info)

            if self.repo.data_volume_config.embedded:
                files_to_upload = self.__get_files_to_upload(files_info, combined_avro_index_files, isolation_token)
                same_files_count = len(files_info) - len(files_to_upload)

                return files_to_upload, same_files_count

            self.__upload_full_index(combined_avro_index_files, isolation_token, file_type='avro')

            return None, 0

        return with_disk_result()

    @classmethod
    def generate_resume_token(cls):
        size = 6
        chars = string.digits
        result = ''.join(random.choice(chars) for _ in range(size))

        return result

    def _get_temp_secure_url(self, volume_id, data_object_name, headers):
        logging.debug('temp temp url for %s', data_object_name)

        url = 'data_volumes/{volume_id}/gcs_urls'.format(volume_id=volume_id)

        msg = {
            'methods': 'PUT',
            'paths': [data_object_name],
            'content_type': headers.get('Content-Type'),
            'temp': True,
        }

        result = ApiCaller.call(self.__ctx.obj, self.__ctx.obj.session, 'post', url, msg)

        put_url = result['put'][0]

        return put_url

    def _upload_file(self, file_obj, put_url, file_description, headers=None):
        from .gcs_utils import Uploader
        from tqdm import tqdm

        def update_bar(c):
            bar.update(c)

        logging.debug('uploading using %s', put_url)
        with tqdm(total=file_obj.tell(), desc="Uploading {}".format(file_description), unit='B', ncols=80,
                  disable=self.__no_progressbar, unit_scale=True) as bar:
            Uploader.upload_http(put_url, None, file_obj, headers, progress_callback=update_bar)
