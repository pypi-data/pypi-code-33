"""tests for checking filter_data method"""

import os
import json
from copy import deepcopy
import pytest

from parski.filter_data import FilterData

DIR_PATH = os.path.dirname(os.path.realpath(__file__))

### standardize inputs

def test_standard_search_dict():
    search_input = {
        "Alias": "corp-prod",
        "Tags": [
            {
                "Key": "Name"
            }
        ]
    }
    search_output = [[
        {"path": ["Alias"], "value": "corp-prod"},
        {"path": ["Tags", 0, "Key"], "value": "Name"},
    ]]

    options = {"search_input": search_input}
    filter_object = FilterData(options)
    filter_object._standardize_input()
    assert filter_object.search_input == search_output

def test_standard_search_dict_list():
    search_input = [{"Alias": "corp-prod",},
        {"Tags": [
            {"Key": "Name"}
        ]}
    ]
    search_output = [
        [{"path": ["Alias"], "value": "corp-prod"}],
        [{"path": ["Tags", 0, "Key"], "value": "Name"}],
    ]

    options = {"search_input": search_input}
    filter_object = FilterData(options)
    filter_object._standardize_input()
    assert filter_object.search_input == search_output

def test_standard_search_path():
    search_input = {"path": [2, "Alias"], "value": "corp-prod"}
    search_output = [[
        {"path": ["Alias"], "value": "corp-prod"}
    ]]

    options = {"search_input": search_input}
    filter_object = FilterData(options)
    filter_object._standardize_input()
    assert filter_object.search_input == search_output

def test_standard_search_path_list():
    search_input = [
        {"path": [1, "Alias"], "value": "digital-public"},
        {"path": [2, "Alias"], "value": "corp-prod"},
        {"path": [1, "Alias"], "value": "trans-prod"},
        {"path": ["Alias"], "value": "trans-preprod"}
    ]
    search_output = [
        [
            {"path": ["Alias"], "value": "digital-public"},
            {"path": ["Alias"], "value": "trans-prod"}
        ],
        [{"path": ["Alias"], "value": "corp-prod"}],
        [{"path": ["Alias"], "value": "trans-preprod"}]
    ]

    options = {"search_input": search_input}
    filter_object = FilterData(options)
    filter_object._standardize_input()
    assert filter_object.search_input == search_output

def test_standard_bad_type():
    options = {"search_input": 5}
    filter_object = FilterData(options)
    try:
        filter_object._standardize_input()
        assert False
    except TypeError:
        assert True

def test_standard_bad_combo():
    search_input = [
        {"Alias": "corp-prod"},
        {"path": ["Alias"], "value": "corp-preprod"}
    ]
    options = {"search_input": search_input}
    filter_object = FilterData(options)
    try:
        filter_object._standardize_input()
        assert False
    except TypeError:
        assert True


### value check ###

EMPTY_METRICS = {
    'missing_keys': {
        'total': 0
    },
    'regex_errors': {
        'total': 0
    },
    'searches': 0,
    'search_time': 0
}

EMPTY_OPTIONS = {
    "search_input": {}
}

def test_value_null():
    filter_object = FilterData(EMPTY_OPTIONS)
    entry = "None"
    value = "Null"
    assert filter_object._value_check(entry, value)

@pytest.mark.skip(reason="can't find something to cause a regex error")
def test_value_regex_error():
    filter_object = FilterData(EMPTY_OPTIONS)
    entry = "None"
    value = "Null"
    assert filter_object._value_check(entry, value)

def test_value_pass():
    filter_object = FilterData(EMPTY_OPTIONS)
    checks = [
        ("", ".*"),
        (543, "43$"),
        ("ban4na", "n[0-9]n")
    ]
    for check in checks:
        assert filter_object._value_check(check[0], check[1])

def test_value_fail():
    filter_object = FilterData(EMPTY_OPTIONS)
    checks = [
        (432, "5"),
        (5432, "43$"),
        ("ban4na", "n[0-3]n")
    ]
    for check in checks:
        assert not filter_object._value_check(check[0], check[1])

