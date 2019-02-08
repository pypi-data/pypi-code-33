# Copyright (c) 2019 Intel, Corp.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

report_definition_req_schema = {
    'type': 'object',
    'properties': {
        'Name': {'type': 'string'},
        'Schedule': {
            'type': 'object',
            'properties': {
                'RecurrenceInterval': {'type': 'string'},
            }
        },
        'MetricReportType': {
            'type': 'string',
            'enum': ['OnChange', 'Periodic', 'OnRequests']
        },
        'CollectionTimeScope': {
            'type': 'string',
            'enum': ['Point', 'Interval', 'StartupInterval']
        },
        'ReportActions': {
            'type': 'array',
            'items': {
                'type': 'string',
                'enum': ['Transmit', 'Log']
            }
        },
        'MetricReport': {
            'type': 'object',
            'properties': {
                '@odata.id': {'type': 'string'}
            }
        },
        'Status': {
            'type': 'object',
            'properties': {
                'State': {'type': 'string'},
                'Health': {'type': 'string'},
                'HealthRollup': {'type': 'string'}
            }
        },
        'MetricProperties': {
            'type': 'array',
            'items': {'type': 'string'}
        }
    },
    'additionalProperties': False
}
