from logging import getLogger

from plenum.common.startable import Mode
from plenum.server.node import Node
from plenum.test import waits
from plenum.test.delayers import cr_delay, cs_delay
from plenum.test.pool_transactions.helper import \
    disconnect_node_and_ensure_disconnected
from plenum.test.helper import sdk_send_random_and_check, assertExp
from plenum.test.node_catchup.helper import waitNodeDataEquality
from plenum.test.stasher import delay_rules
from plenum.test.test_node import checkNodesConnected
from plenum.test.view_change.helper import start_stopped_node
from stp_core.loop.eventually import eventually

logger = getLogger()


def test_3pc_while_catchup(tdir, tconf,
                           looper,
                           testNodeClass,
                           txnPoolNodeSet,
                           sdk_pool_handle,
                           sdk_wallet_client,
                           allPluginsPath):
    # Prepare nodes
    lagging_node = txnPoolNodeSet[-1]
    rest_nodes = txnPoolNodeSet[:-1]

    # Check that requests executed well
    sdk_send_random_and_check(looper, txnPoolNodeSet, sdk_pool_handle,
                              sdk_wallet_client, 10)

    # Stop one node
    waitNodeDataEquality(looper, lagging_node, *rest_nodes)
    disconnect_node_and_ensure_disconnected(looper,
                                            txnPoolNodeSet,
                                            lagging_node,
                                            stopNode=True)
    looper.removeProdable(lagging_node)

    # Send more requests to active nodes
    sdk_send_random_and_check(looper, txnPoolNodeSet, sdk_pool_handle,
                              sdk_wallet_client, 10)
    waitNodeDataEquality(looper, *rest_nodes)

    # Restart stopped node and wait for successful catch up
    lagging_node = start_stopped_node(lagging_node,
                                      looper,
                                      tconf,
                                      tdir,
                                      allPluginsPath,
                                      start=False,
                                      )

    initial_all_ledgers_caught_up = lagging_node.spylog.count(Node.allLedgersCaughtUp)
    assert all(replica.stasher.num_stashed_catchup == 0 for inst_id, replica in lagging_node.replicas.items())
    # delay CurrentState to avoid Primary Propagation (since it will lead to more catch-ups not needed in this test).
    with delay_rules(lagging_node.nodeIbStasher, cs_delay()):
        with delay_rules(lagging_node.nodeIbStasher, cr_delay()):
            looper.add(lagging_node)
            txnPoolNodeSet[-1] = lagging_node
            looper.run(checkNodesConnected(txnPoolNodeSet))

            # wait till we got catchup replies for messages missed while the node was offline,
            # so that now qwe can order more messages, and they will not be caught up, but stashed
            looper.run(
                eventually(lambda: assertExp(len(lagging_node.nodeIbStasher.delayeds) >= 3), retryWait=1,
                           timeout=60))

            # make sure that more requests are being ordered while catch-up is in progress
            sdk_send_random_and_check(looper, txnPoolNodeSet, sdk_pool_handle,
                                      sdk_wallet_client, 10)

            assert lagging_node.mode == Mode.syncing
            assert all(replica.stasher.num_stashed_catchup > 0 for inst_id, replica in lagging_node.replicas.items())

        # check that the catch-up is finished
        looper.run(
            eventually(
                lambda: assertExp(lagging_node.mode == Mode.participating), retryWait=1,
                timeout=waits.expectedPoolCatchupTime(len(txnPoolNodeSet))
            )
        )
        looper.run(
            eventually(
                lambda: assertExp(
                    lagging_node.spylog.count(Node.allLedgersCaughtUp) == initial_all_ledgers_caught_up + 1)
            )
        )
        # check that the node was able to order requests stashed during catch-up
        waitNodeDataEquality(looper, *txnPoolNodeSet, customTimeout=5)
        assert all(replica.stasher.num_stashed_catchup == 0 for inst_id, replica in lagging_node.replicas.items())
