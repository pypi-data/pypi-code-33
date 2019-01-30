"""we'll need a test sample"""

from copy import deepcopy

import boto3
from moto import mock_dynamodb2
from pynamo import Pynamo

TEST_ITEM = {
    "PrimaryKey": 'primary-key-1',
    "SecondaryKey": 'secondary-key-2',
    "data": {
        'datakey0': "",
        'datakey1': 1,
        'datakey2': 'hello',
        'datakey3': True,
        'datakey4': None,
        'datakey5': [
            1, True, 'hello'
        ]
    }
}

TEST_RETURN = {
    "PrimaryKey": 'primary-key-1',
    "SecondaryKey": 'secondary-key-2',
    "data": {
        'datakey0': None,
        'datakey1': 1,
        'datakey2': 'hello',
        'datakey3': True,
        'datakey4': None,
        'datakey5': [
            1, True, 'hello'
        ]
    }
}

TEST_KEY = {
    "PrimaryKey": 'primary-key-1',
    "SecondaryKey": 'secondary-key-2'
}

TEST_ATTRIBUTES = {
    "data": {
        "Value": {
            "datakey1": 2
        },
        "Action": "PUT"
    }
}
SESSION_INFO = {
    "aws_access_key_id": "FakeKey",
    "aws_secret_access_key": "FakeSecretKey",
    "aws_session_token": "FakeSessionToken",
    "region_name": 'us-east-1'
}

@mock_dynamodb2
def test_get_keys():
    create_test_table()
    pyn = Pynamo(**SESSION_INFO)
    table_keys = pyn.table_keys('test_table')
    assert table_keys['HASH'] == "PrimaryKey"
    assert table_keys['RANGE'] == "SecondaryKey"

@mock_dynamodb2
def test_empty_scan():
    create_test_table()
    pyn = Pynamo(**SESSION_INFO)
    response = pyn.scan('test_table')
    assert response['status'] == 200 and response['data'] == [] and response['error_msg'] is None

@mock_dynamodb2
def test_put_scan():
    create_test_table()
    pyn = Pynamo(**SESSION_INFO)
    pyn.put_item('test_table', TEST_ITEM, overwrite=True)
    scan_response = pyn.scan('test_table')
    assert scan_response['status'] == 200
    assert scan_response['data'] == [TEST_RETURN]
    assert scan_response['error_msg'] is None

@mock_dynamodb2
def test_put_get():
    create_test_table()
    pyn = Pynamo(**SESSION_INFO)
    pyn.put_item('test_table', TEST_ITEM, overwrite=True)
    get_response = pyn.get_item('test_table', TEST_KEY)
    assert get_response['status'] == 200
    assert get_response['data'] == TEST_RETURN
    assert get_response['error_msg'] is None

@mock_dynamodb2
def test_put_delete():
    create_test_table()
    pyn = Pynamo(**SESSION_INFO)
    pyn.put_item('test_table', TEST_ITEM)
    pyn.delete_item('test_table', TEST_KEY)
    scan_response = pyn.scan('test_table')
    assert scan_response['status'] == 200
    assert scan_response['data'] == []
    assert scan_response['error_msg'] is None

@mock_dynamodb2
def test_put_update_get():
    create_test_table()
    pyn = Pynamo(**SESSION_INFO)
    pyn.put_item('test_table', TEST_ITEM)
    pyn.update_item('test_table', TEST_KEY, TEST_ATTRIBUTES)
    get_response = pyn.get_item('test_table', TEST_KEY)

    predicted_item = deepcopy(TEST_RETURN)
    predicted_item['data'] = {"datakey1": 2}
    assert get_response['data'] == predicted_item

@mock_dynamodb2
def test_rewrite_same_key():
    create_simple_table()
    pyn = Pynamo(**SESSION_INFO)
    pyn.put_item('simple_table', TEST_ITEM)

    new_item = deepcopy(TEST_ITEM)
    new_item['data'] = ["Hi"]

    new_return = deepcopy(TEST_RETURN)
    new_return['data'] = ["Hi"]

    pyn.replace_item('simple_table', TEST_KEY, new_item)
    get_response = pyn.get_item('simple_table', TEST_KEY)

    assert get_response['data'] == new_return
    assert len(pyn.scan('simple_table')['data']) == 1

@mock_dynamodb2
def test_rewrite_diff_prim_key():
    create_simple_table()
    pyn = Pynamo(**SESSION_INFO)
    pyn.put_item('simple_table', TEST_ITEM)

    new_item = deepcopy(TEST_ITEM)
    new_item['PrimaryKey'] = "NewKey"

    new_key = deepcopy(TEST_KEY)
    new_key['PrimaryKey'] = "NewKey"
    new_key.pop('SecondaryKey', None)

    new_return = deepcopy(TEST_RETURN)
    new_return['PrimaryKey'] = "NewKey"

    pyn.replace_item('simple_table', TEST_KEY, new_item)
    get_response = pyn.get_item('simple_table', new_key)

    assert get_response['data'] == new_return
    assert len(pyn.scan('simple_table')['data']) == 1

