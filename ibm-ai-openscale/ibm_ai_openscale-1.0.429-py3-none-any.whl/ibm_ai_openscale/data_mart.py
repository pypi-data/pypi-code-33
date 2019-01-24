# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-J33
# Copyright IBM Corp. 2018
# The source code for this program is not published or other-wise divested of its trade 
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

from ibm_ai_openscale.supporting_classes import *
from ibm_ai_openscale.subscriptions import Subscriptions
from ibm_ai_openscale.bindings import Bindings
import inspect


class DataMart:
    """
    Manages DB Instance.

    :var bindings: Manage bindings of you AI OpenScale instance.
    :vartype bindings: Bindings
    :var subscriptions: Manage subscriptions of you AI OpenScale instance.
    :vartype subscriptions: Subscriptions
    """
    def __init__(self, ai_client):
        from ibm_ai_openscale.base_classes.client.client import APIClientBase
        validate_type(ai_client, 'ai_client', APIClientBase, True)
        self._logger = logging.getLogger(__name__)
        self._ai_client = ai_client
        self._internal_db = False
        self.bindings = Bindings(ai_client)
        self.subscriptions = Subscriptions(ai_client)

    def _prepare_db_credentials_payload(self, postgres_credentials=None, db_credentials=None, schema=None, internal_db=False):
        if internal_db is False:
            if postgres_credentials is not None:
                # DeprecationWarning does not work in notebook - need to use print as workaround sic!
                # TODO remove in next major release support for this and optional Schema
                print("DeprecationWarning: 'postgres_credentials' parameter is deprecated and will be removed in 1.1.0 release; use 'db_credentials' instead.")
                db_credentials = postgres_credentials

            validate_type(db_credentials, 'db_credentials', [dict, DatabaseCredentials], True)
            validate_type(schema, 'schema', str, False)

            if type(db_credentials) == dict:
                if 'uri' in db_credentials:
                    validate_type(db_credentials['uri'], 'db_credentials.uri', str, False)
                if 'jdbcurl' in db_credentials:
                    validate_type(db_credentials['jdbcurl'], 'db_credentials.jdbcurl', str, False)
                if 'db_type' in db_credentials:
                    validate_type(db_credentials['db_type'], 'db_credentials.db_type', str, False)

                if 'uri' not in db_credentials and 'jdbcurl' not in db_credentials and 'db_type' not in db_credentials:
                    raise ClientError("Required fields missing in db_credentials. Non of following were found: uri, jdbcurl, db_type. To correct this error add `db_type` field set to one of these values: db2, postgresql.")

                if 'db_type' in db_credentials:
                    db_type = db_credentials['db_type']
                else:

                    db_type_url = db_credentials['uri'] if 'uri' in db_credentials else db_credentials['jdbcurl']

                    if 'postgres' in db_type_url:
                        db_type = "postgresql"
                    elif 'db2' in db_type_url:
                        db_type = "db2"
                    else:
                        raise ClientError("Unsupported type of db.")
            else:
                if type(db_credentials) == DB2:
                    db_type = "db2"
                elif type(db_credentials) == PostgreSQL:
                    db_type = "postgresql"

                db_credentials = db_credentials.credentials # TODO in final version it should be reworked

            if 'name' in db_credentials.keys():
                db_name = db_credentials['name']
            else:
                db_name = str(db_type)

            database_configuration = {
                "database_type": db_type,
                "name": db_name,
                "credentials": db_credentials,
                "location": {}
            }

            if schema is not None:
                database_configuration['location']['schema'] = schema

            payload = {"database_configuration": database_configuration}
        else:
            self._internal_db = internal_db
            payload = {"internal_database": internal_db}

        return payload

    def setup(self, postgres_credentials=None, db_credentials=None, schema=None, internal_db=False):
        """
        Setups db instance.

        :param db_credentials: describes the instance which should be connected
        :type db_credentials: dict

        :param schema: schema in your database under which the tables should be created
        :type schema: str

        :param internal_db: you can use internally provided database. Please note that this db comes with limitations.
        :type internal_db: bool

        Examples of usage (postgres):

        >>> postgres_credentials = {
        >>>     "db_type": "postgresql",
        >>>     "uri_cli_1": "xxx",
        >>>     "maps": [],
        >>>     "instance_administration_api": {
        >>>         "instance_id": "xxx",
        >>>         "root": "xxx",
        >>>         "deployment_id": "xxx"
        >>>     },
        >>>     "name": "xxx",
        >>>     "uri_cli": "xxx",
        >>>     "uri_direct_1": "xxx",
        >>>     "ca_certificate_base64": "xxx",
        >>>     "deployment_id": "xxx",
        >>>     "uri": "xxx"
        >>> }
        >>>
        >>> # option 1:
        >>> ai_client.data_mart.setup(db_credentials=postgres_credentials)
        >>> # option 2:
        >>> ai_client.data_mart.setup(db_credentials=PostgreSQL(postgres_credentials))

        Examples of usage (db2):

        >>> db2_credentials = {
        >>>     "hostname": "xxx",
        >>>     "password": "xxx",
        >>>     "https_url": "xxx",
        >>>     "port": 50000,
        >>>     "ssldsn": "xxx",
        >>>     "host": "xxx",
        >>>     "jdbcurl": "xxx",
        >>>     "uri": "xxx",
        >>>     "db": "BLUDB",
        >>>     "dsn": "xxx",
        >>>     "username": "xxx",
        >>>     "ssljdbcurl": "xxx"
        >>> }
        >>>
        >>> # option 1:
        >>> ai_client.data_mart.setup(db_credentials=db2_credentials)
        >>> # option 2:
        >>> ai_client.data_mart.setup(db_credentials=DB2(db2_credentials))

        Example of usage (internal db):

        >>> ai_client.data_mart.setup(internal_db=True)
        """

        payload = self._prepare_db_credentials_payload(postgres_credentials, db_credentials, schema, internal_db)

        response = requests_session.put(
            self._ai_client._href_definitions.get_data_mart_href(),
            json=payload,
            headers=self._ai_client._get_headers()
        )

        try:
            handle_response(200, "setup of data mart", response, False)
        except ApiRequestWarning:
            ApiRequestWarning.print_msg(error_msg=u'Warning during {}.'.format('setup of data mart'), response=response)
            return

    def update(self, postgres_credentials=None, db_credentials=None, schema=None):
        """
         Updates data mart configuration to work with new db instance. There is no data migration.

         :param db_credentials: describes the instance which should be connected
         :type db_credentials: dict

         :param schema: schema in your database under which the tables should be created (optional)
         :type schema: str
        """

        payload = self._prepare_db_credentials_payload(postgres_credentials, db_credentials, schema, False)

        response = requests_session.put(
            self._ai_client._href_definitions.get_data_mart_href() + '?force=true',
            json=payload,
            headers=self._ai_client._get_headers()
        )

        handle_response(200, "setup of data mart", response, False)

    def get_details(self):
        """
        Get db instance details.

        :return: db instance details
        :rtype: dict
        """

        response = requests_session.get(
            self._ai_client._href_definitions.get_data_mart_href(),
            headers=self._ai_client._get_headers()
        )

        result = handle_response(200, "getting data mart details", response, True)

        if ("internal_database" in result.keys()) and result['internal_database'] and ('._ai_client' not in str(inspect.stack()[1])):
            return handle_credentials(result)
        else:
            return result

    def get_deployment_metrics(self, subscription_uid=None, asset_uid=None, deployment_uid=None, metric_type=None):
        """
        Get metrics.

        :param subscription_uid: UID of subscription for which the metrics which be prepared (optional)
        :type subscription_uid: str

        :param asset_uid: UID of asset for which the metrics which be prepared (optional)
        :type asset_uid: str

        :param deployment_uid: UID of deployment for which the metrics which be prepared (optional)
        :type deployment_uid: str

        :param metric_type: metric type which should be returned (optional)
        :type metric_type: str

        :return: metrics
        :rtype: dict
        """
        validate_type(subscription_uid, 'subscription_uid', str, False)
        validate_type(asset_uid, 'asset_uid', str, False)
        validate_type(deployment_uid, 'deployment_uid', str, False)

        # TODO MetricTypes should be enum
        validate_type(metric_type, 'metric_type', [MetricTypes, str], False)

        response = requests_session.get(
            self._ai_client._href_definitions.get_deployment_metrics_href(),
            headers=self._ai_client._get_headers()
        )

        details = handle_response(200, "getting deployment metrics", response, True)['deployment_metrics']

        if subscription_uid is not None:
            details = list(filter(lambda x: x['subscription']['subscription_id'] == subscription_uid, details))

        if asset_uid is not None:
            details = list(filter(lambda x: x['asset']['asset_id'] == asset_uid, details))

        if deployment_uid is not None:
            details = list(filter(lambda x: x['deployment']['deployment_id'] == deployment_uid, details))

        if metric_type is not None:
            for record in details:
                record['metrics'] = list(filter(lambda m: m['metric_type'] == metric_type, record['metrics']))

        return {'deployment_metrics': details}

    def delete(self, force=True):
        """
        Delete data_mart configuration.

        :param force: force configuration deletion
        :type force: bool
        """

        validate_type(force, 'force', bool, True)
        response = requests_session.delete(
            self._ai_client._href_definitions.get_data_mart_href() + '?force=' + str(force).lower(),
            headers=self._ai_client._get_headers()
        )

        handle_response(202, "delete of data mart", response, False)

        start_time = time.time()
        elapsed_time = 0
        timeout = 120
        while True and elapsed_time < timeout:
            try:
                self.get_details()
                elapsed_time = time.time() - start_time
                time.sleep(10)
            except ApiRequestFailure as ex:
                if "404" in str(ex.error_msg):
                    return
                else:
                    raise ex

        self._logger.info("Deletion takes more than {} seconds - switching to background mode".format(timeout))