def test_entry_pass():
    filter_object = FilterData(EMPTY_OPTIONS)
    filter_object.metrics = deepcopy(EMPTY_METRICS)
    entry = "5"
    path_list = [{"path": [], "value": "5"}]
    assert (filter_object._entry_filter(entry, path_list)
            and filter_object.metrics['regex_errors']['total'] == 0
            and filter_object.metrics['missing_keys']['total'] == 0)

def test_entry_fail():
    filter_object = FilterData(EMPTY_OPTIONS)
    filter_object.metrics = deepcopy(EMPTY_METRICS)
    entry = "6"
    path_list = [{"path": [], "value": "5"}]
    assert (not filter_object._entry_filter(entry, path_list)
            and filter_object.metrics['regex_errors']['total'] == 0
            and filter_object.metrics['missing_keys']['total'] == 0)

def test_deep_entry_pass():
    filter_object = FilterData(EMPTY_OPTIONS)
    filter_object.metrics = deepcopy(EMPTY_METRICS)
    entry = {"test_key": "5"}
    path_list = [{"path": ["test_key"], "value": "5"}]
    assert (filter_object._entry_filter(entry, path_list)
            and filter_object.metrics['regex_errors']['total'] == 0
            and filter_object.metrics['missing_keys']['total'] == 0)

def test_deep_entry_fail():
    filter_object = FilterData(EMPTY_OPTIONS)
    filter_object.metrics = deepcopy(EMPTY_METRICS)
    entry = {"test_key": "6"}
    path_list = [{"path": ["test_key"], "value": "5"}]
    assert (not filter_object._entry_filter(entry, path_list)
            and filter_object.metrics['regex_errors']['total'] == 0
            and filter_object.metrics['missing_keys']['total'] == 0)

def test_entry_missing_key():
    filter_object = FilterData(EMPTY_OPTIONS)
    filter_object.metrics = deepcopy(EMPTY_METRICS)
    entry = {"missing_key": "5"}
    path_list = [{"path": ["test_key"], "value": "5"}]
    assert (not filter_object._entry_filter(entry, path_list)
            and filter_object.metrics['regex_errors']['total'] == 0
            and filter_object.metrics['missing_keys']['total'] == 1)


### Functional Tests ###

def test_filter_data():
    with open(os.path.join(DIR_PATH, "instances.json"), "r") as instances_file:
        test_data = json.loads(instances_file.read())
        #test_data length = 23
        instances_file.close()

    generic_options = {
        'data': test_data,
        'max_results': 100000,
        'silent': False
    }

    filter_dicts = [
        #simple check
        ({'Alias': 'digital-public'}, 11),

        #LaunchTime check
        ({'LaunchTime': '(2017/06/05)(3000/03/05)'}, 13),

        #AND check
        ({'Alias': 'digital-public', 'LaunchTime': '(2017/06/05)(3000/03/05)'}, 8),

        #Group sorting
        ({'Tags': [{'Key': 'Name', 'Value': 'Bastion'}, {'Key': 'csadmin', 'Value': 'csadmin'}]}, 2),
        ({'Tags': [{'Key': 'Name', 'Value': 'csadmin'}, {'Key': 'csadmin', 'Value': 'Bastion'}]}, 0),

        #Deep Search
        ({"Subkey1": {"Subkey2": [{"Subkey3": 4}]}}, 1),
        ({"Subkey1": {"Subkey2": [{"Subkey3": 2}]}}, 0),

        #OR Check
        ([{'Alias': 'digital-public'}, {'LaunchTime': '(2017/06/05)(3000/03/05)'}], 16),

        #List string Check
        ({'Action': [".*"]}, 4),
        ({'Action': ["build"]}, 4),
        ({'Action': ["codestar"]}, 1),
        ({'Action': ["codestar", "cur"]}, 0),
        ({'Action': ["codestar", "build"]}, 1)

    ]
    filter_options = deepcopy(generic_options)
    for item in filter_dicts:
        filter_options['search_input'] = item[0]
        filter_object = FilterData(filter_options)

        filter_object.filter_data()
        assert len(filter_object.results) == item[1]
