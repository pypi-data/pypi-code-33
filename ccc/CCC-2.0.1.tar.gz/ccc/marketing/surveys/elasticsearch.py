from ccc.elasticsearch.elasticsearch import ElasticSearch


class SurveyElasticSearch(ElasticSearch):
    index_name = 'crm_survey'
    doc_type = 'crm_survey_data'
