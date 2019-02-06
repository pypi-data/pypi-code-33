def check_attributes(pointcloud, attribute_list=[]):
    ''' Function to check if attributes are present in
        dataframe. Will result in assert error is attribute
        can not be found.

        args:
            df             : pandas dataframe
            attribute_list : list (of attributes to check)
        returns:
            Assertion error or None
    '''

    for attr in attribute_list:
        assert attr in pointcloud.columns, 'Error: Attribute not in dataframe.'

    return None
