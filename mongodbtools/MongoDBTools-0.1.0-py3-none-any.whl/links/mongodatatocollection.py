# **********************************************************************************
# * Project: Eskapade - A python-based package for data analysis                   *
# * Class  : MongoDataToCollection                                                 *
# * Created: 2016/11/08                                                            *
# * Description:                                                                   *
# *      Algorithm to store a list in mongo database                               *
# *                                                                                *
# * Authors:                                                                       *
# *      KPMG Big Data team, Amstelveen, The Netherlands                           *
# *                                                                                *
# * Redistribution and use in source and binary forms, with or without             *
# * modification, are permitted according to the terms listed in the file          *
# * LICENSE.                                                                       *
# **********************************************************************************

from escore import process_manager, ConfigObject, Link, DataStore, StatusCode
from mongodbtools import MongoConnection, etl_utils

import os

class MongoDataToCollection(Link):
    """
    Adds data in a pandas.DataFrame to one or more mongo collections.
    """

    def __init__(self, name='MongoDataToCollection'):
        """
        Store the configuration of link MongoDataToCollection

        :param str name: name of link
        :param str read_key: key of data to read from data store
        :param list store_collections: mongo collection names of the collections to store the data
        :param bool clearFirst: if True the mongo store_collections are cleared before storage
        :param int minimal_input_size: integer. Storage is only performed if data meets minimal length (gt 0). default is -1.
        :param list force_move_keys: list of keys to booleans in datastore, OR-red, to overwrite minimal_input_size.
        :param bool clear_input: if true, input data is deleted from ds after storage in mongo.
        """

        Link.__init__(self, name)

        self.read_key = None
        self.store_collections = []
        self.clearFirst = False
        self.minimal_input_size = -1
        self.force_move_keys = []
        self.clear_input = False
        self.fork = False
        self.wait_after_fork = False

        return

    def initialize(self):
        """ Initialize MongoDataToCollection """

        assert isinstance(self.read_key, str) and len(self.read_key) > 0, 'read key not set.'
        if len(self.store_collections) == 0:
            self.store_collections.append(self.read_key)

        if isinstance(self.force_move_keys, str):
            self.force_move_keys = [self.force_move_keys]

        # initialize mongo connection
        # when forking, need to set up new connection.
        if not self.fork:
            settings = process_manager.service(ConfigObject)
            process_manager.service(MongoConnection).set_config_info(settings)
            self.mdb = process_manager.service(MongoConnection).database

        return StatusCode.Success

    def execute(self):
        """ Execute MongoDataToCollection """

        ds = process_manager.service(DataStore)
        docs = ds.get(self.read_key, None)
        if docs is None:
            self.logger.warning('object with key {} is empty. skipping'.format(self.read_key))
            return StatusCode.Success

        if self.minimal_input_size > 0:
            invoke = any( [ds.get(f,False) for f in self.force_move_keys] )
            if len(docs) < self.minimal_input_size and not invoke:
                self.logger.debug('Input collection <%s> has fewer than %d records. Not stored.' % (self.read_key, self.minimal_input_size))
                return StatusCode.Success
            else:
                self.logger.debug('Storing input collection <%s> with size %d' % (self.read_key, len(docs)))

        if len(docs) == 0:
            self.logger.info('Input collection <%s> has zero length. Nothing to store.' % self.read_key)
            return StatusCode.Success

        if not self.fork:
            # default
            etl_utils.dostorage(self.mdb, docs, self.store_collections, self.clearFirst, self.logger, self.read_key)
        else:
            self.fork_and_store()

        if self.clear_input:
            del ds[self.read_key]

        return StatusCode.Success

    def fork_and_store(self):
        """Fork and then store input collection

        Need to reopen mongo connection after fork
        """
        self.logger.debug("Process id before forking: {}".format(os.getpid()))

        child_pid_list = []

        # submit a new process
        try:
            pid = os.fork()
        except OSError:
            raise OSError("Could not create a child process.")

        if pid == 0:
            self.logger.debug("In child process with PID {}".format(os.getpid()))

            # Need to open separate mongo connection after each fork
            settings = process_manager.service(ConfigObject)
            mongo_connection = MongoConnection()
            mongo_connection.set_config_info(settings)
            mdb = mongo_connection.database

            ds = process_manager.service(DataStore)
            docs = ds[self.read_key]

            # store docs
            etl_utils.dostorage(mdb, docs, self.store_collections, self.clearFirst, self.logger, self.read_key)

            # close connection
            mongo_connection.close()

            # safe jupyter exit when forking
            os._exit(os.EX_OK)
        else:
            self.logger.debug("Back in parent process after forking child {}".format(pid))
            child_pid_list.append(pid)

        # can wait for fork to finish, or just go.
        if self.wait_after_fork:
            # check that fork is finished
            while child_pid_list:
                self.logger.debug("Waiting for child process to finish.")
                finished = os.waitpid(0, 0)
                if finished[0] in child_pid_list:
                    self.logger.debug("Finished child process {} with status {}".format(finished[0], finished[1]))
                    child_pid_list.remove(finished[0])

        self.logger.debug('Finished fork.')
