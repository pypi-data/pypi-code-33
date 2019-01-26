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

    def get_labeled_data_products(connection):
        """
        An sql query to download item names with the labeled categories
        """
        sql_query = "SELECT pr.id as item_id, pr.category_id as class_id, pr.title \
                     FROM sixads.sixads_product as pr \
                     where category_id is not null"

        return pd.read_sql_query(sql_query, connection)
        
    def get_fetchproduct_data(connection, limit = None):
       """
       Downloads the data for predictions
       """
       sql_query = "SELECT id, original_title as title, shop_id \
                    FROM sixads.sixads_fetchedproduct pr"
                    
       if limit is not None :
           sql_query = sql_query + ' LIMIT ' + str(limit)
                              
       return pd.read_sql_query(sql_query, connection) 
   
    def get_excluded_cats(connection, shop_id):
        sql_query = "SELECT * \
                    FROM sixads.sixads_shop_excluded_categories \
                    where shop_id = {shop_id}".format(shop_id = shop_id)
        
        return pd.read_sql_query(sql_query, connection)
    
    def adult_info(connection, shop_id):
        sql_query = "SELECT exclude_adult \
        from sixads.sixads_shop \
        where id = {shop_id}".format(shop_id = shop_id) 
        
        return pd.read_sql_query(sql_query, connection)
    
    def curr_info(connection, shop_id):
        sql_query = "SELECT currency \
        from sixads.sixads_shop \
        where id = {shop_id}".format(shop_id = shop_id) 
        
        return pd.read_sql_query(sql_query, connection)
    
    def get_adult_cats(connection):
        sql_query = "SELECT id as category_id \
        from sixads.sixads_category \
        where base_parent_id = 3981"
        
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