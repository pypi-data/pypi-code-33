# -*- coding: utf-8 -*-
"""
Polarion docstring fields info.
"""


POLARION_FIELDS = {
    'assignee': '',
    'initialEstimate': '',
    'caseimportance': 'high',
    'caselevel': 'component',
    'caseposneg': 'positive',
    'caseautomation': 'automated',
    'testtype': 'functional',
    'casecomponent': '-',
    'subtype1': '-',
    'subtype2': '-',
    'tags': '',
    'setup': '',
    'teardown': '',
    'description': '',
    'linkedWorkItems': '',
    'testSteps': '',
    'expectedResults': '',
    'title': '',
}

# fields that are not present in Polarion but are added by us
ADDED_FIELDS = (
    'work_item_id',
)

KNOWN_FIELDS = tuple(POLARION_FIELDS) + ADDED_FIELDS


CUSTOM_FIELDS = (
    'caseautomation',
    'caseimportance',
    'caselevel',
    'caseposneg',
    'testtype',
    'casecomponent',
    'subtype1',
    'subtype2',
    'tags',
    'setup',
    'teardown',
)

# fields valid only for manual test cases
MANUAL_ONLY_FIELDS = (
    'title',
    'setup',
    'teardown',
    'testSteps',
    'expectedResults',
)

# fields that correspond to pytest markers
MARKERS_FIELDS = {
    'caselevel': 'tier',
    'caseautomation': 'manual',
    'linkedWorkItems': 'requirements',
}

# fields that need to be present in every docstring
REQUIRED_FIELDS = (
    'assignee',
    'initialEstimate',
)

CASELEVELS = {
    'component': '0',
    'integration': '1',
    'system': '2',
    'acceptance': '3',
}

# mapping of component names to their internal representation
CASECOMPONENT_MAP = {
    'Cloud': 'cloud',
    'Infra': 'infra',
    'Services': 'services',
    'Control': 'control',
    'Automate': 'automate',
    'Configuration': 'config',
    'Appliance': 'appl',
    'C&U': 'candu',
    'Reporting': 'report',
    'SmartState': 'smartst',
    'Provisioning': 'prov',
    'SelfServiceUI': 'ssui',
    'Stack': 'stack',
    'UI': 'web_ui',
    'Optimize': 'optimize',
    'Ansible': 'ansible',
}

CASEIMPORTANCE_VALID = (
    'critical',
    'high',
    'medium',
    'low',
)

CASECOMPONENT_VALID = (
    'cloud',
    'infra',
    'services',
    'control',
    'automate',
    'config',
    'appl',
    'candu',
    'report',
    'smartst',
    'prov',
    'ssui',
    'stack',
    'web_ui',
    'optimize',
    'ansible',
)

CASEPOSNEG_VALID = (
    'positive',
    'negative',
)

TESTTYPE_VALID = (
    'functional',
    'nonfunctional',
    'structural',
    'integration',
    'upgrade',
)

VALID_VALUES = {
    'caseimportance': CASEIMPORTANCE_VALID,
    'caseposneg': CASEPOSNEG_VALID,
    'testtype': TESTTYPE_VALID,
    'casecomponent': CASECOMPONENT_VALID,
}
