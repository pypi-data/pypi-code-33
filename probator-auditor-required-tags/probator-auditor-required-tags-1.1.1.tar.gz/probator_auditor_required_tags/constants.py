from collections import namedtuple
from dataclasses import dataclass

from probator.plugins.types.resources import BaseResource
from probator_auditor_required_tags.types import RequiredTagsIssue

DEFAULT_ALERT_CONFIG = {
    'global': {
        'actions': [
            {
                'name': 'alert:1',
                'age': 'now',
                'action': 'alert',
                'order': 0,
            },
            {
                'name': 'alert:2',
                'age': '3 weeks',
                'action': 'alert',
                'order': 1,
            },
            {
                'name': 'alert:3',
                'age': '3 weeks, 6 days',
                'action': 'alert',
                'order': 2,
            },
            {
                'name': 'stop',
                'age': '4 weeks',
                'action': 'stop',
                'order': 3,
            },
            {
                'name': 'remove',
                'age': '12 weeks',
                'action': 'remove',
                'order': 4,
            }
        ],
        'requiredTags': {
            'Name': None,
            'owner': r'([a-zA-Z0-9._%+-]+[^+]@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})'
        },
        'extraConfig': {}
    },
    'aws_ec2_instance': {
        'requiredTags': {
            'ssmEnabled': r'^(true|false)$'
        }
    }
}
DEFAULT_AUDIT_SCOPES = {
    'enabled': [],
    'available': [],
    'max_items': 0,
    'min_items': 0
}


@dataclass
class IssueAction(object):
    issue: RequiredTagsIssue
    resource: BaseResource
    alert: bool = True


ResourceTypeIssues = namedtuple('ResourceTypeIssues', ('new', 'updated'))
