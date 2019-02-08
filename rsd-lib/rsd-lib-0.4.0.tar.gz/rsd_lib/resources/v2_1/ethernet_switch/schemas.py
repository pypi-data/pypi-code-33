# Copyright 2018 99cloud, Inc.
# All Rights Reserved.
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

vlan_network_interface_req_schema = {
    'type': 'object',
    'properties': {
        'VLANId': {'type': 'number'},
        'VLANEnable': {'type': 'boolean'},
        'Oem': {
            'type': 'object',
            'properties': {
                'Intel_RackScale': {
                    'type': 'object',
                    'properties': {
                        'Tagged': {'type': 'boolean'}
                    },
                    'required': ['Tagged']
                }
            },
            'required': ['Intel_RackScale']
        }
    },
    'required': [
        'VLANId',
        'VLANEnable',
        'Oem'
    ],
    'additionalProperties': False
}

acl_rule_req_schema = {
    'type': 'object',
    'oneOf': [
        {
            'properties': {
                'Action': {'enum': ['Forward']}
            },
            'required': ['ForwardMirrorInterface']
        },
        {
            'properties': {
                'Action': {'enum': ['Mirror']}
            },
            'required': ['ForwardMirrorInterface',
                         'MirrorPortRegion', 'MirrorType']
        },
        {
            'properties': {
                'Action': {'enum': ['Permit', 'Deny']}
            }
        }
    ],
    'properties': {
        'RuleId': {'type': 'number'},
        'Action': {
            'type': 'string',
            'enum': ['Permit', 'Deny', 'Forward', 'Mirror']
        },
        'ForwardMirrorInterface': {
            'type': 'object',
            'properties': {
                '@odata.id': {
                    'type': 'string'
                }
            },
            'required': ['@odata.id']
        },
        'MirrorPortRegion': {
            'type': 'array',
            'items': {
                'type': 'object',
                'properties': {
                    '@odata.id': {
                        'type': 'string'
                    }
                },
                'required': ['@odata.id']
            }
        },
        'MirrorType': {
            'type': 'string',
            'enum': ['Egress', 'Ingress', 'Bidirectional', 'Redirect']
        },
        'Condition': {
            'type': 'object',
            'properties': {
                'IPSource': {
                    'type': 'object',
                    'properties': {
                        'IPv4Addresses': {'type': 'string'},
                        'Mask': {'type': ['string', 'null']}
                    },
                    'required': ['IPv4Address']
                },
                'IPDestination': {
                    'type': 'object',
                    'properties': {
                        'IPv4Address': {'type': 'string'},
                        'Mask': {'type': ['string', 'null']}
                    },
                    'required': ['IPv4Address']
                },
                'MACSource': {
                    'type': 'object',
                    'properties': {
                        'MACAddress': {'type': 'string'},
                        'Mask': {'type': ['string', 'null']}
                    },
                    'required': ['MACAddress']
                },
                'MACDestination': {
                    'type': 'object',
                    'properties': {
                        'MACAddress': {'type': 'string'},
                        'Mask': {'type': ['string', 'null']}
                    },
                    'required': ['MACAddress']
                },
                'VLANId': {
                    'type': 'object',
                    'properties': {
                        'Id': {'type': 'number'},
                        'Mask': {'type': ['number', 'null']}
                    },
                    'required': ['Id']
                },
                'L4SourcePort': {
                    'type': 'object',
                    'properties': {
                        'Port': {'type': 'number'},
                        'Mask': {'type': ['number', 'null']}
                    },
                    'required': ['Port']
                },
                'L4DestinationPort': {
                    'type': 'object',
                    'properties': {
                        'Port': {'type': 'number'},
                        'Mask': {'type': ['number', 'null']}
                    },
                    'required': ['Port']
                },
                'L4Protocol': {'type': ['number', 'null']}
            }
        },
    },
    'required': ['Action', 'Condition'],
    'additionalProperties': False
}
