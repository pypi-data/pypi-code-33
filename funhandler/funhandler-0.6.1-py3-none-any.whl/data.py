import os
import sys
import time
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
from distributed.worker import thread_state
from funpicker import Query, QueryTypes

from funhandler.file_manager import store_local_storage
from funhandler.file_manager import store_cloud_storage
# this is a pointer to the module object instance itself. 
# NOTE: We use this to set module-wide variables such as the storage location
this = sys.modules['funhandler']

# TODO: add proper logging


def add_bars(data):
    """ Adds the bars of the current data to the database

    This function receives list(dict) or will convert pd.DataFrame
    to list(dict). Data should contain required keys in it that
    will be used to query `funpicker`. Once funpicker response is
    ready data will be stored to `funtime`.

    Function will do basic validation on the incoming data.
    --------------------------------------------------------------

    Parameters
    ----------
    data: list(dict)
        List of lookups 
    Returns
    -------
    bool
        False - if anything went wrong TODO: add exceptions
        True - if bars were saved successfully

    Raises
    ------
    AttributeError
        Raised when passed datatype is not correct

    KeyError
        Raised when required keys missing in passed data
        
    """

    # Start validation of incoming  data

    # 0. If data is None, return False
    print("Adding data")
    if not data:
        return False
    # 1. Check if datatype of incoming data is list(dict)
    #    If data is a pd.DataFrame -> convert it to list(dict)
    if not isinstance(data, list):
        if isinstance(data, pd.DataFrame):
            data = data.to_dict('records')
        else:
            raise AttributeError("Not valid datatype for param data provided."
                                 "Datatype has to be list(dict) or pandas.DataFrame.")

    # print(data)
    # 2. Ensure all of the necessary keys are here
    # You did it wrong here man. We need to be able to add new keys. If the data isn't prepared it wont work.
    required_keys = ['base', 'trade', 'exchange', 'period', 'type']
    for item in data:
        keys = item.keys()
        if not set(required_keys).issubset(keys):
            raise KeyError("Some required keys are not present in dataset:"
                           f"dataset: {keys}, required: {required_keys}")

        # item['type'] = "price"
        # NOTE:

        # we can start processing and pulling data from funpicker at this
        # point. The question is: do we want to know if all dataset has valid
        # keys first or not?

        # The way I would think we need to do is to skip whatever lines are not correct and
        # process what we can and maybe record where data was wrong and retun 'Warnings' back
        # to user.

    # End validation

    # Get bars data from `funpicker`
    # Another question. Why do we need the timestamp?
    for item in data:
        # print(item)
        result = _get_bars_data_from_funpicker(**item)
        # print(result)
        if (isinstance(result, dict)
            and result.get('Response')
            and result['Response'] == 'Error'):
            print(f"Error for a pair: {item['base']}-{item['trade']} | "
                  f"Message: {result.get('Message')}")
            continue
        if not result:
            continue
        # TODO: remove all NaN as 0
        save_to_funtime(result, **item)

    return True

def _get_bars_data_from_funpicker(data={},limit=800,**kwargs):
    crypto = kwargs['base']
    fiat = kwargs['trade']
    exchange = kwargs['exchange']
    period = kwargs['period']

    # query_type = kwargs['type']

    return (Query().set_crypto(crypto)
                   .set_fiat(fiat)
                   .set_exchange(exchange)
                   .set_period(period)
                   .set_limit(limit)
                   .get())

def save_to_funtime(data, **kwargs):
    """ Store data results to funtime

    Parameters
    ----------
    data: list(dict)
        Response data from funpicker
    """
    # db = this.db
    # store_name = this.store_name
    # if not db:
    #     db = thread_state.db
    #     store = thread_state.store_name
    # print(kwargs)
    for item in data:
        item.update(kwargs)
        # TODO: funtime doesn't have store_many functionality as of right now.
        # once that is added we should be able to pass a list to funtime and
        # it will handle batch load.
        if item.get('time') is not None:
            item.update({"timestamp": float(item['time'])})
            this.db[this.store_name].store(item)

def _convert_to_pq_and_save(df, file_name):
    # storage_information = this.storage_information
    # if not storage_information:
    #     thread_state.storage_information = 
    table = pa.Table.from_pandas(df)
    file_path = os.path.join(
        this.storage_information['base_path'],
        this.storage_information['storage_folder']
    )
    if not os.path.isdir(file_path):
        os.makedirs(file_path)
    pq.write_table(
        table,
        os.path.join(file_path, file_name)
    )

