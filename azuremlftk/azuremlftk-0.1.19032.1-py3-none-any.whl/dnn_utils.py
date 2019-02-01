import pandas as pd
from warnings import warn
import keras
import h5py
import tempfile
import os

def create_lag_lead_features(data, ts_col, aux_cols, num_lags=1, num_leads=0, dropnan=True) :	
    """
    Creates lag and lead features for a given timeseries. It also allows an additional 
    auxiliary columns to be be included from the input data frame.    
    Todo: if lags and lead features are needed to be constructed for auxiliary columns as well then
    that functionality needs to be added here.
    This function should go away once lagleadoperator from ftk could be used instead.
    : param data
        dataframe containing time series for which lag and lead features need to be generated. 
        It also contains auxiliary data that could provide additional information for the time series.      
    : param ts_col
        name of the column that contains time series data.
    : param aux_cols
        name of the column(s) that contain auxiliary data.
    : param num_lags
        number of lags to construct.
    : param num_leads
        number of leads to contruct.  
    : param dropnan
        boolean indicating whether to drop rows with NaN values as lags and leads are constructed.
    : return
        dataframe with lag and lead fatures of a time series data, along with auxiliary column information.
    """
       
    df = pd.DataFrame(data)
    lag_lead_data = [df.loc[:, aux_cols]]
    final_col_names = aux_cols
    
    if (num_lags < 0) :
        error_message = 'number of lags cannot be negative.'
        raise Exception(error_message)

    if (num_leads < 0) :
        error_message = 'number of leads cannot be negative.'
        raise Exception(error_message)
       
	# historical lags creation (t-n, ... t-1)
    for i in range(num_lags, 0, -1) :
        lag_lead_data.append(df[ts_col].shift(i))        
        final_col_names += [(ts_col + 'Lag' + str(i))]

    # future value creation (t, t+1, ... t+n)
    for i in range(0, (num_leads + 1)) :
        lag_lead_data.append(df[ts_col].shift(-i))
        if i == 0 :
            final_col_names += [(ts_col + 'Lead0')]
        else:
            final_col_names += [(ts_col + 'Lead' + str(i))]

	# collect all the data into one place
    result = pd.concat(lag_lead_data, axis=1)
    result.columns = final_col_names

	# drop rows with NaN values
    if dropnan :
        result = result.dropna()
    
    return result


def pickle_keras_models():
    """
    This function is temporarily added for prototype code and will be replaced with serialization and deserialization code.
    """
    def __getstate__(self):
        serialized_model = ""
        fd = tempfile.NamedTemporaryFile(suffix='.hdf5', delete=True)
        tmp_filename = fd.name
        fd.close()
        keras.models.save_model(self, tmp_filename, overwrite=True)
        fd = open(tmp_filename, 'rb')
        serialized_model = fd.read()
        model_state = { 'serialized_model': serialized_model }
        fd.close()
        os.remove(tmp_filename)
        return model_state

    def __setstate__(self, state):
        with tempfile.NamedTemporaryFile(suffix='.hdf5', delete=False) as fd:
            tmp_filename = fd.name
            fd.write(state['serialized_model'])
            fd.flush()
            fd.close()        
        model = keras.models.load_model(tmp_filename)
        os.remove(tmp_filename)
        self.__dict__ = model.__dict__


    cls = keras.models.Model
    cls.__getstate__ = __getstate__
    cls.__setstate__ = __setstate__