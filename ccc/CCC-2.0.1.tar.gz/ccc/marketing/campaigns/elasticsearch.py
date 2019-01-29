from ccc.elasticsearch.elasticsearch import ElasticSearch


class CampaignElasticSearch(ElasticSearch):
    index_name = 'crm_campaign'
    doc_type = 'crm_campaign_data'

    def top_search(self, text):
        if text:
            template = {
                "query": {
                    "query_string": {
                        "query": text+'*'
                    }
                }
            }
        else:
            template = {
                "query": {
                    "match_all": {}
                }
            }
        return self.search(template)['hits']['hits']
