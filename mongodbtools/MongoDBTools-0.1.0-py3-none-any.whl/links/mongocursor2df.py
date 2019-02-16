# **********************************************************************************
# * Project: Eskapade - A python-based package for data analysis                   *
# * Class  : MongoCursor2Df
# * Created: 2018/02/05
# * Description:                                                                   *
# *      Algorithm to do...(fill in one-liner here)                                *
# *                                                                                *
# * Authors:                                                                       *
# *      KPMG Big Data team, Amstelveen, The Netherlands                           *
# *                                                                                *
# * Redistribution and use in source and binary forms, with or without             *
# * modification, are permitted according to the terms listed in the file          *
# * LICENSE.                                                                       *
# **********************************************************************************

from escore import process_manager, ConfigObject, Link, DataStore, StatusCode
from mongodbtools import MongoConnection
from mongodbtools.cursor_reader import MongoCursorReader

class MongoCursor2Df(Link):
    """Defines the content of link MongoCursor2Df"""

    def __init__(self, **kwargs):
        """Initialize MongoCursor2Df instance

        :param str name: name of link
        :param str collection: name of collection to find in mongo db
        :param str query: query to pass to mongo find command
        :param int skip: number of records to skip in query. Default is None.
        :param int limit: limit number of records in query. Default is None.
        :param str use_cols: columns to request from mongo collection in query
        :param int chuck_size: chunk_size with which to loop over mongo cursor. default is 10000.
        :param str store_key: key of output data to store in data store
        :param bool skip_empty: skip chain if (last) dataframe is empty. default is true.
        :param int n_chunks_in_fork: number of chunks per fork. Default is 1.
        """

        # initialize Link, pass name from kwargs
        Link.__init__(self, kwargs.pop('name', 'MongoCursor2Df'))

        # Process and register keyword arguments.  All arguments are popped from
        # kwargs and added as attributes of the link.  The values provided here
        # are defaults.
        self._process_kwargs(kwargs,
                             collection=None,
                             query=None,
                             skip=None,
                             limit=None,
                             use_cols=None,
                             chuck_size=10000,
                             store_key=None,
                             skip_empty=True,
                             n_chunks_in_fork=1)

        # check residual kwargs; exit if any present
        self.check_extra_kwargs(kwargs)

        # internal
        self._reader = None
        self._latest_data_length = 0
        self._sum_data_length = 0

    def initialize(self):
        """Initialize MongoCursor2Df

        :returns: status code of initialization
        :rtype: StatusCode
        """
        assert isinstance(self.collection, str) and len(self.collection), 'input collection not set.'
        assert isinstance(self.store_key, str) and len(self.store_key), 'key of output df not set.'

        # configure mongo to pick up at execute
        self.configure_mongo()

        return StatusCode.Success

    def configure_mongo(self, lock:bool=False) -> None:
        """Configure mongo used during exectute

        This is the final part of initialization, and needs to be redone in case of
        forked processing. Hence this function is split off into a separate function. 
        The function can be locked once the configuration is final.

        :param bool lock: if True, lock this part of the configuration
        """
        if self.config_lock:
            return
        self.config_lock = lock

        settings = process_manager.service(ConfigObject)
        if settings.get('fork', False): # during fork
            # Need to open separate mongo connection after each fork
            self.mongo_connection = MongoConnection()
            self.mongo_connection.set_config_info(settings)
            self.mdb = self.mongo_connection.database
            # set length of cursor of this fork
            fidx = settings['fork_index']
            self.skip = self.n_chunks_in_fork * fidx * self.chunk_size
            self.limit = self.n_chunks_in_fork * self.chunk_size
        else: # default (no fork)
            process_manager.service(MongoConnection).set_config_info(settings)
            self.mdb = process_manager.service(MongoConnection).database

        # check if collection names are in database
        colls = self.mdb.collection_names()
        if self.collection not in colls:
            self.logger.warning('Source collection <%s> does not exist in mongo db.' % self.collection)
            raise NameError
        try:
            kwargs = dict()
            kwargs['filter'] = self.query
            kwargs['projection'] = self.use_cols
            if self.skip: kwargs['skip'] = self.skip
            if self.limit: kwargs['limit'] = self.limit
            cursor = self.mdb[self.collection].find(**kwargs)
            self._reader = MongoCursorReader(cursor, self.chunk_size)
        except:
            self.logger.critical('Could not get cursor to source collection <%s> from mongo db.' % self.collection)
            raise BufferError

    def execute(self):
        """Execute MongoCursor2Df

        :returns: status code of execution
        :rtype: StatusCode
        """
        ds = process_manager.service(DataStore)
        settings = process_manager.service(ConfigObject)

        # 0. when in fork mode, need to reconfigure paths read out. lock ensures it's only done once.
        if settings.get('fork', False):
            self.configure_mongo(lock=True)

        self.logger.debug('Now executing link: {}'.format(self.name))

        df = next(self)

        # at end of all records? skip rest of chain
        if self.latest_data_length()==0 and self.skip_empty:
            return StatusCode.BreakChain

        # do we have more datasets to go?
        # pass this information to the (possible) repeater at the end of chain
        reqstr = 'chainRepeatRequestBy_'+self.name
        settings[reqstr] = True if not self.isFinished() else False
        ds[reqstr] = self.isFinished()

        numentries = self.latest_data_length()
        sumentries = self.sum_data_length()
        self.logger.info('Read next <%d> transactions; summing up to <%d>.' % (numentries, sumentries))
        
        # store df and number of records
        ds[self.store_key] = df
        ds['n_'+self.store_key] = numentries
        ds['n_sum_'+self.store_key] = sumentries
        
        return StatusCode.Success

    def __next__(self):
        """ 
        Pass up the next df of the mongo cursor.
        """
        try:
            df = self._reader.next()
        except StopIteration:
            # BlockFileReader throws stopiterator exception at end
            df = None
        except Exception:
            raise Exception('Unexpected error: cannot process next iteration.')

        # bookkeeping
        try:
            self._latest_data_length = len(df.index)
        except: 
            self._latest_data_length = 0
        self._sum_data_length += self._latest_data_length
            
        return df

    def latest_data_length(self):
        """ Return length of current dataset """
        return self._latest_data_length
    
    def sum_data_length(self):
        """ Return sum length of all datasets processed sofar """
        return self._sum_data_length

    def isFinished(self):
        """ 
        Try to assess if looper is done iterating over cursor.
        """
        finished = (self._latest_data_length < self.chunk_size)
        return finished

    @property
    def config_lock(self):
        """Get lock status of configuration

        Default lock status is False.

        :returns: lock status of configuration
        :rtype: bool
        """
        if not hasattr(self, '_config_lock'):
            self._config_lock = False
        return self._config_lock

    @config_lock.setter
    def config_lock(self, lock):
        """Lock the configuration status

        Once locked, configuration stays locked.

        :param bool lock: to-be status of configuration lock
        :raises RunTimeError: If already locked, it will not overwrite to False.
        """
        if hasattr(self, '_config_lock'):
            if self._config_lock and not lock:
                raise RuntimeError('Configuration lock already set. Will not unlock.')
        self._config_lock = lock
