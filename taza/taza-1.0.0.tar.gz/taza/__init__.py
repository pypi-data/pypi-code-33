import logging
from taza.tacyt.TacytApp import TacytApp
from taza.worker import TacytAppThreadPool

class APILimitReached(Exception):
    pass


class TazaClient:
    """
    Handles the connection between the applicationa and the TacytApp class.
    It's mostly an utility class that implements common actions.

    If you come up with a query that more people could use, put it here.

    Instances of this class should be created with the factory methods.
    """
    
    def __init__(self, wrapped_api, max_results_per_page=100, grouped_results=False):
        self.api = wrapped_api
        self.max_results_per_page = max_results_per_page
        self.grouped_results = grouped_results
        self.__logger = logging.getLogger('TazaClient[%d]' % id(self))

    instances = {}
        

    @staticmethod
    def from_credentials(app_id, secret_key, max_results_per_page=100, grouped_results=False, pool=False, pool_size=4):
        """
        Factory method for creating instances of TazaClient class using the Tacyt credentials.

        :param app_id: APP_ID credential for Tacyt.
        :param secret_key: SECRET_KEY credential for Tacyt.
        :param max_results_per_page: The number of results per page that is requested to Tacyt.
        :param grouped_results: Whenever Tacyt should group the results.
        :param pool: Whenever the client should leverage the work to threads in a pool or run the requests in the current thread.
        """
        #instance_hash = app_id, secret_key, max_results_per_page, grouped_results, pool, pool_size

        #if instance_hash in TazaClient.instances:
        #    return TazaClient.instances[instance_hash]
        
        api = TacytApp(app_id, secret_key)
        if pool:
            api = TacytAppThreadPool(api, pool_size)
        new_instance = TazaClient(api, max_results_per_page, grouped_results)
        #TazaClient.instances[instance_hash] = new_instance
        return new_instance

    def search_apps_with_query(self, query, fields=None):
        """
        Will invoke the search_apps method from TacytApp automatically handling the pagination.
        Returns a generator.
        """
        def send_query(page):
            self.__logger.debug("Sending query \"%s\" at page %d", str(query), page)
            result = self.api.search_apps(str(query),
                                          maxResults=self.max_results_per_page,
                                          numberPage=page,
                                          outfields=fields,
                                          grouped=self.grouped_results)
            err = result.get_error()
            if err:
                self.__logger.warning("Error in result from Tacyt: {}".format(err))
                if err.code == 112:
                    raise APILimitReached()
            result = result.get_data()['result']
            nResults = result['numResults']
            return nResults, result['applications'], nResults > (self.max_results_per_page * page)
        
        if not fields:
            fields = []
        has_tail = True
        page = 1
        while has_tail:
            nResults, apps, has_tail = send_query(page)
            for app in apps:
                yield app
            page += 1

