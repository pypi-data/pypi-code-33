from django.conf import settings

from elasticsearch import Elasticsearch


class ElasticSearch(object):
    """Elastic Search"""

    index_name = 'test'

    def __init__(self):
        self.elasticsearch = Elasticsearch(settings.ELASTICSEARCH_SERVICE_URL, send_get_body_as='POST')
        try:
            if not self.elasticsearch.indices.exists(self.index_name):
                # Ignore 400 means to ignore "Index Already Exist" error.
                self.elasticsearch.indices.create(index=self.index_name, ignore=400, body=settings)
                print('Created Index')
        except Exception as ex:
            print(str(ex))

    def store_record(self, id=None, data=None):
        try:
            return self.elasticsearch.index(index=self.index_name, doc_type=self.doc_type, id=id, body=data)
        except Exception as ex:
            print('Error in indexing data')
            print(str(ex))

    def delete_record(self, doc_id):
        """delete record"""
        try:
            return self.elasticsearch.delete(index=self.index_name, doc_type=self.doc_type, id=doc_id)
        except Exception as ex:
            print('Error in indexing data')
            print(str(ex))

    def update_by_query(self, body=None, params=None):
        """Update by query"""
        return self.elasticsearch.update_by_query(self.index_name, doc_type=self.doc_type, body=body, params=params)

    def search_by_id(self, id):
        """search search record by ID"""
        return self.elasticsearch.get(index=self.index_name, doc_type=self.doc_type, id=id)

    def search(self, search):
        """search record"""
        return self.elasticsearch.search(index=self.index_name, doc_type=self.doc_type, body=search)