@mock_dynamodb2
def test_rewrite_diff_both_key():
    create_simple_table()
    pyn = Pynamo(**SESSION_INFO)
    pyn.put_item('simple_table', TEST_ITEM)

    new_item = deepcopy(TEST_ITEM)
    new_item['PrimaryKey'] = "NewPrimary"
    new_item['SecondaryKey'] = "NewSecondary"

    new_key = deepcopy(TEST_KEY)
    new_key['PrimaryKey'] = "NewPrimary"
    new_key.pop('SecondaryKey', None)

    new_return = deepcopy(TEST_RETURN)
    new_return['PrimaryKey'] = "NewPrimary"
    new_return['SecondaryKey'] = "NewSecondary"

    pyn.replace_item('simple_table', TEST_KEY, new_return)
    get_response = pyn.get_item('simple_table', new_key)

    assert get_response['data'] == new_return
    assert len(pyn.scan('simple_table')['data']) == 1

@mock_dynamodb2
def test_get_key_values():
    create_test_table()
    pyn = Pynamo(**SESSION_INFO)
    pyn.put_item('test_table', TEST_ITEM, overwrite=True)
    key_values = pyn.table_key_values('test_table')['data']
    assert key_values[0]["PrimaryKey"] == "primary-key-1"
    assert key_values[0]["SecondaryKey"] == "secondary-key-2"
    assert len(key_values) == 1

@mock_dynamodb2
def test_table_copy():
    create_test_table()
    create_simple_table()
    pyn = Pynamo(**SESSION_INFO)
    pyn.put_item('simple_table', TEST_ITEM, overwrite=True)
    pyn.copy_table('simple_table', 'test_table')
    get_response = pyn.get_item('test_table', TEST_KEY)

    assert get_response['status'] == 200
    assert get_response['data'] == TEST_RETURN
    assert get_response['error_msg'] is None




# @mock_dynamodb2
# def test_get_key_values_no_range():
#     create_simple_table()
#     pyn = Pynamo(**SESSION_INFO)
#     pyn.put_item('test_table', TEST_ITEM)
#     key_values = pyn.table_key_values('test_table')['data']
#     new_key = deepcopy(TEST_KEY)
#     new_key.pop('SecondaryKey', None)
#     assert key_values[0] == new_key
#     assert len(key_values) == 1

# add back when moto fixes its shit
# @mock_dynamodb2
# def test_rewrite_existing_key():
#     create_simple_table()
#     pyn = Pynamo(**SESSION_INFO)

#     new_item = deepcopy(TEST_ITEM)
#     new_item['PrimaryKey'] = "NewPrimary"
#     new_item['SecondaryKey'] = "NewSecondary"

#     old_key = deepcopy(TEST_KEY)
#     old_key.pop('SecondaryKey', None)
#     new_key = deepcopy(TEST_KEY)
#     new_key['PrimaryKey'] = "NewPrimary"
#     new_key.pop('SecondaryKey', None)

#     pyn.put_item('test_table', TEST_ITEM)
#     pyn.put_item('test_table', new_item)
#     assert len(pyn.scan('test_table')['data']) == 2

#     rewrite_response = pyn.replace_item('test_table', old_key, new_item)

#     assert rewrite_response['status'] == 403
#     assert rewrite_response['error_msg'] == "Entry exists already with chosen Key."

#     get_response = pyn.get_item('test_table', old_key)
#     assert get_response['data'] == TEST_RETURN
#     assert len(pyn.scan('test_table')['data']) == 2

@mock_dynamodb2
def test_error_no_table():
    create_test_table()
    error_codes = [403, 404, 500]
    pyn = Pynamo(**SESSION_INFO)
    if pyn.scan('bad-table')['status'] not in error_codes:
        assert False
    if pyn.get_item('bad-table', TEST_KEY)['status'] not in error_codes:
        assert False
    if pyn.put_item('bad-table', TEST_ITEM)['status'] not in error_codes:
        assert False
    if pyn.delete_item('bad-table', TEST_KEY)['status'] not in error_codes:
        assert False
    if pyn.update_item('bad-table', TEST_KEY, TEST_ATTRIBUTES)['status'] not in error_codes:
        assert False
    assert True

@mock_dynamodb2
def test_existing_session():
    create_test_table()
    session = boto3.session.Session(**SESSION_INFO)
    response = Pynamo(boto_session=session).scan('test_table')
    assert response['status'] == 200 and response['data'] == [] and response['error_msg'] is None


def create_test_table():
    pyn = Pynamo(**SESSION_INFO)
    pyn.client.create_table(
        AttributeDefinitions=[
            {
                'AttributeName': 'PrimaryKey',
                'AttributeType': 'S'
            },
            {
                'AttributeName': 'SecondaryKey',
                'AttributeType': 'S'
            }
        ],
        TableName='test_table',
        KeySchema=[
            {
                'AttributeName': 'PrimaryKey',
                'KeyType': 'HASH'
            },
            {
                'AttributeName': 'SecondaryKey',
                'KeyType': 'RANGE'
            },
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 10,
            'WriteCapacityUnits': 10
        }
    )

def create_simple_table():
    pyn = Pynamo(**SESSION_INFO)
    pyn.client.create_table(
        AttributeDefinitions=[
            {
                'AttributeName': 'PrimaryKey',
                'AttributeType': 'S'
            }
        ],
        TableName='simple_table',
        KeySchema=[
            {
                'AttributeName': 'PrimaryKey',
                'KeyType': 'HASH'
            }
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 10,
            'WriteCapacityUnits': 10
        }
    )