import json
import logging

import pandas as pd

from serenytics.task import Task
from .helpers import SerenyticsException, make_request, HTTP_201_CREATED
from . import settings

logger = logging.getLogger(__name__)


class UnknownDataSource(SerenyticsException):
    def __init__(self, uuid_or_name):
        super(UnknownDataSource, self).__init__(u'Source with uuid or name "{}" does not exist'.format(uuid_or_name))


class DataSource(object):
    """
    Serenytics data source
    """

    def __init__(self, config, client):
        self._config = config
        self._client = client
        self._headers = client._headers

    def _check_is_storage_source(self):
        if self._config['type'] != 'Storage':
            raise SerenyticsException('Error: You can only reload the data of a storage data source.')

    @property
    def name(self):
        return self._config['name']

    @property
    def uuid(self):
        return self._config['uuid']

    @property
    def type(self):
        return self._config['type']

    @property
    def _measures(self):
        return self._config['jsonContent'].get('measures')

    def reload_data(self, new_data):
        """
        Reset data of a Storage data source.

        It erases old data and loads new data instead.

        Notes:
            - current data source must be a Storage data source
            - new data doesn't have to have the same structure as old data.
        """
        self._check_is_storage_source()

        reload_url = settings.SERENYTICS_API_DOMAIN + '/api/data_source/' + self.uuid + '/reload'
        make_request('post', reload_url, data=json.dumps(new_data), headers=self._headers,
                     expected_json_status='ok')

    def reload_data_from_array(self, columns, rows):
        """
        Reset data of a Storage data source.

        It erases old data and loads new data instead.

        :param columns: list of string, each string is a column name
        :param rows: list of list of values, each list of values is a row

        Notes:
            - current data source must be a Storage data source
            - new data doesn't have to have the same structure as old data.
        """
        self._check_is_storage_source()

        new_data = []
        for r in rows:
            new_row = {}
            for idx, column in enumerate(columns):
                column_name = column if column != '$$count$$' else '__count__'
                new_row[column_name] = r[idx]
            new_data.append(new_row)

        self.reload_data(new_data)

    def reload_data_from_dataframe(self, df):
        """
        Reset data of a Storage data source.

        It erases old data and loads new data instead.

        :param df: pandas dataframe to load in the source

        Notes:
            - current data source must be a Storage data source
            - new data doesn't have to have the same structure as old data.
        """
        self._check_is_storage_source()

        rows = df.values.tolist()
        self.reload_data_from_array(df.columns, rows)

    def reload_data_from_file(self, filename, separator=',', force_types=None):
        """
        Reset data of a Storage data source.

        It erases old data and loads new data from the given file instead.

        :param filename: path of the file to load. The file must be a csv file (.csv) and can be gzipped (.csv.gz) for
        better transfer speed and shorter script execution times.
        :param separator: CSV field separator, usually a comma or a semicolon.
        :param force_types: Dict of column names with types ('int', 'float', 'datetime', 'str') to force column type in
        our storage.

        Notes:
            - current data source must be a Storage data source
            - new data doesn't have to have the same structure as old data.
        """
        self._check_is_storage_source()

        if not filename.endswith(('.csv', '.csv.gz')):
            raise SerenyticsException('filename must end with ".csv" or ".csv.gz"')

        self._upload_new_file(filename, separator, force_types)
        self._load_data_from_file()

    def reload_data_from_s3_file(self, s3_bucket, s3_key, s3_csv_separator=None, s3_region=None, s3_credentials=None,
                                 force_types=None):
        """
        Reset data of a Storage data source.

        It erases old data and loads new data from the given S3 file instead.

        :param s3_bucket: S3 bucket of the object to load
        :param s3_key: S3 key of the object to load
        :param s3_csv_separator: Optional, CSV field separator, usually a comma or a semicolon.
        :param s3_region: Optional, must be provided if region is different from the redshift region
        :param s3_credentials: Optional, must be provided if the object is not public (must be a string with such as
        "aws_access_key_id=my_aws_access_key_id;aws_secret_access_key=my_aws_secret_access_key"
        :param force_types: force some column types

        Notes:
            - current data source must be a Storage data source
            - new data doesn't have to have the same structure as old data.
        """
        self._check_is_storage_source()
        self._load_data_from_s3_file(s3_bucket, s3_key, s3_csv_separator, s3_region, s3_credentials, force_types)

    def update_data_from_file(self, filename, primary_key, separator=','):
        """
        Update data of a Storage data source.

        Inserts new data from filename in current source and replace rows with same primary key as in given file.

        :param filename: path of the file to load. The file must be a csv file (.csv) and can be gzipped (.csv.gz) for
        better transfer speed and shorter script execution times.
        :param primary_key: column name of the primary key (the key used to uniquely define the data rows, such as an id
        or a guid).
        :param separator: CSV field separator, usually a comma or a semicolon.

        Notes:
            - current data source must be a Storage data source
            - new data has to have the same structure as old data
        """
        self._check_is_storage_source()

        if not filename.endswith(('.csv', '.csv.gz')):
            raise SerenyticsException('filename must end with ".csv" or ".csv.gz"')

        self._upload_new_file(filename, separator=separator)
        self._update_data_from_file(primary_key)

    def _upload_new_file(self, filename, separator=None, force_types=None):
        self._config['originalFileName'] = filename

        if separator is not None:
            self._config['jsonContent']['separator'] = separator

        if force_types is not None:
            self._config['jsonContent']['advanced_options'] = json.dumps({'force_types': force_types})

        self.save()

        response = make_request('GET', settings.SERENYTICS_API_DOMAIN + '/api/data_source/sign_s3/',
                                params={'s3_object_type': 'csv/gz', 's3_object_name': self.uuid},
                                headers=self._headers)
        response_content = response.json()

        with open(filename, 'rb') as file_to_upload:
            data = file_to_upload.read()

        if response_content['status'] == 'error':
            # the server doesn't use S3
            make_request('POST', settings.SERENYTICS_API_DOMAIN + '/api/data_source/' + self.uuid + '/file',
                         data=data, headers=self._headers, expected_status_code=HTTP_201_CREATED)
        else:
            make_request('PUT', response_content['signed_request'], data=data,
                         headers={'Content-Type': 'csv/gz', 'x-amz-acl': 'private'})

    def _load_data_from_file(self):
        response = make_request('POST',
                                settings.SERENYTICS_API_DOMAIN + '/api/data_source/' + self.uuid + '/reload_from_file',
                                data=json.dumps({'async': True}),
                                headers=self._headers)
        task = Task(task_id=response.json()['task_id'], description="Reload data from file", headers=self._headers)
        task.wait()
        task.raise_on_error()
        logger.info('import status: %s' % task.result)

    def _load_data_from_s3_file(self, s3_bucket, s3_key, s3_csv_separator, s3_region, s3_credentials, force_types):
        payload = {
            'async': True,
            's3_bucket': s3_bucket,
            's3_key': s3_key
        }
        if s3_csv_separator:
            payload['s3_csv_separator'] = s3_csv_separator
        if s3_region:
            payload['s3_region'] = s3_region
        if s3_credentials:
            payload['s3_credentials'] = s3_credentials
        if force_types is not None:
            payload['force_types'] = force_types

        response = make_request('POST',
                                settings.SERENYTICS_API_DOMAIN + '/api/data_source/' + self.uuid + '/reload_from_s3',
                                data=json.dumps(payload),
                                headers=self._headers)
        task = Task(task_id=response.json()['task_id'], description="Reload data from S3", headers=self._headers)
        task.wait()
        task.raise_on_error()
        logger.info('import status: %s' % task.result)

    def _update_data_from_file(self, primary_key):
        response = make_request('POST',
                                settings.SERENYTICS_API_DOMAIN + '/api/data_source/' + self.uuid + '/update_from_file',
                                data=json.dumps({'primary_key': primary_key, 'async': True}),
                                headers=self._headers)
        task = Task(task_id=response.json()['task_id'], description="Update data from file", headers=self._headers)
        task.wait()
        task.raise_on_error()

    def batch(self,
              rows_to_insert=None,
              rows_to_insert_or_update=None,
              rows_to_delete=None,
              primary_key=None,
              async=False):
        """
        Run batch operations on data source (insert/update/delete).

        Note: either `rows_to_insert`, `rows_to_insert_or_update` or `rows_to_delete` must be supplied to the function
        as a list of rows.

        Notes:
            - current data source must be a Storage data source
            - new data has to have the same structure as old data.
        """
        self._check_is_storage_source()

        def _check_argument(arg, name):
            if arg and not isinstance(arg, (list, tuple)):
                raise SerenyticsException('%s must be a list or a tuple, and it was: %r' % (name, arg))

        _check_argument(rows_to_insert, 'rows_to_insert')
        _check_argument(rows_to_insert_or_update, 'rows_to_insert_or_update')
        _check_argument(rows_to_delete, 'rows_to_delete')

        if rows_to_insert is None and rows_to_insert_or_update is None and rows_to_delete is None:
            raise SerenyticsException('at least one argument in `rows_to_insert`, `rows_to_insert_or_update` and'
                                      ' `rows_to_delete` must be not None')
        if (rows_to_insert_or_update or rows_to_delete) and primary_key is None:
            raise SerenyticsException('`primary_key`argument must be not None when updating or deleting rows')

        operations = []

        if rows_to_insert:
            operations.append({
                'action': 'insert',
                'rows': rows_to_insert
            })

        if rows_to_insert_or_update:
            operations.append({
                'action': 'insertOrUpdate',
                'rows': rows_to_insert_or_update,
                'primaryKey': primary_key
            })

        if rows_to_delete:
            operations.append({
                'action': 'delete',
                'rows': rows_to_delete,
                'primaryKey': primary_key
            })

        batch_url = settings.SERENYTICS_API_DOMAIN + '/api/data_source/' + self.uuid + '/batch'
        make_request('post', batch_url, headers=self._headers,
                     data=json.dumps({
                         'async': async,
                         'operations': operations
                     }),
                     expected_json_status='ok')

    def push_data(self, data):
        """
        Append `data` to current storage data source.

        Warning: this call is not blocking and doesn't wait for the data to be imported into serenytics datawarehouse.
        Then you won't have any guarantee that the data has really been imported. If you need a guarantee, at the
        expense of a longer function call, please use method `batch` and regroup all your rows of data
        in a list.
        """
        self._check_is_storage_source()
        token = self._config['token']
        push_url = settings.SERENYTICS_API_DOMAIN + '/api/data_source/' + self.uuid + '/push/' + token
        make_request('post', push_url, data=json.dumps(data), headers=self._headers)

    def get_data(self, options=None):
        """
        Extract data from the data source
        """
        no_options = options is None

        if no_options:
            options = {'only_headers': True}

        self._add_measure_uuid_when_needed(options)

        response = make_request('post', settings.SERENYTICS_API_DOMAIN + '/api/formatted_data/' + self.uuid,
                                data=json.dumps(options),
                                headers=self._headers)
        response_content = response.json()

        if response_content['status'] == 'error':
            raise SerenyticsException(response_content['errors'][0])

        if not no_options:
            return Data(response_content)

        # make second API call to retrieve actual data
        headers = response_content['columns_titles']
        new_options = {
            'order': 'row_by_row',
            'data_processing_pipeline': [{
                'select': [header['name'] for header in headers]
            }]
        }
        response = make_request('post', settings.SERENYTICS_API_DOMAIN + '/api/formatted_data/' + self.uuid,
                                data=json.dumps(new_options),
                                headers=self._headers)
        response_content = response.json()

        if response_content['status'] == 'error':
            raise SerenyticsException(response_content['errors'][0])

        return Data(response_content)

    def _add_measure_uuid_when_needed(self, options):
        if 'data_processing_pipeline' not in options:
            return

        measures = self._measures
        if not measures:
            return

        measure_uuid_by_name = {measures[uuid]['name']: uuid for uuid in measures}

        headers_to_process = [
            header
            for header_list in ('select', 'where', 'group_by', 'order_by')
            for step in options['data_processing_pipeline']
            if header_list in step
            for header in step[header_list]
        ]

        for header in headers_to_process:
            if isinstance(header, dict) and 'name' in header:
                name = header['name']
                if name in measure_uuid_by_name:
                    header['measureUuid'] = measure_uuid_by_name[name]

    # for backward compatibility only
    def _save(self):
        self.save()

    def save(self):
        make_request('PUT', settings.SERENYTICS_API_DOMAIN + '/api/data_source/' + self.uuid,
                     data=json.dumps(self._config),
                     headers=self._headers)

    def invalidate_cache(self):
        """
        Invalidate data source cache.

        All get_data() calls or calls made when loading a dashboard using this source won't use current cache.
        Works whatever the cache config of the source (i.e. if the source is static, or cached for 24h, or another
        duration).
        """
        url = settings.SERENYTICS_API_DOMAIN + '/api/data_source/' + self.uuid + '/invalidate_cache'
        make_request('post', url, headers=self._headers)

    def reload_users_metadata(self):
        """
        Reload users metadata with the data from this source.

        The data source should have a first column named login with one row by user in the organization. Other
        columns will be stored as user metadata.

        Note:
        - The user authenticated must be admin of this organization.
        """
        url = settings.SERENYTICS_API_DOMAIN + '/api/data_source/' + self.uuid + '/reload_users_metadata'
        make_request('post', url, headers=self._headers)

    def set_property(self, property_name, value):
        """
        Set a property of this source.
        Contact support@serenytics.com for the list of properties you can set for a given data source type.
        """
        self._config['jsonContent'][property_name] = value


class Data(object):
    """
    Handles data extracted from a data source
    """

    def __init__(self, raw_data):
        self._raw_data = raw_data

    @property
    def headers(self):
        return self._raw_data.get('columns_titles', [])

    @property
    def columns(self):
        return [header['name'] for header in self.headers]

    @property
    def rows(self):
        return self._raw_data.get('data', [])

    def get_as_dataframe(self):
        return pd.DataFrame(self.rows, columns=self.columns)
