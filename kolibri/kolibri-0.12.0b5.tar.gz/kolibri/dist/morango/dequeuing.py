from .sqlalchemybridge import Bridge
from morango.models import Buffer, Store, RecordMaxCounter, RecordMaxCounterBuffer
from sqlalchemy.sql import and_
from sqlalchemy import select

def _dequeuing_delete_rmcb_records(transfersession_id):

    bridge = Bridge()

    BufferTable = bridge.get_table(Buffer)
    StoreTable = bridge.get_table(Store)
    RecordMaxCounterTable = bridge.get_table(RecordMaxCounter)
    RecordMaxCounterBufferTable = bridge.get_table(RecordMaxCounterBuffer)

    connection = bridge.get_connection()

    subselect = select([RecordMaxCounterBufferTable.c.model_uuid]).where(
                                                                        and_(
                                                                            # scope to a single record*
                                                                            StoreTable.c.id == BufferTable.c.model_uuid,
                                                                            StoreTable.c.id == RecordMaxCounterTable.c.store_model_id,
                                                                            StoreTable.c.id == RecordMaxCounterBufferTable.c.model_uuid,
                                                                            # checks whether LSB of buffer or less is in RMC of store
                                                                            BufferTable.c.last_saved_instance == RecordMaxCounterTable.c.instance_id,
                                                                            BufferTable.c.last_saved_counter <= RecordMaxCounterTable.c.counter,
                                                                            RecordMaxCounterBufferTable.c.transfer_session_id == transfersession_id,
                                                                            BufferTable.c.transfer_session_id == transfersession_id
                                                                        )
                                                                    )
    rmcb_statement = RecordMaxCounterBufferTable.delete().where(RecordMaxCounterBufferTable.c.model_uuid.in_(subselect))
    connection.execute(rmcb_statement)

    bridge.end()


def _dequeuing_delete_buffered_records(self, cursor, transfersession_id):

    bridge = Bridge()

    BufferTable = bridge.get_table(Buffer)
    StoreTable = bridge.get_table(Store)
    RecordMaxCounterTable = bridge.get_table(RecordMaxCounter)
    RecordMaxCounterBufferTable = bridge.get_table(RecordMaxCounterBuffer)

    connection = bridge.get_connection()

    subselect = select([BufferTable.c.model_uuid]).where(
                                                        and_(
                                                            # scope to a single record
                                                            StoreTable.c.id == BufferTable.c.model_uuid,
                                                            RecordMaxCounterTable.c.store_model_id == BufferTable.c.model_uuid,
                                                            # checks whether LSB of buffer or less is in RMC of store
                                                            BufferTable.c.last_saved_instance == RecordMaxCounterTable.c.instance_id,
                                                            BufferTable.c.last_saved_counter <= RecordMaxCounterTable.c.counter,
                                                            BufferTable.c.transfer_session_id == transfersession_id
                                                        )
                                                    )
    buffer_statement = BufferTable.delete().where(BufferTable.c.model_uuid.in_(subselect))

    connection.execute(buffer_statement)

def _dequeuing_merge_conflict_rmcb(self, cursor, transfersession_id):
    raise NotImplemented("Subclass must implement this method.")

def _dequeuing_merge_conflict_buffer(self, cursor, current_id, transfersession_id):
    raise NotImplemented("Subclass must implement this method.")

def _dequeuing_update_rmcs_last_saved_by(self, cursor, current_id, transfersession_id):
    raise NotImplemented("Subclass must implement this method.")

def _dequeuing_delete_mc_buffer(self, cursor, transfersession_id):
    bridge = Bridge()

    BufferTable = bridge.get_table(Buffer)
    StoreTable = bridge.get_table(Store)
    RecordMaxCounterTable = bridge.get_table(RecordMaxCounter)
    RecordMaxCounterBufferTable = bridge.get_table(RecordMaxCounterBuffer)

    connection = bridge.get_connection()

    subselect = select([RecordMaxCounterBufferTable.c.model_uuid]).where(
                                                                        and_(
                                                                            # scope to a single record*
                                                                            StoreTable.c.id == BufferTable.c.model_uuid,
                                                                            StoreTable.c.id == RecordMaxCounterTable.c.store_model_id,
                                                                            StoreTable.c.id == RecordMaxCounterBufferTable.c.model_uuid,
                                                                            # checks whether LSB of buffer or less is in RMC of store
                                                                            BufferTable.c.last_saved_instance == RecordMaxCounterTable.c.instance_id,
                                                                            BufferTable.c.last_saved_counter <= RecordMaxCounterTable.c.counter,
                                                                            RecordMaxCounterBufferTable.c.transfer_session_id == transfersession_id,
                                                                            BufferTable.c.transfer_session_id == transfersession_id
                                                                        )
                                                                    )
    rmcb_statement = RecordMaxCounterBufferTable.delete().where(RecordMaxCounterBufferTable.c.model_uuid.in_(subselect))
    connection.execute(rmcb_statement)

    bridge.end()



    # delete records with merge conflicts from buffer
    delete_mc_buffer = """DELETE FROM {buffer}
                                WHERE EXISTS
                                (SELECT 1 FROM {store} AS store, {buffer} AS buffer
                                /*Scope to a single record.*/
                                WHERE store.id = {buffer}.model_uuid
                                AND {buffer}.transfer_session_id = '{transfer_session_id}'
                                /*Exclude fast-forwards*/
                                AND NOT EXISTS (SELECT 1 FROM {rmcb} AS rmcb WHERE store.id = rmcb.model_uuid
                                                                              AND store.last_saved_instance = rmcb.instance_id
                                                                              AND store.last_saved_counter <= rmcb.counter
                                                                              AND rmcb.transfer_session_id = '{transfer_session_id}'))
                           """.format(buffer=Buffer._meta.db_table,
                                      store=Store._meta.db_table,
                                      rmc=RecordMaxCounter._meta.db_table,
                                      rmcb=RecordMaxCounterBuffer._meta.db_table,
                                      transfer_session_id=transfersession_id)
    cursor.execute(delete_mc_buffer)

