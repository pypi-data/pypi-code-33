def _queue_into_buffer(transfersession):
    """
    Takes a chunk of data from the store to be put into the buffer to be sent to another morango instance.
    """
    last_saved_by_conditions = []
    filter_prefixes = Filter(transfersession.filter)
    server_fsic = json.loads(transfersession.server_fsic)
    client_fsic = json.loads(transfersession.client_fsic)

    if transfersession.push:
        fsics = _fsic_queuing_calc(client_fsic, server_fsic)
    else:
        fsics = _fsic_queuing_calc(server_fsic, client_fsic)

    # if fsics are identical or receiving end has newer data, then there is nothing to queue
    if not fsics:
        return

    # create condition for all push FSICs where instance_ids are equal, but internal counters are higher than FSICs counters
    for instance, counter in iteritems(fsics):
        last_saved_by_conditions += ["(last_saved_instance = '{0}' AND last_saved_counter > {1})".format(instance, counter)]
    if fsics:
        last_saved_by_conditions = [_join_with_logical_operator(last_saved_by_conditions, 'OR')]

    partition_conditions = []
    # create condition for filtering by partitions
    for prefix in filter_prefixes:
        partition_conditions += ["partition LIKE '{}%'".format(prefix)]
    if filter_prefixes:
        partition_conditions = [_join_with_logical_operator(partition_conditions, 'OR')]

    # combine conditions
    fsic_and_partition_conditions = _join_with_logical_operator(last_saved_by_conditions + partition_conditions, 'AND')

    # filter by profile
    where_condition = _join_with_logical_operator([fsic_and_partition_conditions, "profile = '{}'".format(transfersession.sync_session.profile)], 'AND')

    # execute raw sql to take all records that match condition, to be put into buffer for transfer
    with connection.cursor() as cursor:
        queue_buffer = """INSERT INTO {outgoing_buffer}
                        (model_uuid, serialized, deleted, last_saved_instance, last_saved_counter,
                         model_name, profile, partition, source_id, conflicting_serialized_data, transfer_session_id, _self_ref_fk)
                        SELECT id, serialized, deleted, last_saved_instance, last_saved_counter, model_name, profile, partition, source_id, conflicting_serialized_data, '{transfer_session_id}', _self_ref_fk
                        FROM {store} WHERE {condition}""".format(outgoing_buffer=Buffer._meta.db_table,
                                                                 transfer_session_id=transfersession.id,
                                                                 condition=where_condition,
                                                                 store=Store._meta.db_table)
        cursor.execute(queue_buffer)
        # take all record max counters that are foreign keyed onto store models, which were queued into the buffer
        queue_rmc_buffer = """INSERT INTO {outgoing_rmcb}
                            (instance_id, counter, transfer_session_id, model_uuid)
                            SELECT instance_id, counter, '{transfer_session_id}', store_model_id
                            FROM {record_max_counter} AS rmc
                            INNER JOIN {outgoing_buffer} AS buffer ON rmc.store_model_id = buffer.model_uuid
                            WHERE buffer.transfer_session_id = '{transfer_session_id}'
                            """.format(outgoing_rmcb=RecordMaxCounterBuffer._meta.db_table,
                                       transfer_session_id=transfersession.id,
                                       record_max_counter=RecordMaxCounter._meta.db_table,
                                       outgoing_buffer=Buffer._meta.db_table)
        cursor.execute(queue_rmc_buffer)


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
