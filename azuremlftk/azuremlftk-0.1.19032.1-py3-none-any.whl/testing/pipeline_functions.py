from pandas import DataFrame

def replace_null_A_with_B(df):
    """
      Replaces nulls in column "A" by values from column "B".
    
      :param df: Pandas data frame. it should contain columns "A" and "B".
      :type df: DataFrame 
      :returns: the copy of data frame where nulls from the column "A" are replaced by values from column "B".
      :rtype: DataFrame
      
    """
    newdf = df.copy()
    newdf.loc[df['A'].isnull(), 'A' ] = df.loc[df['A'].isnull(), 'B']
    return newdf

def square_each_value(df):
    """
      Raises each value to the power of 2.
    
      :param df: Pandas data frame containing only numbers.
      :type df: DataFrame  
      :returns: the copy of data frame where all the values are raised to the power of 2.
      :rtype: DataFrame
      
    """
    return df.apply(lambda x: x**2)