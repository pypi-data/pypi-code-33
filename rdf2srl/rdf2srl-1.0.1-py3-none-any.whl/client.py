import sys
import io

from SPARQLWrapper import SPARQLWrapper, CSV
import pandas as pd

__author__ = "Aisha Mohamed <ahmohamed@qf.org.qa>"

_MAX_ROWS = 1000000 # maximum number of rows returned in the result set
_TIMEOUT = 900 # in seconds

class Client(object):
    """
    class for sparql client that handles communication with a sparql end-point
    over http using the sparql wrapper library.
    """
    def __init__(self, endpoint):
        """
        Constructs an instance of the client class
        :param endpoint: string of the SPARQL endpoint's URI hostname:port
        :type endpoint: string
        """
        self.endpoint = endpoint

    def is_alive(self, endpoint=None):
        """
        :param endpoint string of the SPARQL endpoint's URI
        :type endpoint string
        :return if endpoint is not None return Ture if endpoint is alive else
            return False. if endpoint is None return True if self.endpoint is
            alive and False otherwise.
        """
        pass

    def get_endpoint(self):
        """
        :return a string of the endpont URI
        """
        return self.endpoint

    def set_endpoint(self, endpoint):
        """
        updates self.endpoint with the new endpoint
        :param endpoint: endpoint uri
        """
        self.endpoint = endpoint

    def execute_query(self, query, limit=_MAX_ROWS):
        """
        Connects to the sparql endpoint, sends the query and returns a dataframe containing the result of a sparql query
        :param query: a valid sparql query string
        :type query: string
        :param output_file: the path to the output file
        :type output_file: string
        :return: a pandas dataframe representing the result of the query
        """
        client = SPARQLWrapper(self.endpoint)
        client.setTimeout(_TIMEOUT)
        offset = 0
        results_string = "" # where all the results are concatenated
        continue_straming = True
        while continue_straming:
            if limit > 1:
                query_string = query+" OFFSET {} LIMIT {}".format(str(offset), str(limit))
            else:
                query_string = query
            client.setQuery(query_string)
            try:
                client.setReturnFormat(CSV)
                header = client.query().convert().split("\n",1)[0]
                results = client.query().convert().split("\n",1)[1] # string
                # if the number of rows is less then the maximum number of rows
                if results.count('\n') < _MAX_ROWS:
                    continue_straming = False
                offset = offset + limit
            except Exception as e:
                print(e)
                sys.exit()
            results_string += results.decode("utf-8")
        # convert it to a dataframe
        results_string = header + "\n" + results_string
        f = io.StringIO(results_string)
        f.seek(0)
        df = pd.read_csv(f, sep=',') # to get the values and the header
        return df