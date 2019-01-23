from elasticsearch_dsl.connections import connections
from elasticsearch.helpers import bulk
from .config import config
from .log import log_exception, raise_exception, log_info
from elasticsearch import NotFoundError


def create_connection(label='es'):
    try:
        host = config(label,'host')
        return connections.create_connection(alias=label,hosts=[host])
    except Exception as e:
        log_exception(e)


__es_clients = {}


def get_es_client(label='es'):
    global __es_clients
    if label not in __es_clients:
        __es_clients[label] = create_connection(label)
    return __es_clients[label]


class BaseSearcher(object):

    def __init__(self, label, doc_model=None):
        self.conn = get_es_client(label)
        self.doc_model = doc_model

    def search_by_id(self, id):
        if self.doc_model is None:
            raise Exception('no doc model found')
        try:
            return self.doc_model.get(id)
        except NotFoundError as ex:
            return None
        except Exception as e:
            return e


class BaseIndexer(object):

    def __init__(self, label, doc_model):
        self.conn = get_es_client(label)
        self.doc_model = doc_model
        self.bulk_list = []
        self.bulk_num = None
        self.old_index = None
        self.new_index = None
        self.index_name = self.doc_model._index._name  # hard trick

    def init_rebuild_index(self, bulk_num=100):
        self.bulk_num = bulk_num
        self.old_index = self._get_exist_index()
        self.new_index = self._get_new_index_name(self.index_name, self.old_index)
        self.doc_model.init(index=self.new_index)
        log_info(
            'init_rebuild_index new_index=' + self.new_index + ' for ' + self.index_name + ' old_index=' + self.old_index)

    def add_bulk_data(self, id, data):
        self._filter_data(id, data)
        self.bulk_list.append(data)
        self.flush_bulk(False)

    def _filter_data(self, id, data):
        data['_index'] = self.new_index
        if '_type' not in data:
            data['_type'] = 'doc'
        data['_id'] = id
        return data

    def save_data(self, id, data):
        self._filter_data(id, data)
        bulk(self.conn, [data], index=self.index_name, doc_type=self.doc_model)

    def flush_bulk(self, must=False):
        if len(self.bulk_list) == 0:
            return
        if len(self.bulk_list) >= self.bulk_num or must:
            bulk(self.conn, self.bulk_list, index=self.new_index, doc_type=self.doc_model)
            self.bulk_list = []

    def done_rebuild_index(self):
        self.flush_bulk(True)
        self._update_alias()
        log_info('done_rebuild_index for ' + self.index_name)

    def _get_new_index_name(self, index_name, old_index):
        if old_index == '' or index_name == old_index:
            return index_name + '_v0'
        pos = old_index.rfind('_v')
        if pos < 0 or pos >= len(old_index) - 2:
            raise_exception('bad old_index name ' + old_index)
            return
        version = int(old_index[pos + 2:len(old_index)]) + 1
        if version > 9:
            version = 0
        return index_name + '_v' + str(version)

    def _update_alias(self):
        if self.old_index == '':
            log_info('no old_index need to update')
            return
        self.conn.indices.put_alias(index=self.new_index, name=self.index_name)
        log_info('put_alias ' + self.new_index + ' for ' + self.index_name)
        self.conn.indices.delete_alias(index=self.old_index, name=self.index_name, ignore=[400, 404])
        log_info('delete_alias ' + self.old_index + ' for ' + self.index_name)

    def _get_exist_index(self):
        indices = self.conn.indices.get('*')
        match_index = ''
        for index in indices:
            if index.find(self.index_name) == 0:
                if match_index != '':
                    raise_exception('multiple index name for ' + self.index_name)
                match_index = index
        return match_index
