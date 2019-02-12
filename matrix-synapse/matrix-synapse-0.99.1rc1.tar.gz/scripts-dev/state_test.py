from twisted.internet import reactor, defer

from synapse.api.constants import RoomVersions
from synapse.server import HomeServer
from synapse.config.homeserver import HomeServerConfig
from synapse.config._base import ConfigError
from synapse.config.logger import setup_logging
from synapse.storage.engines import create_engine
from synapse.replication.slave.storage.events import SlavedEventStore

import synapse.events

import sys
import logging


logger = logging.getLogger("main")


class Server(HomeServer):
    def setup(self):
        logger.info("Setting up.")
        self.datastore = SlavedEventStore(self.get_db_conn(), self)
        logger.info("Finished setting up.")


def make_hs():
    try:
        config = HomeServerConfig.load_config(
            "Synapse synchrotron", sys.argv[1:]
        )
    except ConfigError as e:
        sys.stderr.write("\n" + e.message + "\n")
        sys.exit(1)

    setup_logging(config, use_worker_options=True)

    synapse.events.USE_FROZEN_DICTS = False

    database_engine = create_engine(config.database_config)

    hs = Server(
        config.server_name,
        db_config=config.database_config,
        config=config,
        version_string="Synapse/TestScript",
        database_engine=database_engine,
    )

    hs.setup()

    return hs


def get_group_list(store, room_id):
    sql = """
        SELECT sort(array_agg(state_group::int)) FROM stream_ordering_to_exterm
        NATURAL JOIN event_to_state_groups
        WHERE room_id = ?
        GROUP BY stream_ordering
        ORDER BY stream_ordering ASC
    """

    def func(txn):
        txn.execute(sql, (room_id,))

        prev = None
        result = []
        for groups, in txn:
            groups = set(groups)
            if groups == prev:
                continue

            prev = groups
            result.append(groups)

        return result

    return store.runInteraction("get_group_list", func)


class Resolver(object):
    def __init__(self, hs):
        self.store = hs.get_datastore()
        self.state = hs.get_state_resolution_handler()

        self.prev_groups = None
        self.prev_state = None
        self.prev_conflicted_state = None

    @defer.inlineCallbacks
    def calculate_state(self, room_id, groups):
        def get_events(ev_ids):
            return self.store.get_events(
                ev_ids, get_prev_content=False, check_redacted=False,
            )

        new_state = None
        if self.prev_groups:
            same_groups = self.prev_groups & groups

            replaced = self.prev_groups - groups
            new = groups - self.prev_groups

            missing_prevs = set(replaced)

            changed_groups = []
            all_matched = True
            for group in new:
                prev_group, delta_ids = yield self.store.get_state_group_delta(group)
                if prev_group in replaced:
                    changed_groups.append((prev_group, group, delta_ids))
                    missing_prevs.discard(prev_group)
                    continue
                all_matched = False
                break

            if all_matched and not missing_prevs:
                logger.info("Calculating delta: %s -> %s", list(self.prev_groups), list(groups))
                state_delta, self.prev_conflicted_state = yield self.state.resolve_delta_state(
                    same_groups,
                    changed_groups,
                    self.prev_conflicted_state,
                    self.store,
                    event_map=None,
                    state_map_factory=get_events,
                )
                new_state = dict(self.prev_state)
                new_state.update(state_delta)
                # self.prev_groups = groups
                # return

        group_to_state = yield self.store.get_state_for_groups(groups)

        entry = yield self.state.resolve_state_groups(
            room_id, RoomVersions.V1, group_to_state, None, get_events
        )

        if new_state is not None and entry.state != new_state:
            for key in entry.state:
                if entry.state[key] != new_state[key]:
                    logger.info("State difference: %s, %s != %s", key, entry.state[key], new_state[key])
            raise Exception("State didn't match")

        self.prev_groups = groups
        self.prev_conflicted_state = entry.conflicted_state
        self.prev_state = entry.state


@defer.inlineCallbacks
def run(hs):
    try:
        room_id = "!DKTALuSIPGrKqdJmPQ:matrix.org"
        groups_list = yield get_group_list(hs.get_datastore(), room_id)

        logger.info("Len: %d", len(groups_list))

        resolver = Resolver(hs)

        i = 0
        for groups in groups_list:
            yield resolver.calculate_state(room_id, groups)
            i += 1
            logger.info("Completed %d/%d", i, len(groups_list))
    finally:
        reactor.stop()


def main():
    hs = make_hs()

    state = hs.get_state_resolution_handler()
    store = hs.get_datastore()

    hs.get_clock().call_later(0, run, hs)

    reactor.run()


if __name__ == "__main__":
    main()
