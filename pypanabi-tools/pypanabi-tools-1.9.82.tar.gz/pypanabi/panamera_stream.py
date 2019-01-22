#!/usr/bin/env python

from .hydra_stream import HydraStream


class PanameraStream(HydraStream):
    def __init__(self, brand, channel, rdl_schema, odl_schema, log_table, max_attempts=5, streaming=True, level='INFO'):
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
        # super initialization
        HydraStream.__init__(self, brand, channel, rdl_schema, odl_schema, log_table, max_attempts, streaming, level)

        # prefix
        self._table_prefix = 'panamera{brand}'.format(brand=self._brand)
