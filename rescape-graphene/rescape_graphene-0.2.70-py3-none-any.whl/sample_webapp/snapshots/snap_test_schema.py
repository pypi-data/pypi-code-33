# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['TestSchema::test_create_foo 1'] = {
    'data': {
        'example': 1.5,
        'friend': {
            'firstName': 'Simba',
            'isActive': True,
            'isStaff': True,
            'lastName': 'The Lion',
            'username': 'lion'
        }
    },
    'geojson': {
        'copyright': '2018',
        'features': [
            {
                'geometry': {
                    'coordinates': [
                        [
                            [
                                49.5294835476,
                                2.51357303225
                            ],
                            [
                                51.4750237087,
                                2.51357303225
                            ],
                            [
                                51.4750237087,
                                6.15665815596
                            ],
                            [
                                49.5294835476,
                                6.15665815596
                            ],
                            [
                                49.5294835476,
                                2.51357303225
                            ]
                        ]
                    ],
                    'type': 'Polygon'
                },
                'type': 'Feature'
            },
            {
                'geometry': {
                    'coordinates': [
                        5.7398201,
                        58.970167
                    ],
                    'type': 'Point'
                },
                'properties': {
                    'type': 'node'
                },
                'type': 'Feature'
            }
        ],
        'generator': 'Open Street Map',
        'type': 'FeatureCollection'
    },
    'key': 'luxembourg',
    'name': 'Luxembourg',
    'user': {
        'firstName': 'Simba',
        'isActive': True,
        'isStaff': True,
        'lastName': 'The Lion',
        'username': 'lion'
    }
}

snapshots['TestSchema::test_create_user 1'] = {
    'firstName': 'T',
    'isActive': True,
    'lastName': 'Rex',
    'username': 'dino'
}

snapshots['TestSchema::test_update 1'] = {
    'firstName': 'Al',
    'isActive': True,
    'lastName': 'Lissaurus',
    'username': 'dino'
}
