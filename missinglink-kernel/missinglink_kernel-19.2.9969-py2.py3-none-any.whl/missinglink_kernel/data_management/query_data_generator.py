# -*- coding: utf8 -*-
import logging
from collections import OrderedDict
import six
from missinglink_kernel.data_management.http_session import create_http_session
from missinglink.core.context import build_context
from missinglink.legit.data_sync import DataSync
from missinglink.legit.data_volume import with_repo_dynamic
from .iterator import Iterator
import numpy as np
import os

logger = logging.getLogger('missinglink')


class QueryDataGeneratorFactory(object):
    def __init__(self, multi_process_control, storage, data_callback, volume_id, batch_size, shuffle, seed):
        self.data_callback = data_callback
        self.volume_id = volume_id
        self.storage = storage
        self.multi_process_control = multi_process_control
        self.batch_size = batch_size
        self.shuffle = shuffle
        self.seed = seed

    @property
    def cache_folder(self):
        return self.storage.storage_params.get('cache_directory')

    def create(self, query, ctx=None):
        return QueryDataGenerator(self, query, ctx=ctx)


class MetadataIndex(object):
    def __init__(self, ctx, volume_id, query, cache_folder):
        self._full_index = None
        self._downloaded_items_index = -1
        self.is_grouped = None
        self.download_all(ctx, volume_id, query, cache_folder)

    @property
    def total_items(self):
        return len(self._full_index or [])

    def __get_item(self, index):
        if index > self._downloaded_items_index:
            raise ValueError()

        return self._full_index[index]

    def get_items_flat(self, indexes):
        for i in indexes:
            items = self.__get_item(i)

            if self.is_grouped:
                for item in items:
                    yield item, i

                continue

            yield items, i

    @classmethod
    def _add_results_using_datapoint(cls, group_key):
        def add_results(data_iter):
            full_index = OrderedDict()

            for normalized_item in data_iter.fetch_all():
                group_value = normalized_item.get(group_key)

                if group_value is None:
                    continue

                full_index.setdefault(group_value, []).append(normalized_item)

            return list(full_index.values())

        return add_results

    def _add_results_individual_results(self, data_iter):
        full_index = [None] * data_iter.total_data_points

        downloaded_items_index = 0

        for normalized_item in data_iter.fetch_all():
            full_index[downloaded_items_index] = normalized_item
            downloaded_items_index += 1

        if full_index and len(full_index) > downloaded_items_index + 1:
            full_index = self._full_index[:downloaded_items_index + 1]

        return full_index

    @classmethod
    def _get_datapoint_by_key_if_present(cls, query):
        from missinglink.legit.scam import QueryParser, visit_query
        from .query_visitors import DatapointVisitor

        tree = QueryParser().parse_query(query)

        group_visitor = visit_query(DatapointVisitor(), tree)

        return group_visitor.datapoint

    @classmethod
    def _get_repo(cls, ctx, volume_id, **kwargs):
        return with_repo_dynamic(ctx, volume_id, **kwargs)

    def download_all(self, ctx, volume_id, query, cache_folder):
        logger.debug('download metadata items started')

        datapoint_key = self._get_datapoint_by_key_if_present(query)
        self.is_grouped = datapoint_key is not None
        add_results = self._add_results_using_datapoint(datapoint_key) if self.is_grouped else self._add_results_individual_results

        with self._get_repo(ctx, volume_id, cache_folder=cache_folder) as repo:
            data_sync = DataSync(ctx, repo, no_progressbar=True)

            # batch_size==-1 means async and all results
            data_iter = data_sync.create_download_iter(query, batch_size=-1, silent=True)

            self._full_index = add_results(data_iter)
            self._downloaded_items_index = len(self._full_index)

        logger.debug('download metadata items finished')


class QueryDataGenerator(Iterator):
    def __init__(self, creator, query, ctx=None):
        self._query = query
        self._creator = creator
        self._ctx = ctx or self.build_context()
        self._metadata_index = self._create_metadata_index(creator.volume_id, query, creator.cache_folder)
        super(QueryDataGenerator, self).__init__(self._metadata_index.total_items, creator.batch_size, creator.shuffle, creator.seed)

    @property
    def ctx(self):
        return self._ctx

    def _create_metadata_index(self, volume_id, query, cache_folder):
        return MetadataIndex(self._ctx, volume_id, query, cache_folder)

    def _get_batches_of_transformed_samples(self, index_array):
        results = self._download_data(index_array)

        batch_data = None

        def create_batch_array(obj):
            if isinstance(obj, six.integer_types + (float, )):
                return np.zeros(len(index_array), dtype=type(obj))

            return np.zeros((len(index_array),) + obj.shape, dtype=obj.dtype)

        i = 0
        for file_name, metadata in results:
            vals = self._creator.data_callback(file_name, metadata)

            if vals is None or vals[0] is None:
                continue

            if batch_data is None:
                batch_data = [create_batch_array(vals[j]) for j in range(len(vals))]

            for j in range(len(vals)):
                batch_data[j][i] = vals[j]

            i += 1

        return None if batch_data is None else tuple(batch_data)

    def next(self):
        with self.lock:
            index_array = next(self.index_generator)

        return self._get_batches_of_transformed_samples(index_array)

    @classmethod
    def build_context(cls, config_prefix=None):
        config_prefix = os.environ.get('ML_CONFIG_PREFIX', config_prefix)
        config_file = os.environ.get('ML_CONFIG_FILE')
        session = create_http_session()

        ctx = build_context(session, config_prefix=config_prefix, config_file=config_file)

        return ctx

    @classmethod
    def _get_repo(cls, ctx, volume_id):
        return with_repo_dynamic(ctx, volume_id)

    @classmethod
    def _group_by_index(cls, data, indices):
        results_grouped = []
        prev_index = None
        for i, d in enumerate(data):
            index = indices[i]
            if prev_index != index:
                results_grouped.append(([], []))
                prev_index = index

            filename, = d[0]
            metadata, = d[1]
            results_grouped[-1][0].append(filename)
            results_grouped[-1][1].append(metadata)

        return results_grouped

    def _download_data(self, index_array):
        with self._get_repo(self._ctx, self._creator.volume_id) as repo:
            data_sync = DataSync(self._ctx, repo, no_progressbar=True)

            results = []

            download_items_with_index = self._metadata_index.get_items_flat(index_array)
            normalized_download_items, indices = zip(*list(download_items_with_index))

            storage = self._creator.storage
            data_sync.download_items(normalized_download_items, storage, self._creator.multi_process_control)
            for normalized_item in normalized_download_items:
                full_path = storage.filename(normalized_item)
                results.append(((full_path, ), (normalized_item, )))

            if self._metadata_index.is_grouped:
                return self._group_by_index(results, indices)

            return results
