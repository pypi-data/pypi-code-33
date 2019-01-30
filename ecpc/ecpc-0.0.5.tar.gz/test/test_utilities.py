import pytest
from ecpc import utilities
from ecpc.configuration import ECPC_DIR, config


def test_valid_selection():
    utilities.valid_selection('eu-west-1', 't2.small')
    with pytest.raises(ValueError):
        result = utilities.valid_selection('xxxx', 't2.small')
    with pytest.raises(ValueError):
        result = utilities.valid_selection('eu-west-1', 'xxxx')
    
def test_nonexistent_uid():
    region = 'eu-west-1'
    uid = 'ABC123'
    assert utilities.get_instance_id(region, uid) is None
    assert utilities.get_security_group_id(region, uid) is None
    assert utilities.get_key_pair(region, uid) is None
    assert utilities.get_pem_file(ECPC_DIR, uid) is None

def test_security_group_functions():
    region = 'eu-west-1'
    uid = 'ABC123'
    result = utilities.create_security_group(region, uid)
    assert utilities.get_security_group_id(region, uid) is not None
    utilities.delete_security_group(region, uid)
    assert utilities.get_security_group_id(region, uid) is None
    
def test_key_pair_functions():
    region = 'eu-west-1'
    uid = 'ABC123'
    key_material = utilities.create_key_pair(region, uid)
    result = utilities.create_pem_file(ECPC_DIR, uid, key_material)
    assert utilities.get_key_pair(region, uid) is not None
    assert utilities.get_pem_file(ECPC_DIR, uid) is not None
    utilities.delete_key_pair(region, uid)
    utilities.delete_pem_file(ECPC_DIR, uid)
    assert utilities.get_key_pair(region, uid) is None
    assert utilities.get_pem_file(ECPC_DIR, uid) is None
    
def test_select_ami():
    region = 'eu-west-1'
    image_id = utilities.select_ami(region, config['ami_description_includes'],
                                    config['ami_description_excludes'])
    assert image_id is not None
