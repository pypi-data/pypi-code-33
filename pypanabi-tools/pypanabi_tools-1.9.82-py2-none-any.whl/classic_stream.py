#!/usr/bin/env python

from .hydra_stream import HydraStream
from datetime import datetime
from time import sleep
from .extras import get_epoch_timestamp


class ClassicStream(HydraStream):
    def __init__(self, brand, region, channel, rdl_schema, odl_schema, log_table, max_attempts=5, streaming=True, level='INFO'):
        """
        Constructor
        :param brand: brand name OLX or Letgo [String]
        :param region: classic region or business region name: CEE, SSA, MENA, MENAPK, ID, PH, SA, CEE,
                                                               LATAM. MEA, ASIA or EU
        :param channel: channel name: Android, iOS or Web [String]
        :param rdl_schema: raw data layer schema [String]
        :param odl_schema: operation data layer schema [String]
        :param log_table: log table name with schema [String]
        :param max_attempts: max number of load attempts [Integer]
        :param streaming: true is loading is coming from kinesis, false from file [Boolean]
        :param level: logging level [String]
        """
        # super initialization
        HydraStream.__init__(self, brand, channel, rdl_schema, odl_schema, log_table, max_attempts, streaming, level)

        # prefix
        self._table_prefix = 'classic{brand}_{region}'.format(brand=self._brand,
                                                              region=region)

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