def load_data(**kwargs):
    """ Loads data based on the provided args to parquet file

    Provided kwargs contain query information wchich is used to
    query funtime. If any of the results are found - they will be
    saved to parquet file either to loca_storage or cloud_storage
    depending on what storage model is setup by the user.

    Raises
    ------
        TODO: add custom exception handlers for different issues.
        Exception()
            if file storage fails. Message will contain the reason.
    """
    # if data exist with the given parameters pull from the funtime library
    result = this.db[this.store_name].query(kwargs)
    _exhausted = object()
    if next(result, _exhausted) == _exhausted:
        # not data found, will return False
        print(f"No data was found with params: {kwargs}")
        return False

    # Create a pandas dataframe for the data
    df = pd.DataFrame(result)

    ss = pd.to_datetime(df['timestamp'],unit='s')
    df = df.set_index(ss)
    df = df.sort_index(ascending=False)
    file_name = f'data_{int(time.time())}.parquet'
    try:
        # Save the parquet file somewhere
        # save file locally or in the cloud
        if this.current_storage_type == 'local':

            _convert_to_pq_and_save(df, file_name)
            file_storage_info = {
                'base_path': this.storage_information['base_path'],
                'storage_folder': this.storage_information['storage_folder'],
                'full_path': os.path.join(
                    this.storage_information['base_path'],
                    this.storage_information['storage_folder'],
                    file_name
                )
            }
        elif this.current_storage_type == 'cloud':
            # TODO: store file in the cloud (AWS S3/GCS)

            # Store file locally first and then upload to cloud
            # _convert_to_pq_and_save(df, file_name)
            # pq.write_table(
            #     table,
            #     os.path.join('/tmp', file_name)
            # )
            # 

            # Upload file to cloud here
            # store_cloud_storage('/tmp/data.parquet')
            file_storage_info = {
                'base_path': this.storage_information['base_path'],
                'bucket_name': this.storage_information['bucket_name'],
                'full_path': os.path.join(
                    this.storage_information['bucket_name'],
                    this.storage_information['base_path'],
                    file_name
                )
            }
            # cleanup from local
            pass
        else:
            raise Exception(
                "Storage model and/or storage info is not setup. "
                "Please use 'set_storage_model()' and/or 'set_local_storage_info()' "
                "to setup file storage configs.")
    except Exception as ex:
        raise ex

    # Add the location into funtime
    # Store file location to funtime as a new object.
    file_location = {
        'storage_type': this.current_storage_type,
        'file_name': file_name,
        'type': 'parquet_file',
        'timestamp': time.time(),
    }
    file_location.update(file_storage_info)
    extra_params = kwargs
    del extra_params['type']
    file_location.update(extra_params)
    this.db[this.store_name].store(file_location)
    return True

def is_still_bars(**kwargs):
    """ Check if parquet file has any bars

    Parameters
    ----------
    kwargs: dict
        query params

    Returns
    -------
    bool
    """
    # limit = kwargs.get('limit', 1)
    query_params = kwargs
    query_params['type'] = 'parquet_file'
    result, data = get_latest_data(query_params)
    if not result:
        return False
    df_data = pd.read_parquet(data['full_path'])
    if not df_data.empty:
        return True

def get_latest_data(query_args):
    if not isinstance(query_args, dict):
        return False, {} 

    last_ran = list(this.db[this.store_name].query_latest({'limit': 1, **query_args}))
    if len(last_ran) == 0:
        # Find something to do here
        return False, {}
    
    return True, last_ran[0]

def get_latest_bar_v2(**kwargs):
    """ Get latest bar(s) from parquet file
        based on provided params

    Parameters
    ----------
    kwargs: dict
        query params

    Returns
    -------
    pandas.Dataframe
        contains >= 1 rows, depending on the provided limit
    """
    # Limit is not the number of rows retuned back from database. It's the numerb of bars returned inside of 
    limit = kwargs.get('limit', 1) # if limit provided then it will be the number of rows returned back.
    if 'limit' in kwargs:
        del kwargs['limit']
    query_params = kwargs
    query_params['type'] = 'parquet_file'
    result, data = get_latest_data(query_params)
    if not result:
        raise LookupError(f"No data found. Params {kwargs}")
    df_data = pd.read_parquet(data['full_path'])
    result = df_data.tail(limit) 
    df_data.drop(df_data.tail(1).index, inplace=True) # Pop only one bar
    _convert_to_pq_and_save(df_data, data['file_name'])
    return result

def get_latest_bar(base, trade, exchange, limit=500, period='minute', data_type='price'):
    # Load the latest bars from the last loaded data (inside of the funtime library)

    # Turn parquet file into latest bar

    # If theres no ran_bars for the latest bars, create a new dataframe and save to funtime for record
    # If there is ran_bars, get the latest for the given type of information (see)
    
    # Query information goes here
    
    q_info = {'base':base, 'trade':trade, 'exchange': exchange, 'limit': limit, 'period': period, 'type': data_type}
    # Should have the latest table or nothing
    latest_bar_table = get_latest_data(q_info)

    if latest_bar_table[0] == False:
        raise AttributeError("Bar doesn't exist")

    # TODO: Pop the latest bar from this table. Ensure it's removed
    # This can be done using the tutorial available here:
        # https://stackoverflow.com/questions/39263411/pandas-pop-last-row
    

    # TODO: Save the new
    return True
