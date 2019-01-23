from urllib.parse import quote
from reliabilly.components.logger import Logger, log_exception
from reliabilly.components.web.http_requestor import HttpRequestor
from reliabilly.components.services import Constants, ResultTypes, QueryResult
from reliabilly.settings import Settings
from reliabilly.components.tools.secret_manager import SecretManager


@log_exception
def get_newrelic_account_id(account_name):
    return Constants.NEWRELIC_ACCOUNT_IDS.get(account_name, None)


@log_exception
def get_newrelic_api_key(account_name, secrets_manager):
    api_key = None
    api_secrets_name = Constants.NEWRELIC_API_KEYS.get(account_name, None)
    if Settings.LOCAL_NR_API_KEY:
        return Settings.LOCAL_NR_API_KEY
    if api_secrets_name:
        api_key = secrets_manager.get_secret(api_secrets_name)
    return api_key


class NewRelicQueryExecutor:

    def __init__(self, account_name, http=HttpRequestor(), secrets_manager=SecretManager()):
        self.http = http
        self.secrets_manager = secrets_manager
        self.account_name = account_name
        self.account_id = get_newrelic_account_id(self.account_name)
        self.api_key = get_newrelic_api_key(self.account_name, self.secrets_manager)
        self.logger = Logger(Settings.SERVICE_NAME)

    def execute_faceted_query(self, query):
        result = self._execute_query(query)
        result_json = result.json()
        if not result.ok:
            return self._get_failure_result(result_json)
        return QueryResult(result_json, ResultTypes.SUCCESS)

    def execute_single_value_query(self, query):
        try:
            result = self._execute_query(query)
            result_json = result.json()
            if not result.ok:
                return self._get_failure_result(result_json)
            results = result_json.get(Constants.RESULTS, None)
            if results:
                first_result = results[0]
                if first_result:
                    filtered_result = next(iter(first_result.values()))
                    return QueryResult(filtered_result, ResultTypes.SUCCESS)
                return QueryResult(None, ResultTypes.UNKNOWN, Constants.NR_EMPTY_RESULTS_MESSAGE)
            return QueryResult(None, ResultTypes.UNKNOWN, Constants.NR_NO_RESULT_ITEM_MESSAGE)
        except (Exception, ValueError) as ex:  # pylint: disable=broad-except
            self.logger.error(f'Newrelic query execution for {query} failed: {ex}')
            return QueryResult(None, ResultTypes.ERROR, ex)

    def _get_failure_result(self, result_json):
        self.logger.info(f'Newrelic result: {result_json}')
        return QueryResult(None, ResultTypes.ERROR, result_json)

    def build_url(self, account_id, query):
        try:
            url = Settings.NEWRELIC_QUERY_URL
            encoded_query = quote(query)
            return url.format(account_id=account_id, query=encoded_query)
        except TypeError as ex:
            self.logger.error(f'Encoding query failed due to non-string parameter: {ex}')
            return None

    def _execute_query(self, query):
        self.logger.info(f'Executing newrelic query: {query}')
        headers = {Constants.X_QUERY_KEY_HEADER: self.api_key}
        url = self.build_url(self.account_id, query)
        return self.http.get(url, headers=headers)
