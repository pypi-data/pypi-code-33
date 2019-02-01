import pandas as pd
from azure.storage.blob.blockblobservice import BlockBlobService
from ftk.datasources import SQLDataManager
import sqlalchemy
import urllib

def create_table_maybe(table, server, database, user, password, data_file, dialect='mssql', driver='SQL Server'):
    """
    Check if there is a database with filled out table.
    If the table already exists, do nothing.
    
    :param table: The table name.
    :type table: str
    :param server: The domain name of a server.
    :type server: str
    :param database: The database name.
    :type database: str
    :param user: The user name.
    :type user: str
    :param password: The password to the user account.
    :type password: str
    :param data_file: The name of a data file to load the data from.
    :type data_file: str
    :param dialect: The database dialect used by the sqlalchemy.
    :type dialect: str
    :param driver: The driver used by the pyodbc.
    :type driver: str
    
    """
    connection_str = SQLDataManager.conn_string(server, database, user, password, driver)
    params = urllib.parse.quote_plus(connection_str)
    cnxn = sqlalchemy.create_engine("{}+pyodbc:///?odbc_connect={}".format(dialect, params))
    data = pd.read_csv(data_file)
    try:
        data.to_sql(table, cnxn, if_exists='fail', index=False)
    except ValueError:
        pass #Table already exists, do nothing.

def delete_blob_table_if_exists(account_name, key, container_name, blob_name):
    """
    Delete the Blob with given prefix from the table.
    
    :param account_name: The name of the account.
    :type account_name: str
    :param key: The key to the storage account.
    :type key: str
    :param container_name: The name of the container.
    :type container_name: str
    :param blob_name: the name of Blob to be deleted.
    :type blob_name: str
    
    """
    blob_service = BlockBlobService(account_name = account_name, account_key=key)
    if blob_service.exists(container_name=container_name, 
                           blob_name=blob_name):
            blob_service.delete_blob(container_name=container_name, 
                                     blob_name=blob_name)
            
def delete_all_in_storage(account_name, key, container_name):
    """
    Delete the all blobs in the storage.
    
    :param account_name: The name of the account.
    :type account_name: str
    :param key: The key to the storage account.
    :type key: str
    :param container_name: The name of the container.
    :type container_name: str
    :param blob_name: the name of Blob to be deleted.
    :type blob_name: str
    
    """
    blob_service = BlockBlobService(account_name = account_name, account_key=key)
    for blob in blob_service.list_blobs(container_name): 
        blob_service.delete_blob(container_name, blob.name)