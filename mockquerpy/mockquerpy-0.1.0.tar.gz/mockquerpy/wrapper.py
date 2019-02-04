#!/usr/bin/env python
# -*- coding: utf-8 -*-

import mockquerpy
import sys

class MockQuerPy():
    mockmap = {
        'google.cloud.bigquery': mockquerpy,
        'google.cloud.bigquery.client': mockquerpy.client,
        'google.cloud.bigquery._helpers': mockquerpy._helpers,
        'google.cloud.bigquery._http': mockquerpy._http,
        'google.cloud.bigquery.dataset': mockquerpy.dataset,
        'google.cloud.bigquery.table': mockquerpy.table,
        'google.cloud.bigquery.schema': mockquerpy.schema,
        'google.cloud.bigquery.external_config': mockquerpy.external_config,
        'google.cloud.bigquery.job': mockquerpy.job,
        'google.cloud.bigquery.query': mockquerpy.query,
        'google.cloud.bigquery.retry': mockquerpy.retry,
    }

    def __init__(self):
        self.sysmodules = {}

    def __enter__(self):
        for module, mock in self.mockmap.items():
            if sys.modules.get(module) is not None:
                self.sysmodules[module] = sys.modules[module]
            sys.modules[module] = mock

    def __exit__(self, exc_type, exc_val, exc_tb):
        for module in self.mockmap.keys():
            if module not in self.sysmodules.keys():
                del sys.modules[module]
            else:
                sys.modules[module] = self.sysmodules[module]
