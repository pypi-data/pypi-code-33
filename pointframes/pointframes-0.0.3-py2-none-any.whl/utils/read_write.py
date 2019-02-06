import pandas as pd
import numpy as np
import os
import string

def read_pointcloud(pointcloud_path):
    ''' Main function for reading a single point cloud file
        into a PointCloud object. The idea is to support as many
        formats as possible.
        args:
            pointcloud_path : string
        returns
            pointcloud : Pandas dataframe
    '''

    known_formats = ['parquet', 'h5', 'csv', 'asc', 'txt']
    assert os.path.isfile(pointcloud_path), 'Error: File not found.'
    file_type = pointcloud_path.split('.')[-1]
    assert file_type in known_formats, 'Error: File format not recognised or supported.'

    if file_type == 'h5':
        pointcloud = pd.read_hdf(pointcloud_path)
    elif file_type == 'parquet':
        pointcloud = pd.read_parquet(pointcloud_path)
    if file_type == 'csv' or file_type == 'asc' or file_type == 'txt':
        pointcloud = pd.read_csv(pointcloud_path)

    return pointcloud

def write_pointcloud(pointcloud, save_path, mode='w'):
    ''' Main function for writing a dataframe pointcloud
        to a file locally. Currently saves a single dataframe
        to a single file.
        args:
            pointcloud : Pandas dataframe
        returns:
            None
    '''

    # Check save directory is valid
    dir_check = "".join(x+'/' for x in save_path.split('/')[0:-1])
    print(dir_check)
    assert os.path.isdir(dir_check), 'Error: Directory not found.'

    # Check file type is supported
    file_type = save_path.split('.')[-1]
    known_formats = ['parquet', 'h5', 'csv', 'asc']
    assert file_type in known_formats, 'Error: File format not recognised or supported.'

    if file_type == 'h5':
        pointcloud.to_hdf(save_path, key='df', mode=mode)
    elif file_type == 'parquet':
        pointcloud.to_parquet(save_path)
    elif file_type == 'csv' or file_type == 'asc':
        pointcloud.to_csv(save_path, mode=mode)

    return None

def merge_dask_csv(directory, filename, npartitions):

    with open(os.path.join(directory, filename+'.csv'), 'w') as outfile:
        for i in range(0, npartitions):
            file_string = os.path.join(directory, filename+'_%.'+str(len(str(npartitions)))+'d.csv')
            with open(file_string%i, 'r') as f:
                next(f)
                for line in f:
                    outfile.write(line)
            os.remove(file_string%i)