def _dequeuing_delete_mc_rmcb(self, cursor, transfersession_id):
    bridge = Bridge()

    BufferTable = bridge.get_table(Buffer)
    StoreTable = bridge.get_table(Store)
    RecordMaxCounterTable = bridge.get_table(RecordMaxCounter)
    RecordMaxCounterBufferTable = bridge.get_table(RecordMaxCounterBuffer)

    connection = bridge.get_connection()

    # select fast-forwards
    select_fast_forwards = select([RecordMaxCounterBufferTable.c.model_uuid]).where(
                                                                     and_(
                                                                        StoreTable.c.id == RecordMaxCounterBufferTable.c.model_uuid,
                                                                        StoreTable.c.last_saved_instance == RecordMaxCounterBufferTable.c.instance_id,
                                                                        StoreTable.c.last_saved_counter == RecordMaxCounterBufferTable.c.counter,
                                                                        RecordMaxCounterBufferTable.c.transfer_session_id == transfersession_id
                                                                     )
                                                                ).correlate(RecordMaxCounterBufferTable)

    subselect = select([RecordMaxCounterBufferTable.c.model_uuid]).where(
                                                                        and_(
                                                                            # scope to a single record*
                                                                            StoreTable.c.id == RecordMaxCounterBufferTable.c.model_uuid,
                                                                            StoreTable.c.id == RecordMaxCounterTable.c.store_model_id,
                                                                            # where buffer rmc is greater than store rmc
                                                                            RecordMaxCounterBufferTable.c.instance_id == RecordMaxCounterTable.c.instance_id,
                                                                            RecordMaxCounterBufferTable.c.transfer_session_id == transfersession_id,
                                                                            # exclude fast forwards
                                                                            RecordMaxCounterBufferTable.c.model_uuid.notin_(select_fast_forwards)
                                                                        )
                                                                    )
    rmcb_statement = RecordMaxCounterBufferTable.delete().where(RecordMaxCounterBufferTable.c.model_uuid.in_(subselect))
    connection.execute(rmcb_statement)

    bridge.end()


    # delete rmcb records with merge conflicts
    delete_mc_rmc = """DELETE FROM {rmcb}
                                WHERE EXISTS
                                (SELECT 1 FROM {store} AS store, {rmc} AS rmc
                                /*Scope to a single record.*/
                                WHERE store.id = {rmcb}.model_uuid
                                AND store.id = rmc.store_model_id
                                /*Where buffer rmc is greater than store rmc*/
                                AND {rmcb}.instance_id = rmc.instance_id
                                AND {rmcb}.transfer_session_id = '{transfer_session_id}'
                                /*Exclude fast fast-forwards*/
                                AND NOT EXISTS (SELECT 1 FROM {rmcb} AS rmcb2 WHERE store.id = rmcb2.model_uuid
                                                                              AND store.last_saved_instance = rmcb2.instance_id
                                                                              AND store.last_saved_counter <= rmcb2.counter
                                                                              AND rmcb2.transfer_session_id = '{transfer_session_id}'))
                           """.format(buffer=Buffer._meta.db_table,
                                      store=Store._meta.db_table,
                                      rmc=RecordMaxCounter._meta.db_table,
                                      rmcb=RecordMaxCounterBuffer._meta.db_table,
                                      transfer_session_id=transfersession_id)
    cursor.execute(delete_mc_rmc)

def _dequeuing_insert_remaining_buffer(self, cursor, transfersession_id):

    BufferTable.insert().where(BufferTable.transfer_session_id == transfersession_id)

def _dequeuing_insert_remaining_rmcb(self, cursor, transfersession_id):

    RecordMaxCounterBufferTable.insert().where(RecordMaxCounterBufferTable.transfer_session_id == transfersession_id)

def _dequeuing_delete_remaining_rmcb(self, cursor, transfersession_id):

    RecordMaxCounterBufferTable.delete().where(RecordMaxCounterBufferTable.transfer_session_id == transfersession_id)

def _dequeuing_delete_remaining_buffer(self, cursor, transfersession_id):

    BufferTable.delete().where(BufferTable.transfer_session_id == transfersession_id)
