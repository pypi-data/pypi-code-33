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

metric_type_schema = {
    'type': 'string',
    'enum': ['Numeric', 'Discrete']
}

trigger_actions_schema = {
    'type': 'array',
    'items': {
        'type': 'string',
        'enum': ['Transmit', 'Log']
    }
}

numeric_triggers_schema = {
    'type': 'array',
    'items': {
        'type': 'object',
        'properties': {
            'Name': {'type': 'string'},
            'Value': {'type': 'number'},
            'DirectionOfCrossing': {
                'type': 'string',
                'enum': ['Increasing', 'Decreasing']
            },
            'DwellTimMsec': {'type': 'number'},
            'Severity': {'type': 'string'}
        },
        'additionalProperties': False
    }
}

discrete_trigger_condition_schema = {
    'type': 'string',
    'enum': ['Specified', 'Changed']
}

discrete_triggers_schema = {
    'type': 'array',
    'items': {
        'type': 'object',
        'properties': {
            'Name': {'type': 'string'},
            'Value': {'type': 'string'},
            'DwellTimMsec': {'type': 'number'},
            'Severity': {'type': 'string'}
        },
        'additionalProperties': False
    }
}

status_schema = {
    'type': 'object',
    'properties': {
        'State': {'type': 'string'},
        'Health': {'type': 'string'},
        'HealthRollup': {'type': 'string'}
    },
    'additionalProperties': False
}

wildcards_schema = {
    'type': 'array',
    'items': {
        'type': 'object',
        'properties': {
            'Name': {'type': 'string'},
            'Keys': {'type': 'string'}
        },
        'additionalProperties': False
    }
}

metric_properties_schema = {
    'type': 'array',
    'items': {
        'type': 'string'
    }
}
