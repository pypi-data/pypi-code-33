import pytest
from indy_common.constants import POOL_UPGRADE, ACTION, START, PACKAGE, APP_NAME, REINSTALL
from indy_node.server.request_handlers.config_req_handlers.pool_upgrade_handler import PoolUpgradeHandler
from plenum.common.constants import VERSION, TXN_PAYLOAD, TXN_PAYLOAD_DATA
from plenum.common.exceptions import InvalidClientRequest

from plenum.common.request import Request
from plenum.common.util import randomString
from plenum.test.testing_utils import FakeSomething


@pytest.fixture(scope='function')
def pool_upgrade_request():
    return Request(identifier=randomString(),
                   reqId=5,
                   operation={
                       'type': POOL_UPGRADE,
                       ACTION: START,
                       PACKAGE: 'smth'
                   })


@pytest.fixture(scope='function')
def pool_upgrade_handler():
    return PoolUpgradeHandler(None,
                              FakeSomething(),
                              FakeSomething(),
                              FakeSomething())


def test_pool_upgrade_static_validation_fails_action(pool_upgrade_handler,
                                                     pool_upgrade_request):
    pool_upgrade_request.operation[ACTION] = 'smth'
    with pytest.raises(InvalidClientRequest) as e:
        pool_upgrade_handler.static_validation(pool_upgrade_request)
    e.match('not a valid action')


def test_pool_upgrade_static_validation_fails_schedule(pool_upgrade_handler,
                                                       pool_upgrade_request):
    pool_upgrade_handler.pool_manager.getNodesServices = lambda: 1
    pool_upgrade_handler.upgrader.isScheduleValid = lambda schedule, node_srvs, force: (False, '')
    with pytest.raises(InvalidClientRequest) as e:
        pool_upgrade_handler.static_validation(pool_upgrade_request)
    e.match('not a valid schedule since')


def test_pool_upgrade_static_validation_passes(pool_upgrade_handler,
                                               pool_upgrade_request):
    pool_upgrade_handler.pool_manager.getNodesServices = lambda: 1
    pool_upgrade_handler.upgrader.isScheduleValid = lambda schedule, node_srvs, force: (True, '')
    pool_upgrade_handler.static_validation(pool_upgrade_request)


def test_pool_upgrade_dynamic_validation_fails_pckg(pool_upgrade_handler,
                                                    pool_upgrade_request):
    pool_upgrade_request.operation[PACKAGE] = ''
    with pytest.raises(InvalidClientRequest) as e:
        pool_upgrade_handler.dynamic_validation(pool_upgrade_request)
    e.match('Upgrade packet name is empty')


def test_pool_upgrade_dynamic_validation_fails_not_installed(pool_upgrade_handler,
                                                             pool_upgrade_request):
    pool_upgrade_handler.curr_pkt_info = lambda pkt: (None, None)
    with pytest.raises(InvalidClientRequest) as e:
        pool_upgrade_handler.dynamic_validation(pool_upgrade_request)
    e.match('is not installed and cannot be upgraded')


def test_pool_upgrade_dynamic_validation_fails_belong(pool_upgrade_handler,
                                                      pool_upgrade_request):
    pool_upgrade_handler.curr_pkt_info = lambda pkt: ('1.1.1', ['some_pckg'])
    with pytest.raises(InvalidClientRequest) as e:
        pool_upgrade_handler.dynamic_validation(pool_upgrade_request)
    e.match('doesn\'t belong to pool')


def test_pool_upgrade_dynamic_validation_fails_upgradable(pool_upgrade_handler,
                                                          pool_upgrade_request):
    pool_upgrade_handler.curr_pkt_info = lambda pkt: ('1.1.1', [APP_NAME])
    pool_upgrade_request.operation[VERSION] = '1.1.1'
    pool_upgrade_request.operation[REINSTALL] = False
    with pytest.raises(InvalidClientRequest) as e:
        pool_upgrade_handler.dynamic_validation(pool_upgrade_request)
    e.match('Version is not upgradable')


def test_pool_upgrade_dynamic_validation_fails_scheduled(pool_upgrade_handler,
                                                         pool_upgrade_request):
    pool_upgrade_handler.curr_pkt_info = lambda pkt: ('1.1.1', [APP_NAME])
    pool_upgrade_request.operation[VERSION] = '1.1.1'
    pool_upgrade_request.operation[REINSTALL] = True
    pool_upgrade_handler.upgrader.get_upgrade_txn = \
        lambda predicate, reverse: \
            {TXN_PAYLOAD: {TXN_PAYLOAD_DATA: {ACTION: START}}}

    with pytest.raises(InvalidClientRequest) as e:
        pool_upgrade_handler.dynamic_validation(pool_upgrade_request)
    e.match('is already scheduled')


def test_pool_upgrade_dynamic_validation_passes(pool_upgrade_handler,
                                                pool_upgrade_request):
    pool_upgrade_handler.curr_pkt_info = lambda pkt: ('1.1.1', [APP_NAME])
    pool_upgrade_request.operation[VERSION] = '1.1.1'
    pool_upgrade_request.operation[REINSTALL] = True
    pool_upgrade_handler.upgrader.get_upgrade_txn = \
        lambda predicate, reverse: \
            {TXN_PAYLOAD: {TXN_PAYLOAD_DATA: {}}}
    pool_upgrade_handler.write_request_validator.validate = lambda a, b: 0
    pool_upgrade_handler.dynamic_validation(pool_upgrade_request)
