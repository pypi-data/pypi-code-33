import json
from time import sleep

from reliabilly.components.logger import log_exception, Logger
from reliabilly.components.services import QueryResult, ResultTypes
from reliabilly.components.tools.secret_manager import SecretManager
from reliabilly.components.web.http_requestor import HttpRequestor
from reliabilly.settings import Settings, Constants


@log_exception
def get_sumologic_api_auth_keys(access_id_name, access_key_name, secrets_manager=SecretManager()):
    if Settings.LOCAL_SUMO_API_KEY:
        split_key = Settings.LOCAL_SUMO_API_KEY.split(Constants.COLON)
        return split_key[0], split_key[1]
    api_id = secrets_manager.get_secret(access_id_name)
    api_key = secrets_manager.get_secret(access_key_name)
    return api_id, api_key


# pylint: disable=too-few-public-methods, too-many-arguments
class SumologicQueryExecutor:

    def __init__(self, http=HttpRequestor()):
        self.http = http
        self.logger = Logger(Settings.SERVICE_NAME)
        self.headers = {Constants.CONTENT_TYPE_HEADER: Constants.CONTENT_TYPE_JSON,
                        Constants.ACCEPT_HEADER: Constants.CONTENT_TYPE_JSON}

    def execute_sumologic_query(self, query, from_time, to_time, api_id, api_key):
        try:
            payload = {Constants.QUERY: query, Constants.FROM_DATE_PARAMETER: from_time,
                       Constants.TO_DATE_PARAMETER: to_time}
            self.logger.info(f'Running sumologic query... {payload}')
            result = self.http.post(
                Constants.SUMOLOGIC_QUERY_URL, auth=self.http.get_auth_value(api_id, api_key),
                data=json.dumps(payload, default=str), headers=self.headers)
            self.logger.info(f'Result from sumologic post is... {result.text}')
            if result.status_code == Constants.RECEIVED_SUCCESS_CODE:
                return self.get_sumologic_query_results(result, api_id, api_key)
            return QueryResult(None, ResultTypes.UNKNOWN, Constants.SUMO_NO_RESULT_FOUND_MESSAGE)
        except (Exception, ValueError) as ex:  # pylint: disable=broad-except
            self.logger.error(f'Sumologic query execution failed: {ex}', exc_info=True)
            return QueryResult(None, ResultTypes.ERROR, ex)

    def get_sumologic_query_results(self, query_request_json, api_id, api_key, retry_count=5, wait_time_seconds=5):
        try:
            retries = retry_count
            result_json = query_request_json.json()
            url_get = result_json[Constants.LINK][Constants.HREF]
            self.logger.info(f'Making sumologic get request for query results. {url_get}')
            while retries >= 0:
                retries -= 1
                query_result = self.http.get(
                    url_get, auth=self.http.get_auth_value(api_id, api_key), headers=self.headers)
                if query_result.status_code == Constants.SUCCESS_RESPONSE_CODE:
                    result = query_result.json()
                    message_count = result.get(Constants.SUMOLOGIC_MESSAGE_COUNT, None)
                    if message_count:
                        return QueryResult(message_count, ResultTypes.SUCCESS)
                    return QueryResult(None, ResultTypes.UNKNOWN, Constants.SUMO_MISSING_COUNT_MESSAGE)
                sleep(wait_time_seconds)
            return QueryResult(0, ResultTypes.UNKNOWN, Constants.SUMO_RETRY_EXCEEDED_MESSAGE)
        except (Exception, ValueError) as ex:  # pylint: disable=broad-except
            self.logger.error(f'Error getting sumologic query results. {ex}')
            return QueryResult(None, ResultTypes.ERROR, ex)
