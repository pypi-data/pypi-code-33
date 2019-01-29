from ccc.elasticsearch.elasticsearch import ElasticSearch


class ContactElasticSearch(ElasticSearch):
    index_name = 'crm_contact'
    doc_type = 'crm_contact_data'
