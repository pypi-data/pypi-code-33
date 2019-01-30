import pytest
from ecpc import data

def test_init():
    database = data.database

def test_data_add():
    database = data.database
    database.add_entry('ABC123')
    entry = database.get('ABC123')
    assert entry['uid'] == 'ABC123'

def test_data_modify():
    database = data.database
    mods = {'test_field': 123}
    database.update('ABC123', mods)
    entry = database.get('ABC123')
    assert 'test_field' in entry
    assert entry['test_field'] == 123
    assert 'uid' in entry

def test_data_list():
    database = data.database
    database.add_entry('DEF456')
    uids = database.ids()
    assert 'ABC123' in uids
    assert 'DEF456' in uids
    
def test_data_remove():
    database = data.database
    database.remove_entry('ABC123')
    uids = database.ids()
    assert not 'ABC123' in uids
    with pytest.raises(IndexError):
        database.remove_entry('XYZ789')
    for uid in database.ids():
        database.remove_entry(uid) 
