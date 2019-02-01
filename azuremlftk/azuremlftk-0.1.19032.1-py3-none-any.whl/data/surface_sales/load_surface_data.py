"""
Utility to read the Surface sales mini-dataset from tsv to a TimeSeriesDataFrame.
"""


## imports
import sys, os, inspect
import pandas as pd

path_to_self = os.path.realpath(os.path.dirname(__file__))
FTK_ROOT_PATH = os.path.realpath(os.path.join(path_to_self, '../../../../lib'))
if FTK_ROOT_PATH not in sys.path:
    sys.path.insert(0, FTK_ROOT_PATH)

from ftk.time_series_data_frame import TimeSeriesDataFrame


#####################################################################################

def load_surface_dataset(data_path = FTK_ROOT_PATH + '/ftk/data/surface_sales/'):
    """
    Returns the Surface Sales dataset (just the basic time series part).

    :param data_path:
        Path of the folder that contains Surface Sales dataset.       
    :type data_path:
        string.

    :return:
        TimeSeriesDataFrame object conataining Surface Sales data.
    """
    # print(data_path)
    series = pd.read_csv(os.path.join(data_path, 'surface_sales_sample.csv'), 
                         low_memory = False)
    # print(series.columns)

    # Convert the date column to numpy.datetime64 type
    series['Date'] = pd.to_datetime(series['Date'])    

    # Convert sales column to float
    series['SellThruUnits']     = series['SellThruUnits'].astype('float')
    series['Retail Price (LC)']  = series['Retail Price (LC)'].astype('float')
    series['ERP (LC)']          = series['ERP (LC)'].astype('float')
    series['Promotion (%)']     = series['SellThruUnits'].astype('float')

    train_ts = TimeSeriesDataFrame(
        series,  
        grain_colnames=['Retailer Chain', 'Country', 'ProductFamilyName'], 
        time_colname='Date', 
        ts_value_colname='SellThruUnits')    

    return train_ts


###############################################################################
## Main

if __name__ == '__main__':
    
    surface_ts = load_surface_dataset(data_path = '.');
    print(surface_ts.describe());
