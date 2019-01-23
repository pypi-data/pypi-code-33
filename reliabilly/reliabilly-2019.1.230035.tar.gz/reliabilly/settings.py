# pylint: disable=too-few-public-methods
import json
from os import environ, listdir, path


class Constants:
    SPACE = ' '
    NEWLINE = '\n'
    DUMMY = 'dummy'
    WRITE_FLAG = 'w+'
    SERVICE_KEY = 'service'
    SERVICE_REPLACE = '{{service}}'
    TEMPLATE_DIR = 'templates'
    IGNORED_FILES = ['.DS_Store']
    CAMELCASE_FILTER = 'camelcase'
    OPEN = 'open'
    MKDIRS = 'mkdirs'
    HEALTH = 'health'
    HEALTH_UNKNOWN_MESSAGE = 'health unknown'
    UNKNOWN_HEALTH_RESPONSE = {HEALTH: HEALTH_UNKNOWN_MESSAGE}
    MONGO_STATS_COMMAND = 'dbstats'
    MONGO_CONNECTION_HEALTH_ERROR = 'unable to connect to mongodb at {host}:{port}'
    MONGO_HEALTH_ID = 'mongo'
    DYNAMO_HEALTH_ID = 'dynamo'
    COMPOSE_FILE_FLAG_SEPARATOR = ' -f '
    COMPOSE_FILE_NAME = 'docker-compose.yml'
    MONITORING_POLICY_URL = 'https://api.newrelic.com/v2/alerts_synthetics_conditions/policies'
    SERVICE_NAME_ENV = 'SERVICE_NAME'
    MONGO_PORT_ENV = 'MONGO_PORT'
    MONGO_URL_ENV = 'MONGO_URL'
    MONGO_URL_DEFAULT = 'mongodb://mongodb'
    RUN_SKIPPED_ENV = 'RUN_SKIPPED'
    RUN_SKIPPED_MSG = 'skipping due to skip not being set'
    VERSION_KEY = 'version'
    APP_PORT_ENV = 'APP_PORT'
    PORT_ENV_SUFFIX = '_PORT'
    PYTHON_MODULE_FILE = '__init__.py'
    INTEGRATION_WILDCARD = '*.yml'
    DOCKER_FILE = 'Dockerfile'
    CURRENT_DIR = '.'
    TESTS_DIR = 'tests'
    SERVICE_DIR = 'services'
    INTEGRATION_TEST_DIR = 'integration'
    DEFAULT_TARGET = 'http://localhost:8080'
    PRODUCTION_URL_BASE = 'https://reliabilly.com'
    BACKUPS_BUCKET = 's3://reliabilly-backups'
    DUMMY_NUM = 420
    DEFAULT_MONGO_PORT = 27017
    DV_URL_ENV = 'DV_URL'
    DV_URL_DEFAULT = 'https://dvt.reliabilly.com/v1/'
    DEFAULT_APP_PORT = 8080
    STARTING_PORT = 5000
    PORT_INCREMENT = 1
    STARTING_PRIORITY = 100
    DEFAULT_VERSION_TIMEOUT = 120
    MONITORING_URL = 'https://synthetics.newrelic.com/synthetics/api/v3/monitors'
    AUTH_TOKEN = 'AUTH_TOKEN'
    ENVIRONMENT = 'ENVIRONMENT'
    LOCAL_URL_BASE = 'http://localhost:8080/'
    LOCAL_SERVICE_URL_BASE = 'http://{0}:8000/'
    LOCAL_STATIC_URL_BASE = 'http://{0}:80/'
    PROD_URL_BASE = 'https://reliabilly.com/'
    UAT_URL_BASE = 'https://reliabilly-uat.com/'
    ACCEPT_HEADER = 'Accept'
    ACCOUNT_NAME = 'account_name'
    ALL_KEY = 'All'
    AMPERSAND = '&'
    AUTHORIZATION_HEADER = 'Authorization'
    AWS_ACCOUNT = 'AWS_ACCOUNT'
    AWS_REGION = 'AWS_REGION'
    BAD_REQUEST_CODE = 400
    BAD_REQUEST_MESSAGE = json.dumps({'message': 'Invalid request'})
    BEARER_PREFIX = 'Bearer '
    BRANCH_NAME_ENV = 'BRANCH_NAME'
    BUILD_NUMBER_ENV = 'BUILD_NUMBER'
    BUILD_URL_ENV = 'RUN_DISPLAY_URL'
    CALENDAR_ROUTE = 'calendar/'
    CHANNEL_NAME = 'channel_name'
    CIRCUIT_BREAKER = 'circuit_breaker'
    CLIENT = 'client'
    CODE = 'Code'
    COLLECTION_ENABLED = 'COLLECTION_ENABLED'
    COLLECTION_FAILED_MESSAGE = json.dumps({'message': 'Collection Failed!'})
    COLLECTION_FAILED_STATUS = 'Collection failed!'
    COLLECTION_INTERVAL_DEFAULT = 900
    COLLECTION_INTERVAL_SECONDS_KEY = 'COLLECTION_INTERVAL_SECONDS'
    COLLECTION_RECEIVED_MESSAGE = json.dumps({'message': 'Collection received!'})
    COLLECTION_ROUTE = 'collect/'
    COLLECTION_STARTED_STATUS = 'Collection started.'
    COLLECTION_STATUS_KEY = 'status'
    COLLECTION_SUCCESS_MESSAGE = json.dumps({'message': 'Collection Successful!'})
    COLLECTION_SUCCESS_STATUS = 'Collection successful!'
    COLLECTION_WITH_ERRORS_STATUS = 'Collection succeeded with {} errors.'
    COLLECTION_WITH_ERRORS_MESSAGE = json.dumps({'message': 'Collection succeeded with errors.'})
    COLLECTION_MANAGER_TABLE = 'collection_manager'
    COLON = ':'
    COMMA = ','
    COMPLETED = 'completed'
    COMPONENT = 'component'
    CONTENT_TYPE_HEADER = 'Content-Type'
    CONTENT_TYPE_JSON = 'application/json'
    CREATED_SUCCESS_CODE = 201
    MONITOR_ACCOUNT_ID = '12345678'
    DATA_MONITORING_URL_DEFAULT = f'https://insights-collector.newrelic.com/v1/accounts/{MONITOR_ACCOUNT_ID}/events'
    DATA_MONITORING_URL_ENV = 'DATA_MONITORING_URL'
    DATE_FORMAT_KEY = '%d/%m/%y'
    DB_ID_KEY = '_id'
    DEBUG_ROUTE = 'debug/'
    DEFAULT_AWS_ACCOUNT = 'default_aws'
    DEFAULT_DB_NAME = "service_db"
    SUMO_KEY = 'abcd'
    DEFAULT_LOG_URL = f'https://endpoint1.collection.us2.sumologic.com/receiver/v1/http/{SUMO_KEY}'
    DEFAULT_PAGE_OFFSET = 0
    DEFAULT_PAGE_SIZE = 25
    DEFAULT_QUEUE_URL = 'localhost'
    DEFAULT_DYNAMO_THROUGHPUT = {'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5, }
    DELAY_SECONDS_KEY = 'DelaySeconds'
    DELETE_REQUEST = 'DELETE'
    DELETE_REQUEST_MESSAGE = json.dumps({'message': 'Delete Successful!'})
    DEV = 'dev'
    DEV_TOKEN = 'reliabilly.developer_keys'
    DIRECT_FEED = 'direct_feed'
    DEFAULT_AWS_CONNECT_TIMEOUT = 1
    DEFAULT_AWS_MAX_RETRY_COUNT = 0
    AWS_MAX_RETRY_ATTEMPTS = 'max_attempts'
    DYNAMO_RESOURCE_KEY = 'dynamodb'
    DYNAMO_RESPONSE_METADATA = 'ResponseMetadata'
    DYNAMO_SUCCESS_STATUS = 'HTTPStatusCode'
    DYNAMO_ITEMS_KEY = 'Items'
    DYNAMO_ITEM_KEY = 'Item'
    DYNAMO_COUNT_KEY = 'Count'
    DYNAMO_PORT_ENV = 'DYNAMO_PORT'
    DYNAMO_PORT_DEFAULT = 8888
    DYNAMO_URL_ENV = 'DYNAMO_URL'
    DYNAMO_URL_DEFAULT = 'http://localhost'
    DYNAMO_TAGS = [{'Key': 'owner', 'Value': 'jblouse@corpseware.com'},
                   {'Key': 'product', 'Value': 'reliabilly'}]
    EMPTY = ''
    ENDPOINT_URL = 'endpoint_url'
    EQUAL = '='
    ERROR = 'Error'
    ERROR_RATE = 'error_rate'
    FORWARD_SLASH = '/'
    FROM = 'from'
    FROM_DATE_PARAMETER = 'from'
    GET_REQUEST = 'GET'
    GITHUB_ORG = 'corpseware'
    GITHUB_REPO = 'reliabilly'
    HOST = 'host'
    HREF = 'href'
    HYPHEN = '-'
    HEALTHCHECK_ENDPOINT = 'ping'
    ID = 'id'  # pylint: disable=invalid-name
    IGNORE_PRODUCT_LIST = ['api', 'mobile']
    JENKINS = 'Jenkins'
    KMS_KEYS = {'us-west-2': 'arn:aws:kms:us-west-2:{AWS_ACCOUNT}:key/{KMS_GUID}',
                'us-east-1': 'arn:aws:kms:us-east-1:{AWS_ACCOUNT}:key/{KMS_GUID}'}
    LEVEL = 'level'
    LINK = 'link'
    LOCAL = 'local'
    LOCAL_API_NR_ENV = 'LOCAL_NR_API'
    LOCAL_API_SUMO_ENV = 'LOCAL_SUMO_API'
    MAX_PAGE_SIZE = 1000
    MESSAGE_ID_KEY = 'MessageId'
    MESSAGE = 'message'
    MESSAGE_RETENTION_PERIOD_SEC = '86400'
    MESSAGE_RETENTION_PERIOD_KEY = 'MessageRetentionPeriod'
    MESSAGES_KEY = 'Messages'
    MONGO_DB_NAME_ENV = 'MONGO_DB_NAME'
    MONGO_PORT_DEFAULT = 27017
    MONITOR_CALLS_SUFFIX = '_calls'
    MONITOR_ELAPSED_SUFFIX = '_elapsed'
    MONITOR_ERROR_KEY = '_err'
    MONITOR_LARGE_KEY = '_large'
    MONITOR_PREFIX = 'reliabilly.'
    MONITOR_INCR_DEFAULT = 1
    NAME = 'name'
    NEWRELIC = 'newrelic'
    NO_COLLECTION_FOUND_MESSAGE = json.dumps({'message': 'Collection not running!'})
    NONE = 'none'
    NOTIFY_CHANNEL_NAME_ENV = 'NOTIFY_CHANNEL_NAME'
    NOTIFY_MESSAGE = 'The build is broken on PR branch: {branch} at Stage: {stage} \n\nResult Output: {result}'
    OKTA_ACTIVE_STATUS = 'ACTIVE'
    OKTA_SESSION_URL = 'https://okta.com/sessions/{session_token}'
    OPTIONS_REQUEST = 'OPTIONS'
    PAGE_OFFSET = 'offset'
    PAGE_SIZE = 'limit'
    PORT = 'port'
    POST_REQUEST = 'POST'
    PROD = 'prod'
    PROD_BRANCH_NAME = 'master'
    PROD_REGION = 'us-east-1'
    PRODUCT = 'product'
    PRODUCTS = 'products'
    PROXY_URL_DEFAULT = 'http://proxy.com:8080'
    PROXY_URL_ENV = 'PROXY_URL'
    PURGE_REQUEST_MESSAGE = json.dumps({'message': 'Purge Successful!'})
    PUT_REQUEST = 'PUT'
    PYTHON_PACKAGE_REPO = 'https://af.com/artifactory/api/pypi/pypi'
    QUEUE_NAME = 'queue_name'
    LOGGER = 'logger'
    QUERY = 'query'
    QUERY_BUILDER_ROUTE = 'build_query/'
    QUERY_EXECUTOR = 'query_executor'
    QUESTION = '?'
    QUEUE_DELAY_SECONDS = '60'
    QUEUE_PORT = 6379
    QUEUE_RETENTION_PERIOD = '86400'
    QUEUE_URL_ENV = 'QUEUE_URL'
    QUEUE_URL_KEY = 'QueueUrl'
    QUEUE_URLS_KEY = 'QueueUrls'
    RB_FLAG = 'rb'
    READ_ONLY = 'r'
    RECEIVED_SUCCESS_CODE = 202
    RECEIPT_HANDLE_KEY = 'ReceiptHandle'
    RELEASE_SPREADSHEET_URL = 'RELEASE_SPREADSHEET_URL'
    RELEASE_SPREADSHEET_URL_DEFAULT = 'https://docs.google.com/forms/d/e/{FORM_ID}/formResponse'
    REMOTE_LOG_URL_ENV = 'REMOTE_LOG_URL'
    RESOURCE = 'resource'
    RESOURCE_NOT_FOUND_CODE = 404
    RESOURCE_NOT_FOUND_MESSAGE = json.dumps({'message': 'Resource not found'})
    RESOURCE_IN_USE_EXCEPTION = 'ResourceInUseException'
    RESTORE_ROUTE = 'restore/'
    RESULT = 'result'
    RESULTS = 'results'
    RESULTS_ROUTE = 'results/'
    RESULTS_EMPTY_MESSAGE = json.dumps({'message': 'No results found.'})
    ROOT_SERVICE = 'app'
    RUN_ROUTE = 'run/'
    SECURITY = 'security'
    SERVICE = 'service'
    SESSION_URL_ENV = 'SESSION_URL'
    SINGLE_QUOTE = "'"
    SHARED_AUTH_TOKEN = 'shared_auth'
    SLACK_ADD_REACTION_TYPE = 'reactions.add'
    SLACK_API_OK_KEY = 'ok'
    SLACK_API_TOKEN_ID = 'RELIABILLY_SLACK_TOKEN'
    SLACK_EMAIL_KEY = 'email'
    SLACK_EPHEMERAL_MESSAGE_TYPE = 'chat.postEphemeral'
    SLACK_ID_KEY = 'id'
    SLACK_OPENED_PR_TITLE = '{0} has passed linting and testing.'
    SLACK_OPENED_PR_MSG = 'A newly opened PR has just passed Jenkins automated checks. ' \
                          'It\'s now ready to be reviewed by a member of the team.'
    SLACK_MEMBERS_KEY = 'members'
    SLACK_POST_MESSAGE_TYPE = 'chat.postMessage'
    SLACK_PROFILE_KEY = 'profile'
    SLACK_UPDATE_MESSAGE_TYPE = 'chat.update'
    SLACK_USERS_LIST_TYPE = 'users.list'
    SLACK_ALERT_TEAM = 'ALERT_TEAM'
    SLACK_ALERT_USER = 'ALERT_USER'
    SLO = 'slo'
    SLOS = 'slos'
    SOURCE_CONTROL_URL_DEFAULT = "https://github.com/api/v3"
    SOURCE_CONTROL_URL_ENV = "SOURCE_CONTROL_URL"
    SQS_CLIENT = 'sqs'
    RESOURCE_TAGS = {'owner': 'jblosue@corpseware.com', 'product': 'reliabilly'}
    STAGE_ENV = 'STAGE_NAME'
    STARTED = 'created'
    STATS_PORT_DEBUG_DEFAULT = 28125
    STATS_PORT_DEBUG_ENV = 'STATS_PORT_DEBUG'
    STATS_PORT_DEFAULT = 8125
    STATS_PORT_ENV = 'STATS_PORT'
    STATS_URL_DEFAULT = '172.17.0.1'
    STATS_URL_ENV = 'STATS_URL'
    STATUS = 'status'
    SUCCESS_RESPONSE_CODE = 200
    SUMO_CATEGORY_HEADER_KEY = 'X-Sumo-Category'
    SUMO_CATEGORY = 'prod/app/json'
    SUMO_HOST_HEADER = 'https/{account}/ecs/global/{service}/{environment}/{version}/ps'
    SUMO_HOST_HEADER_KEY = 'X-Sumo-Host'
    SUMO_LEVEL_KEY = '@l'
    SUMO_MESSAGE_KEY = '@m'
    SUMO_TIMESTAMP_KEY = '@t'
    SUMO_TIMESTAMP_FORMAT = '%Y-%m-%dT%H:%M:%SZ'
    SUMOLOGIC = 'sumologic'
    SUMOLOGIC_MESSAGE_COUNT = 'messageCount'
    SUMOLOGIC_QUERY_URL = 'https://api.us2.sumologic.com/api/v1/search/jobs'
    TABLE = 'table'
    TASK_MANAGEMENT_URL_DEFAULT = 'https://jira.com'
    TASK_MANAGEMENT_URL_ENV = 'TASK_MANAGEMENT_URL'
    THRESHOLD = 'threshold'
    TIMEZONE = 'timezone'
    TITLE = 'title'
    TO_DATE_PARAMETER = 'to'
    TOTAL = 'TOTAL'
    TOPIARY = 'topiary'
    NEWRELIC_QUERY_URL = 'NEWRELIC_QUERY_URL'
    NEWRELIC_DEFAULT_QUERY_URL = 'https://insights-api.newrelic.com/v1/accounts/{account_id}/query?nrql={query}'
    UAT = 'uat'
    UAT_REGION = 'us-west-2'
    UNAUTHORIZED_CODE = 403
    UNAUTHORIZED_REQUEST_MESSAGE = json.dumps({'message': 'Access Denied. Please try again with a valid auth token.'})
    UNDERSCORE = '_'
    UNPROCESSABLE_ENTITY_CODE = 422
    UNPROCESSABLE_ENTITY_MESSAGE = json.dumps({'message': 'Invalid payload.'})
    USERS_EMAIL_QUERY = f'{PRODUCTION_URL_BASE}/users/?email='
    URL_SEPARATOR = '/'
    UTF8 = 'utf-8'
    VALUE = 'value'
    VERSION_CHECK_TIMEOUT = 60
    VERSION_ENV = 'VERSION'
    VERSION_RESPONSE_TEMPLATE = '{{"service": "{service}", "version": "{version}", "build-number": "{build_number}"}}'
    NEWRELIC_ACCOUNT_IDS = {'acct1': 1234567, 'acct2': 1234568}
    NEWRELIC_API_KEYS = {'acct1': 'reliabilly.newrelic_acct1_api_key', 'acct2': 'reliabilly.newrelic_acct2_api_key'}
    YML_EXTENSION = 'yml'
    ENCRYPTED_EXTENSION = 'encrypted'
    DYNAMO_ID_TABLE_KEY = {'AttributeName': ID, 'KeyType': 'HASH'}
    DYNAMO_ID_TABLE_ATTR = {'AttributeName': ID, 'AttributeType': 'S'}
    COLLECTION_RECEIVED_RESPONSE = RECEIVED_SUCCESS_CODE, COLLECTION_RECEIVED_MESSAGE
    PING_ROUTE = 'ping/'
    PING_RESPONSE = '{"answer": "pong"}'
    COUNT_ROUTE = 'count/'
    HEALTH_ROUTE = 'health/'
    VERSION_ROUTE = 'version/'
    PURGE_ROUTE = 'purge/'
    AUTH = 'auth'
    MANAGER = 'manager'
    DATA_CLIENT = 'data_client'
    COLLECT_DATA_CLIENT = 'collect_data_client'
    SECRETS_MANAGER = 'secrets_manager'
    COLLECTOR = 'collector'
    CONTROLLER = 'controller'
    FACTORY = 'factory'
    BODY_KEY = 'Body'
    HTTP_CLIENT = 'http_client'
    RESULTS_CLIENT = 'results_client'
    COLLECTION_REQUESTS = 'collection_requests'
    COLLECTION_RESULTS = 'collection_results'
    RUNNER_FACTORY = 'runner_factory'
    MODEL = 'model'
    QUEUE_RECEIVER_ID = 'SqsReceiver.run'
    SQS_URL_ENV = 'SQS_URL'
    SQS_PORT_ENV = 'SQS_PORT'
    DEFAULT_SQS_URL = 'http://localhost'
    DEFAULT_SQS_PORT = '9324'
    USE_DYNAMO = 'USE_DYNAMO'
    X_QUERY_KEY_HEADER = 'X-Query-Key'
    X_INSERT_KEY_HEADER = 'X-Insert-Key'
    NR_EMPTY_RESULTS_MESSAGE = 'Empty results in return payload.'
    NR_NO_RESULT_ITEM_MESSAGE = 'Results not in return payload.'
    SUMO_RETRY_EXCEEDED_MESSAGE = 'Retry count exceeded on querying results.'
    SUMO_MISSING_COUNT_MESSAGE = 'Missing message count on query results.'
    SUMO_NO_RESULT_FOUND_MESSAGE = 'Sumologic result not found for query.'
    FACETS = 'facets'
    CORRELATION_ID = 'correlation_id'
    IGNORE = 'ignore'
    TIMEOUT = 'timeout'
    DEFAULT_MESSAGE_WAIT_SECONDS = 5
    SQS_CREATION_ATTRIBUTES = {MESSAGE_RETENTION_PERIOD_KEY: MESSAGE_RETENTION_PERIOD_SEC}
    METRIC_EVENT_TYPE_KEY = 'eventType'
    METRIC_NAME_KEY = 'metric_name'
    METRIC_VALUE_KEY = 'metric_value'
    METRIC_TAG_KEY_PREFIX = 'metric_tag_'
    METRIC_EVENT_ID = 'METRIC_EVENT_ID'
    DEFAULT_METRIC_EVENT_ID = 'dev1'
    NEWRELIC_METRICS_INSERT_SECRET_ID = 'reliabilly.newrelic_acct1_api_insert_key'


def get_service_lists():
    service_list = list()
    lint_list = []
    test_list = list()
    compose_list = [Constants.COMPOSE_FILE_NAME]
    for directory in listdir(Constants.CURRENT_DIR):
        if path.exists(path.join(directory, Constants.DOCKER_FILE)):
            service_list.append(directory)
        if path.exists(path.join(directory, Constants.COMPOSE_FILE_NAME)):
            compose_list.append(path.join(directory, Constants.COMPOSE_FILE_NAME))
        if path.exists(path.join(directory, Constants.PYTHON_MODULE_FILE)):
            lint_list.append(directory)
        if path.exists(path.join(directory, Constants.TESTS_DIR)):
            if not listdir(path.join(directory, Constants.TESTS_DIR)) == []:
                test_list.append(directory)
    return service_list, lint_list, test_list, compose_list


# noinspection PyBroadException
class Settings:
    ENV = environ.get(Constants.ENVIRONMENT, None)
    AWS_ACCOUNT = environ.get(Constants.AWS_ACCOUNT, Constants.DEFAULT_AWS_ACCOUNT)
    AWS_REGION = environ.get(Constants.AWS_REGION, Constants.NONE)
    BUILD_BRANCH = environ.get(Constants.BRANCH_NAME_ENV, None)
    BUILD_NUMBER = environ.get(Constants.BUILD_NUMBER_ENV, Constants.NONE)
    BUILD_STAGE = environ.get(Constants.STAGE_ENV, None)
    COLLECTION_ENABLED = bool(environ.get(Constants.COLLECTION_ENABLED, True))
    COLLECTION_INTERVAL_SECONDS = int(environ.get(
        Constants.COLLECTION_INTERVAL_SECONDS_KEY, Constants.COLLECTION_INTERVAL_DEFAULT))
    DATA_MONITORING_URL = environ.get(Constants.DATA_MONITORING_URL_ENV, Constants.DATA_MONITORING_URL_DEFAULT)
    MONGO_DB_NAME = environ.get(Constants.MONGO_DB_NAME_ENV, Constants.DEFAULT_DB_NAME)
    MONGO_PORT = int(environ.get(Constants.MONGO_PORT_ENV, Constants.MONGO_PORT_DEFAULT))
    MONGO_URL = environ.get(Constants.MONGO_URL_ENV, Constants.MONGO_URL_DEFAULT)
    DV_URL = environ.get(Constants.DV_URL_ENV, Constants.DV_URL_DEFAULT)
    DYNAMO_PORT = int(environ.get(Constants.DYNAMO_PORT_ENV, Constants.DYNAMO_PORT_DEFAULT))
    DYNAMO_URL = environ.get(Constants.DYNAMO_URL_ENV, Constants.DYNAMO_URL_DEFAULT)
    SQS_URL = environ.get(Constants.SQS_URL_ENV, Constants.DEFAULT_SQS_URL)
    SQS_PORT = environ.get(Constants.SQS_PORT_ENV, Constants.DEFAULT_SQS_PORT)
    NEWRELIC_QUERY_URL = environ.get(Constants.NEWRELIC_QUERY_URL, Constants.NEWRELIC_DEFAULT_QUERY_URL)
    NOTIFY_CHANNEL = environ.get(Constants.NOTIFY_CHANNEL_NAME_ENV, None)
    PROXY_URL = environ.get(Constants.PROXY_URL_ENV, Constants.PROXY_URL_DEFAULT)
    QUEUE_URL = environ.get(Constants.QUEUE_URL_ENV, Constants.DEFAULT_QUEUE_URL)
    RELEASE_SPREADSHEET_URL = environ.get(Constants.RELEASE_SPREADSHEET_URL, Constants.RELEASE_SPREADSHEET_URL_DEFAULT)
    REMOTE_LOG_URL = environ.get(Constants.REMOTE_LOG_URL_ENV, None)
    SERVICE_NAME = environ.get(Constants.SERVICE_NAME_ENV, 'empty')
    SESSION_URL = environ.get(Constants.SESSION_URL_ENV, Constants.OKTA_SESSION_URL)
    SLACK_API_TOKEN = environ.get(Constants.SLACK_API_TOKEN_ID, None)
    SOURCE_CONTROL_URL = environ.get(Constants.SOURCE_CONTROL_URL_ENV, Constants.SOURCE_CONTROL_URL_DEFAULT)
    STATS_PORT_DEBUG = int(environ.get(Constants.STATS_PORT_DEBUG_ENV, Constants.STATS_PORT_DEBUG_DEFAULT))
    STATS_PORT = int(environ.get(Constants.STATS_PORT_ENV, Constants.STATS_PORT_DEFAULT))
    STATS_URL = environ.get(Constants.STATS_URL_ENV, Constants.STATS_URL_DEFAULT)
    TASK_MANAGEMENT_URL = environ.get(Constants.TASK_MANAGEMENT_URL_ENV, Constants.TASK_MANAGEMENT_URL_DEFAULT)
    VERSION = environ.get(Constants.VERSION_ENV, Constants.DEV)
    USE_DYNAMO = environ.get(Constants.USE_DYNAMO, None)
    LOCAL_NR_API_KEY = environ.get(Constants.LOCAL_API_NR_ENV, None)
    LOCAL_SUMO_API_KEY = environ.get(Constants.LOCAL_API_SUMO_ENV, None)
    AUTH_TOKEN = environ.get(Constants.AUTH_TOKEN, VERSION)
    RUN_SKIPPED = bool(environ.get(Constants.RUN_SKIPPED_ENV, False))
    METRIC_EVENT_ID = environ.get(Constants.METRIC_EVENT_ID, Constants.DEFAULT_METRIC_EVENT_ID)
    try:
        SERVICES, LINT_LIST, TEST_MODULES, COMPOSE_LIST = get_service_lists()
        LINT_MODULES = Constants.SPACE.join(LINT_LIST)
        COMPOSE_FLAGS = Constants.COMPOSE_FILE_FLAG_SEPARATOR + Constants.COMPOSE_FILE_FLAG_SEPARATOR.join(COMPOSE_LIST)
        LOCAL_MONITORING_API_KEY = str(environ.get('LOCAL_MONITORING_API_KEY', ''))
        MONITORING_API_KEY_NAME = str(environ.get('MONITORING_API_KEY_NAME', ''))
    except Exception:  # pylint: disable=broad-except
        # Keep containers from failing if this code runs as it is only for
        # builds and shouldn't be executing on containers.
        pass


def get_base_url(service_name=Settings.SERVICE_NAME):
    if Settings.ENV == Constants.UAT:
        return Constants.UAT_URL_BASE
    if Settings.ENV == Constants.PROD:
        return Constants.PROD_URL_BASE
    if service_name == Constants.ROOT_SERVICE:
        return Constants.LOCAL_STATIC_URL_BASE.format(service_name)
    if not Settings.ENV and Settings.SERVICE_NAME:
        return Constants.LOCAL_SERVICE_URL_BASE.format(service_name)
    return Constants.LOCAL_URL_BASE


def get_raw_service_url(service_name):
    url_base = get_base_url(service_name)
    if service_name == Constants.ROOT_SERVICE:
        return url_base
    return f'{url_base}{service_name}/'


def get_service_collection_url(service_name):
    base_url = get_raw_service_url(service_name)
    return f'{base_url}{Constants.COLLECTION_ROUTE}'


def get_service_url(service_name, offset=None):
    url_base = get_base_url(service_name)
    service_url = f'{url_base}{service_name}/'
    if offset:
        return f'{service_url}?limit=1000&offset={offset}'
    return service_url + '?limit=1000&offset={offset}'


def get_production_service_url(service_name, offset=None):
    service_url = f'{Constants.PRODUCTION_URL_BASE}/{service_name}/'
    if offset:
        return f'{service_url}?limit=1000&offset={offset}'
    return service_url + '?limit=1000&offset={offset}'


class PortMapper:
    next_port = None

    @classmethod
    def get_next_port(cls):
        if not cls.next_port:
            cls.next_port = Constants.STARTING_PORT
        else:
            cls.next_port += Constants.PORT_INCREMENT
        return cls.next_port


def get_compose_environment():
    for service in Settings.SERVICES:
        environ[f'{service.upper()}{Constants.PORT_ENV_SUFFIX}'] = str(PortMapper.get_next_port())
    environ[Constants.MONGO_PORT_ENV] = str(environ.get(Constants.MONGO_PORT_ENV, Constants.DEFAULT_MONGO_PORT))
    environ[Constants.APP_PORT_ENV] = str(Constants.DEFAULT_APP_PORT)
    environ[Constants.MONGO_URL_ENV] = environ.get(Constants.MONGO_URL_ENV, Constants.MONGO_URL_DEFAULT)
    PortMapper.next_port = Constants.STARTING_PORT
    environ['COMPOSE_CONVERT_WINDOWS_PATHS'] = '1'
