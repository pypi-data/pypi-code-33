"""
Class for data download
"""

import pandas as pd
from sqlalchemy import create_engine

class Get_sql:
    
    def get_google_tree(connection):
        """
        An sql query to download the whole google taxonomy tree 
        """
        sql_query = "SELECT distinct(full_title), id, parent_id, title as class \
                        FROM sixads.sixads_category"

        tree = pd.read_sql_query(sql_query, connection)
        def f(x):
            if x is None:
                return ""
            else:
                return '>' + x
        tree['full_title'] = [f(x) for x in tree['full_title']]
        return tree

    def get_data(connection, select_part, from_part, where_part = ''):
        "Function that construcs a query from the given parts and executes it"
        
        columns = ",".join(select_part)
        
        sql_query = "SELECT {columns} \
                    FROM {from_part} \
                    {where_part}".format(columns = columns, 
                                         from_part = from_part, 
                                         where_part = where_part)
                    
        return pd.read_sql_query(sql_query, connection)

class Write_sql:
        
    def write_to_table(specs, table, data, if_exists = 'replace'):
        """
        Writes data to the desired table 
        """
        engine = create_engine("mysql+pymysql://{user}:{pw}@{host}/{db}"
                       .format(user=specs['user'],
                               pw=specs['password'],
                               host = specs['host'],
                               db=specs['db']))
        data.to_sql(table, con = engine, 
                            if_exists = if_exists, index = False)    