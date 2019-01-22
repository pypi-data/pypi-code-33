#!/usr/bin/env python

import abc
from datetime import datetime
from time import sleep
from .aws import Redshift
from .extras import get_epoch_timestamp, get_business_regions, TS_MILLIS_FORMAT, get_environment_variables
from .file import JSONFile
from .logger import Logger


class HydraStream(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, brand, channel, rdl_schema, odl_schema, log_table, max_attempts, streaming, level):
        """
        Constructor
        :param brand: brand name OLX or Letgo [String]
        :param channel: channel name: Android, iOS or Web [String]
        :param rdl_schema: raw data layer schema [String]
        :param odl_schema: operation data layer schema [String]
        :param log_table: log table name with schema [String]
        :param max_attempts: max number of load attempts [Integer]
        :param streaming: true is loading is coming from kinesis, false from file [Boolean]
        :param level: logging level [String]
        """
        # common attributes
        self._log_table = log_table
        self._level = level
        self._max_attempts = max_attempts
        self._streaming = streaming
        self._logger = Logger(logger_name=__name__, level=self._level)
        self._rdl_schema = rdl_schema
        self._odl_schema = odl_schema
        self._brand = brand.lower()
        self._channel = channel.lower()
        self._epoch = get_epoch_timestamp
        self._table_prefix = None
        self._table_suffix = 'ninja_{channel}'.format(channel=self._channel)

        # countries
        self._countries = []
        env_countries = get_environment_variables().get('COUNTRIES')
        if env_countries:
            self._countries = ["'" + x.upper() + "'" for x in env_countries.split(':')]

        # commands
        self._commands = None

        # manifest
        self._s3_manifest_path = None

        # database
        self._db_client = None

        # flags
        self._rdl_sync_table_truncated = False
        self._rdl_staging_table_truncated = False

        # files loaded/failed
        self._total_rows_affected = 0
        self._total_files_processed = 0
        self._ok_prefixes = []
        self._ko_prefixes = []

    def connect_database(self, config, profile, arn):
        """
        Configure database connection
        :param config: database configuration file path [String]
        :param profile: profile to connect to database [String]
        :param arn: role used to copy data from S3 to Redshift [String]
        :return: None
        """
        try:
            db_config = JSONFile(config)
            db_config.load()
            db_settings = db_config.get(profile)
            db_settings['level'] = self._level
            self._logger.info("Loaded database configuration file '{config}'.".format(config=config))
            self._db_client = Redshift(**db_settings)
            self._db_client.set_credentials(arn)
            self._logger.info("Connected")

        except Exception as e:
            self._logger.error(repr(e))
            raise

    def set_commands(self, commands):
        """
        Set commands to execute
        :param commands: commands to execute
        :return: None
        """
        self._commands = commands

    def get_commands(self):
        """
        Get commands to execute
        :return: list of commands [List<String>]
        """
        return self._commands

    def is_streaming(self):
        """
        Streaming
        :return: streaming [Boolean]
        """
        return self._streaming

    def get_log_table(self):
        """
        Get log table name
        :return: log table name [String]
        """
        return self._log_table

    def _get_rdl_tables_and_views(self):
        """
        Get all tables/views involved in the process corresponding to RDL schema
        :return: dictionary with RDL tables/views [Dictionary]
        """
        rdl_prefix = self._table_prefix + '_' + self._table_suffix
        rdl_tables_views = {
            'SyncTable': '{rdl_schema}.{rdl_prefix}_sync'.format(rdl_schema=self._rdl_schema,
                                                                 rdl_prefix=rdl_prefix),
            'StagingTable': '{rdl_schema}.{rdl_prefix}_staging'.format(rdl_schema=self._rdl_schema,
                                                                       rdl_prefix=rdl_prefix),
            'TransformationView': '{rdl_schema}.{rdl_prefix}_transformation_view'.format(rdl_schema=self._rdl_schema,
                                                                                         rdl_prefix=rdl_prefix)
        }

        return rdl_tables_views

    def _get_odl_tables_and_views(self):
        """
        Get all tables/views involved in the process corresponding to ODL schema
        :return: dictionary with ODL tables/views [Dictionary]
        """
        odl_tables_views = {}
        rdl_prefix = self._table_prefix + '_hydra_' + self._table_suffix
        odl_table_prefix = 'panamera{brand}_hydra_ninja_{channel}'.format(brand=self._brand,
                                                                          channel=self._channel)

        for business_region in get_business_regions():
            odl_tables_views[business_region] = {
                'TemplateTable': '{odl_schema}.{odl_table_prefix}_template'.format(odl_schema=self._odl_schema,
                                                                                   odl_table_prefix=odl_table_prefix),
                'HourlyTable': '{odl_schema}.fact_{brand}_{business_region}_hydra_hourly_{channel}_by_session_long'.format(odl_schema=self._odl_schema,
                                                                                                                           brand=self._brand,
                                                                                                                           business_region=business_region,
                                                                                                                           channel=self._channel),
                'TransformationView': '{odl_schema}.{rdl_prefix}_transformation_view'.format(odl_schema=self._odl_schema,
                                                                                             rdl_prefix=rdl_prefix),
                'HourlyLoadingView': '{odl_schema}.{rdl_prefix}_loading_view'.format(odl_schema=self._odl_schema,
                                                                                     rdl_prefix=rdl_prefix),
                'HourlyTransformationView': '{odl_schema}.{rdl_prefix}_hourly_by_session_long_transformation_view'.format(odl_schema=self._odl_schema,
                                                                                                                          rdl_prefix=rdl_prefix)
            }

        return odl_tables_views

    def get_last_sequence_loaded(self):
        """
        Get last sequence read from log table
        :return: last sequence read [String]
        """
        last_seq = None
        try:
            if self._db_client:
                query = """
                        SELECT sequence_number AS seq
                        FROM {log_table}
                        WHERE inserted_at = (
                            SELECT MAX(inserted_at)
                            FROM {log_table}
                            WHERE staged
                        )
                        ;
                        """.format(log_table=self.get_log_table())
                result = self._db_client.execute(query)

                if result['rowcount'] > 0:
                    last_seq = result['data'][0].seq
            else:
                raise Exception('No database connection established, connect to database before to run any method')
        except Exception as ex:
            self._logger.error(repr(ex))
            pass

        return last_seq

    def set_last_sequence(self, inserted_at, sequence_number):
        """
        Get last sequence read from log table
        :return: last sequence read
        """
        try:
            if self._db_client:

                query = """
                        INSERT INTO {log_table}
                        VALUES ('{inserted_at}'::TIMESTAMP, {sequence_number}, FALSE, FALSE)
                        ;
                        """.format(log_table=self.get_log_table(),
                                   inserted_at=datetime.strftime(inserted_at, TS_MILLIS_FORMAT),
                                   sequence_number=sequence_number)
                self._db_client.execute(query)
            else:
                raise Exception('No database connection established, connect to database before to run any method')
        except Exception as ex:
            self._logger.error(repr(ex))
            raise

    def _remove_sequences_not_processed(self):
        """
        Remove logs for sequences not processed
        :return: None
        """
        try:
            if self._db_client:
                query = """
                        DELETE FROM {log_table} WHERE not loaded;
                        """.format(log_table=self.get_log_table())
                self._db_client.execute(query)
            else:
                raise Exception('No database connection established, connect to database before to run any method')
        except Exception as ex:
            self._logger.error(repr(ex))
            raise

    def _update_sequence(self, field):
        """
        Update sequence, set it as loaded
        :param field: field to update, staged or loaded [String]
        :return: None
        """
        try:
            if self._db_client:
                if field == 'staged':
                    query = """
                        UPDATE {log_table}
                        SET loaded = TRUE
                        WHERE NOT staged
                        AND inserted_at < (
                            SELECT MAX(inserted_at)
                            FROM {log_table}
                        )
                        ;
                        """.format(log_table=self.get_log_table())
                    self._db_client.execute(query)

                    query = """
                            UPDATE {log_table}
                            SET staged = TRUE
                            WHERE NOT staged
                            ;
                            """.format(log_table=self.get_log_table())
                    self._db_client.execute(query)

                elif field == 'loaded':
                    query = """
                            UPDATE {log_table}
                            SET loaded = TRUE
                            WHERE NOT loaded
                            ;
                            """.format(log_table=self.get_log_table())
                    self._db_client.execute(query)
                    self._db_client.commit()

            else:
                raise Exception('No database connection established, connect to database before to run any method')
        except Exception as ex:
            self._logger.error(repr(ex))
            raise

    def _get_staging_mode(self):
        """
        Get staging mode
        :return: staging mode APPEND or TRUNCATE [String]
        """
        mode = 'TRUNCATE'
        try:
            if self._db_client:
                query = """
                            SELECT sequence_number AS seq
                            FROM {log_table}
                            WHERE NOT loaded 
                            AND inserted_at < (
                                SELECT MAX(inserted_at)
                                FROM {log_table}
                            );
                            """.format(log_table=self.get_log_table())
                result = self._db_client.execute(query)

                if result['rowcount'] > 0:
                    mode = 'APPEND'
            else:
                raise Exception('No database connection established, connect to database before to run any method')
        except Exception as ex:
            self._logger.error(repr(ex))
            pass

        return mode

    def get_extract_metrics(self):
        """
        Get extract metrics
        :return: dictionary with metrics related with the extract process [Dictionary]
        """
        return {
            "TotalRows": self._total_rows_affected,
            "PrefixesOK": self._ok_prefixes,
            "PrefixesKO": self._ko_prefixes
        }

    def extract(self, s3_path, json_as, manifest):
        """
        Extract data from the S3 and copy it to the sync table
        :param s3_path: s3 path to json file to load [String]
        :param json_as: s3 path to json manifest or 'auto' option [String]
        :param manifest: If prefix provided is a manifest [Boolean]
        :return: None
        """
        sync_table = self._get_rdl_tables_and_views()['SyncTable']

        try:
            if self._db_client:
                if not self._rdl_sync_table_truncated:
                    self._db_client.truncate(sync_table)
                    self._logger.info("TRUNCATE completed in the sync table '{sync_table}'".format(sync_table=sync_table))
                    self._rdl_sync_table_truncated = True

                result = self._db_client.copy(prefix=s3_path,
                                              table=sync_table,
                                              jsonas=json_as,
                                              manifest=manifest,
                                              compression='GZIP',
                                              maxerror=100000,
                                              truncatecolumns=True,
                                              acceptanydate=True,
                                              acceptinvchars=True,
                                              compupdate=False,
                                              statupdate=False)

                self._logger.info("COPY of the path '{s3_path}' completed' [Rows: {rows}]".format(s3_path=s3_path,
                                                                                                  rows=result['rowcount']))
                self._total_rows_affected += result['rowcount']
                self._ok_prefixes.append(s3_path)
            else:
                raise Exception('No database connection established, connect to database before to run any method')
        except Exception as _:
            self._ko_prefixes.append(s3_path)
            self._logger.error("Skipped loading of the path '{s3_path} into the table '{sync_table}'".format(s3_path=s3_path,
                                                                                                             sync_table=sync_table))
            pass

        self._total_files_processed += 1

    def transform(self):
        """
        Transform data loaded in the sync table and insert it in the staging table (RDL)
        :return: None
        """
        # status
        code = 0
        message = None

        try:
            if self._db_client:
                # starting timer
                start = datetime.now()

                # counters
                inserted_rows = 0

                staging_table = self._get_rdl_tables_and_views()['StagingTable']
                transformation_view = self._get_rdl_tables_and_views()['TransformationView']

                # truncate staging table
                loading_mode = self._get_staging_mode()
                self._logger.info('Staging mode set to {mode}'.format(mode=loading_mode))

                if loading_mode == 'TRUNCATE' or not self._streaming:
                    self._db_client.truncate(staging_table)
                    self._logger.info("TRUNCATE completed of the staging table '{staging_table}'".format(staging_table=staging_table))

                # transform and insert data into staging table using transformation view
                condition = ';'
                if self._countries:
                    condition = " WHERE country_code IN ({});".format(','.join(self._countries))
                    self._logger.warning('Applied filter to get only data for countries {}'.format(', '.join(self._countries)))

                query = 'INSERT INTO {staging_table} SELECT * FROM {transformation_view}{condition}'.format(staging_table=staging_table,
                                                                                                            transformation_view=transformation_view,
                                                                                                            condition=condition)

                result = self._db_client.execute(query)
                inserted_rows += result['rowcount']
                self._logger.info("INSERT completed in the staging table '{staging_table}' [Rows: {rows}]".format(staging_table=staging_table,
                                                                                                                  rows=result['rowcount']))

                if result['rowcount'] > 0:
                    self._db_client.analyze(staging_table)

                    if not self._streaming:
                        self._remove_sequences_not_processed()
                        self._logger.warning("Removed sequences not loaded from log table to avoid collisions")
                    else:
                        self._update_sequence(field='staged')
                        self._logger.info("Updated log table '{log_table} SET staged = TRUE'".format(log_table=self.get_log_table()))

                # ending timer
                end = datetime.now()
                elapsed_time = (end-start).total_seconds()

                self._logger.info('\r')
                self._logger.info('+++++++++++++++++++++++++++++++++++++')
                self._logger.info('|             STATISTICS            |')
                self._logger.info('+++++++++++++++++++++++++++++++++++++')
                self._logger.info('| Inserted:       {:12d} rows |'.format(inserted_rows))
                self._logger.info('| Elapsed time:   {:12d} sec  |'.format(int(elapsed_time)))
                self._logger.info('+++++++++++++++++++++++++++++++++++++')
            else:
                raise Exception('No database connection established. Connect to database before to run any method.')
        except Exception as e:
            code = 1
            message = repr(e)
            pass

        return code, message

    def load(self):
        """
        Load data into the final table from the staging table [ODL]
        :return: None
        """
        # status
        code = 0
        message = None

        try:
            if self._db_client:
                # starting timer
                start = datetime.now()

                # counters
                total_rows = 0
                inserted_rows = 0
                unknown_rows = 0

                # getting business region with data loaded
                rdl_staging_table = self._get_rdl_tables_and_views()['StagingTable']

                # changing autocommit mode
                self._db_client.set_autocommit(autocommit=False)

                query = """SELECT DISTINCT 
                                business_region     AS region,
                                COUNT(*)            AS rowcount
                           FROM {rdl_staging_table} 
                           GROUP BY business_region
                           ORDER BY business_region
                           ;
                        """.format(rdl_staging_table=rdl_staging_table)

                result = self._db_client.execute(query)
                regions_with_data = result['data']

                for row in regions_with_data:
                    total_rows += row.rowcount

                    if row.region == 'unknown':
                        unknown_rows += row.rowcount
                    else:
                        self._logger.info('>>> ' + row.region.upper())

                        # creating staging table
                        template_table = self._get_odl_tables_and_views()[row.region]['TemplateTable']
                        staging_table = template_table.replace('{odl_schema}.'.format(odl_schema=self._odl_schema), '').replace('_template', '_{business_region}_{epoch}_staging'.format(business_region=row.region,
                                                                                                                                                                                         epoch=get_epoch_timestamp())).strip()

                        query = 'CREATE TEMP TABLE {staging_table} (LIKE {template_table});'.format(staging_table=staging_table,
                                                                                                    template_table=template_table)

                        self._db_client.execute(query)
                        self._logger.info("CREATE TEMP table '{staging_table}' completed".format(staging_table=staging_table))

                        # inserting data into TEMP table
                        transformation_view = self._get_odl_tables_and_views()[row.region]['TransformationView']
                        query = """
                                INSERT INTO {staging_table}
                                SELECT * FROM {transformation_view}
                                WHERE region_nk = '{region}';
                                """.format(staging_table=staging_table,
                                           transformation_view=transformation_view,
                                           region=row.region)

                        result = self._db_client.execute(query)
                        inserted_rows += result['rowcount']

                        if result['rowcount'] > 0:
                            self._logger.info("INSERT INTO TEMP table '{staging_table}' completed [Rows: {rows}]".format(staging_table=staging_table,
                                                                                                                         rows=result['rowcount']))

                            # creating hourly view
                            hourly_loading_view = self._get_odl_tables_and_views()[row.region]['HourlyLoadingView']
                            query = 'DROP VIEW IF EXISTS {hourly_loading_view} CASCADE;'.format(hourly_loading_view=hourly_loading_view)
                            self._db_client.execute(query)

                            query = 'CREATE VIEW {hourly_loading_view} AS SELECT * FROM {staging_table}'.format(hourly_loading_view=hourly_loading_view,
                                                                                                                staging_table=staging_table)
                            self._db_client.execute(query)

                            # deleting data in hourly table
                            hourly_table = self._get_odl_tables_and_views()[row.region]['HourlyTable']
                            if not self._streaming:
                                query = """
                                        DELETE FROM {hourly_table}
                                        USING (SELECT DISTINCT 
                                                    server_path                                                  AS server_path,
                                                    SPLIT_PART(country_sk,'|',1) || split_part(country_sk,'|',3) AS livesync_dbname,
                                                    TO_CHAR(time_event_local, 'YYYYMMDDHH24')::INTEGER           AS hour_sk
                                               FROM  {staging_table}) AS tmp
                                        WHERE {hourly_table}.server_path = tmp.server_path
                                        AND   {hourly_table}.livesync_dbname = tmp.livesync_dbname
                                        AND   {hourly_table}.hour_sk = tmp.hour_sk;
                                        """.format(hourly_table=hourly_table,
                                                   staging_table=staging_table)

                                result = self._db_client.execute(query)
                                self._logger.info("DELETE of data from hourly table '{hourly_table}' completed [Rows: {rows}]".format(hourly_table=hourly_table,
                                                                                                                                      rows=result['rowcount']))

                            # inserting data in hourly table
                            transformation_view = self._get_odl_tables_and_views()[row.region]['HourlyTransformationView']
                            query = 'INSERT INTO {hourly_table} SELECT * FROM {transformation_view};'.format(hourly_table=hourly_table,
                                                                                                             transformation_view=transformation_view)

                            result = self._db_client.execute(query)
                            self._logger.info("INSERT INTO table '{hourly_table}' completed [Rows: {rows}]".format(hourly_table=hourly_table,
                                                                                                                   rows=result['rowcount']))

                            # selecting distinct months to load
                            query = """
                                    SELECT DISTINCT
                                        TO_CHAR(date_event_nk, 'YYYYMM') AS month_nk
                                    FROM {staging_table}
                                    WHERE date_event_nk IS NOT NULL;
                                    """.format(staging_table=staging_table)

                            result = self._db_client.execute(query)
                            months = result['data']

                            for month in months:
                                # creating final table if does not exist
                                tracking_table = (template_table.replace('_template', '_{month}'.format(month=month.month_nk))).replace('{brand}_hydra'.format(brand=self._brand), '{brand}_{business_region}_hydra'.format(brand=self._brand, business_region=row.region))
                                query = 'CREATE TABLE IF NOT EXISTS {tracking_table} (LIKE {template_table});'.format(tracking_table=tracking_table,
                                                                                                                      template_table=template_table)

                                self._db_client.execute(query)

                                attempt = 1
                                delete_status = False
                                insert_status = False

                                while attempt <= self._max_attempts:
                                    try:
                                        self._logger.info('ATTEMPT #{attempt}'.format(attempt=attempt))

                                        # deleting data in tracking table
                                        if not self._streaming:
                                            if not delete_status:
                                                query = """
                                                    DELETE FROM {tracking_table}
                                                    USING (SELECT DISTINCT 
                                                                server_path             AS server_path,
                                                                country_sk              AS country_sk,
                                                                min(time_event_local)   AS min_time_event_local,
                                                                max(time_event_local)   AS max_time_event_local
                                                           FROM  {staging_table}
                                                           GROUP BY 1, 2
                                                           ORDER BY 1, 2) AS tmp
                                                    WHERE {tracking_table}.server_path = tmp.server_path
                                                    AND   {tracking_table}.country_sk = tmp.country_sk
                                                    AND   {tracking_table}.time_event_local BETWEEN tmp.min_time_event_local AND tmp.max_time_event_local;
                                                    """.format(tracking_table=tracking_table,
                                                               staging_table=staging_table)

                                            result = self._db_client.execute(query)
                                            self._logger.info("DELETE of data from tracking table '{tracking_table}' completed [Rows: {rows}]".format(tracking_table=tracking_table,
                                                                                                                                                      rows=result['rowcount']))

                                            delete_status = True

                                        if not insert_status:
                                            # inserting data in tracking table
                                            query = 'INSERT INTO {tracking_table} SELECT * FROM {staging_table};'.format(tracking_table=tracking_table,
                                                                                                                         staging_table=staging_table)

                                            result = self._db_client.execute(query)
                                            self._logger.info("INSERT INTO table '{tracking_table}' completed [Rows: {rows}]".format(tracking_table=tracking_table,
                                                                                                                                     rows=result['rowcount']))

                                            # drop staging table
                                            self._db_client.drop(staging_table)

                                            insert_status = True

                                        code = 0
                                        message = None
                                        break

                                    except Exception as e:
                                        if attempt > self._max_attempts:
                                            code = 1
                                            message = repr(e)
                                            break
                                        else:
                                            attempt += 1
                                            self._logger.info('Waiting 60 seconds before the next loading attempt...')
                                            sleep(60)
                                        pass

                                if code == 1:
                                    break
                        else:
                            self._logger.warning("No data loaded in TEMP table '{staging_table}'".format(staging_table=staging_table))

                if code == 0:
                    self._db_client.commit()

                    # update log table
                    if self._streaming:
                        self._update_sequence(field='loaded')
                        self._logger.info("Updated log table '{log_table} SET loaded = TRUE'".format(log_table=self.get_log_table()))

                    # truncating rdl staging table
                    self._db_client.truncate(rdl_staging_table)

                # ending timer
                end = datetime.now()
                elapsed_time = (end-start).total_seconds()

                self._logger.info('\r')
                self._logger.info('+++++++++++++++++++++++++++++++++++++')
                self._logger.info('|             STATISTICS            |')
                self._logger.info('+++++++++++++++++++++++++++++++++++++')
                self._logger.info('| Unknown region: {:12d} rows |'.format(unknown_rows))
                self._logger.info('| Bots/Blacklist: {:12d} rows |'.format(total_rows - unknown_rows - inserted_rows))
                self._logger.info('| Inserted:       {:12d} rows |'.format(inserted_rows))
                self._logger.info('| Elapsed time:   {:12d} sec  |'.format(int(elapsed_time)))
                self._logger.info('+++++++++++++++++++++++++++++++++++++')
            else:
                raise Exception('No database connection established. Connect to database before to run any method.')

        except Exception as e:
            code = 1
            message = repr(e)
            pass

        return code, message
