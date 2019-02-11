from directory_api_client.base import CachedAbstractAPIClient
from directory_api_client.version import __version__


class ExportOpportunityAPIClient(CachedAbstractAPIClient):

    endpoints = {
        'create-opportunity-food': '/export-opportunity/food/',
        'create-opportunity-legal': '/export-opportunity/legal/',

    }
    version = __version__

    def create_opportunity_food(self, form_data):
        return self.post(
            self.endpoints['create-opportunity-food'],
            data=form_data
        )

    def create_opportunity_legal(self, form_data):
        return self.post(
            self.endpoints['create-opportunity-legal'],
            data=form_data
        )
