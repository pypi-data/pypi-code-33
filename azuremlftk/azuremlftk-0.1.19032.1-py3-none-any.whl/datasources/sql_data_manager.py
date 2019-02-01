import re
from enum import Enum
from builtins import isinstance

import pyodbc

class SQLDataManager(object):
    """
      An abstract class describing sklearn transformers which can write or read from the data base.
      If the connection string does not contain required fields the ValueError is raised.
    
      :param server: The domain name of a server.
      :type server: str
      :param database: The name of the database.
      :type database: str
      :param user: The user name to authenticate to the server.
      :type user: str
      :param password: The password used to authenticate to server.
      :type password: str
      :param driver: The pyodbc driver to the database.
      :type driver: str
      :raises: ValueError.
      
    """
    RE_NAME = re.compile(r"^[A-Za-z][\w@$#]{0,127}$")
    RE_QUERY = re.compile("\\s*(alter table )|(drop table )|(update )|(delete from )")
    
    @staticmethod
    def conn_string(server,
                    database,
                    user,
                    password,
                    driver = 'SQL Server'
                    ):
        """
        Construct the pyodbc connection string.
        
        :param server: The domain name of a server.
        :type server: str
        :param database: The name of the database.
        :type database: str
        :param user: The user name to authenticate to the server.
        :type user: str
        :param password: The password used to authenticate to server.
        :type password: str
        :param driver: The pyodbc driver to the database.
        :type driver: str
        :returns: The pyodbc connection string.
        :rtype: str
        
        """
        templ_str = 'DRIVER={{{}}};SERVER={{{}}};DATABASE={{{}}};UID={{{}}};PWD={{{}}}'
        return templ_str.format(driver, server, database, user, password)

    def __init__(self, 
                 server,
                 database,
                 user,
                 password,
                 dialect = 'mssql',
                 driver = 'SQL Server'):
        """
        Construct a data SQL transformer.
        If the connection string does not contain required fields the ValueError is raised.
        
        :param server: The domain name of a server.
        :type server: str
        :param database: The name of the database.
        :type database: str
        :param user: The user name to authenticate to the server.
        :type user: str
        :param password: The password used to authenticate to server.
        :type password: str
        :param dialect: The sqlalchemy dialect+driver. The default is mssql+pyodbc
                        other possible drivers are: mysql, oracle, mssql+pymssql, sqlite, postgresql.
        :type dialect: str
        :param driver: The pyodbc driver to the database.
        :type driver: str
        
        :raises: ValueError.
        """
        self._driver = driver
        self._dialect = dialect
        self._server = server
        self._database = database
        self._user = user
        self._password = password
        self._connection_str = SQLDataManager.conn_string(server, database, user, password, driver)
    
    def get_connection(self, X):
        """
          If X is connection info, then ignore connection string
          provided in constructor and use that.
          
          :param X: Connection string.
          :type X: str
          :returns: the connection to data base.
          :rtype: Connection
          
        """
        cnxn = None
        if not X is None and isinstance(X, str) and not re.match('DRIVER={.+};SERVER={.+};DATABASE={.+};UID={.+};PWD={.*}', X) is None:
            cnxn = pyodbc.connect(X)
        else:
            cnxn = pyodbc.connect(self.connection_str)
        return cnxn
      
    @property
    def connection_str(self):
        """The connection string to the database.
        :getter: return connection string.
        :type: str
        
        """
        return self._connection_str
    
    @property
    def driver(self):
        """The driver.
        :getter: return driver.
        :type: str
        
        """
        return self._driver
     
    @property
    def server(self):
        """The server.
        :getter: return server.
        :type: str
        
        """
        return self._server
     
    @property
    def database(self):
        """The database.
        :getter: return database.
        :type: str
        
        """
        return self._database
         
    @property
    def user(self):
        """The user name.
        :getter: return user name.
        :type: str
        
        """
        return self._user
     
    @property    
    def password(self):
        """The password.
        :getter: return password.
        :type: str
        
        """
        return self._password

    @property
    def dialect(self):
        """The dialect.
        :getter: return a sqlalchemy dialect.
        :type: str
        
        """
        return self._dialect 
        
    @staticmethod
    def drop_table(table_name:str, connection_str:str):
        """
          Delete the table with the name table_name.
          Raise Value error if table name contains wrong symbols.
          
          :param table_name: The name of a table ton be deleted.
          :type table_name: str
          :param connection_str: The connection string.
          :type connection_str: str
          :raises: ValueError
          
        """
        SQLDataManager.validate_name(table_name)
        cnxn = pyodbc.connect(connection_str)
        cursor = cnxn.cursor()
        cursor.execute("DROP TABLE {};".format(table_name))
        cnxn.commit()
        
    @staticmethod
    def drop_if_exists(table_name:str, database:str, connection_str:str):
        """
          Delete the table with the name table_name if any.
          Raise Value error if the database or table name contains wrong symbols.
           
          :param table_name: The name of a table ton be deleted.
          :type table_name: str
          :param database: The database fort table lookup.
          :type database: str
          :param connection_str: The connection string.
          :type connection_str: str
          :raises: ValueError
          
        """
        if SQLDataManager.is_table_present(table_name, database, connection_str):
            SQLDataManager.drop_table(table_name, connection_str)
            
    @staticmethod
    def is_table_present(table_name:str, database:str, connection_str:str):
        """
          Return if the table with name table_name is present in the database.
          Raise Value error if the database name contains wrong symbols. 
           
          :param table_name: The name of a table ton be deleted.
          :type table_name: str
          :param database: The database fort table lookup.
          :type database: str
          :param connection_str: The connection string.
          :type connection_str: str
          :returns: if table is present.
          :rtype: bool
          :raises: ValueError
          
        """
        SQLDataManager.validate_name(database)
        tbl_query = "SELECT TABLE_NAME FROM {}.INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE' AND TABLE_NAME = ?".format(database)
        cnxn = pyodbc.connect(connection_str)
        cursor = cnxn.cursor()
        cursor.execute(tbl_query, (table_name))
        row = cursor.fetchone()
        return not row is None
    
    @staticmethod
    def create_table(table_name:str, data_types:dict, connection_str:str):
        """
        Create table with the name table_name.
        Raise ValueError if the name of table, field or type of variable contains the wrong character
        or if variable type contains semicolon.
         
        :param table_name: The name of a table ton be deleted.
        :type table_name: str
        :param data_types: The dictionary with data types field->data type.
        :type data_types: dict
        :param connection_str: The connection string.
        :type connection_str: str
        :raises: ValueError
 
        """
        cnxn = pyodbc.connect(connection_str)
        cursor = cnxn.cursor()
        SQLDataManager.validate_name(table_name)
        types_list = []
        for k, v in data_types.items():
            SQLDataManager.validate_name(k)
            if v.find(';')!=-1:
                raise ValueError('Invalid variable name {}'.format(v))
            types_list.append("{} {}".format(k, v))
        cursor.execute("CREATE TABLE {}(\n{}\n);".format(table_name, ",\n".join(types_list)))
        cnxn.commit()
    
    @staticmethod
    def _drop_tables_by_substring(database:str, substring:str, connection:str, table_schema:str='dbo'):
        """
        Delete ALL tables, containing given substring.
        WARNING! Deletes ALL tables whose name contains the given substring. Use with care.
        Raise Value error if the database name contains wrong symbols or if substring contains semicolon. 
        
        :param database: The database for table lookup.
        :type database: str
        :param substring: the tables containing given substring in name will be deleted.
        :type: substring: str
        :param connection_str: The connection string.
        :type connection_str: str
        :param table_schema: The schema to delete table from.
        :type table_schema: str
        :raises: ValueError
        
        """
        SQLDataManager.validate_name(database)
        if substring.find(';')!=-1:
            raise ValueError('Invalid variable name {}'.format(substring))
        tbl_query = ("SELECT TABLE_NAME FROM {}.INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = "
                     "'BASE TABLE' AND TABLE_SCHEMA = ? AND TABLE_NAME LIKE '%{}%'".format(database, substring))
        cnxn = pyodbc.connect(connection)
        cursor = cnxn.cursor()
        cursor.execute(tbl_query,  (table_schema,))
        rows = cursor.fetchall()
        for row in rows:
            SQLDataManager.drop_table(row[0], connection)
            
    @staticmethod
    def validate_name(name:str):
        """
        Check if the name is valid. If the name is not valid, the value error is raised.
        
        :param name: the name of database or table field.
        :type database: str
        :raises: ValueError
        """
        if not SQLDataManager.RE_NAME.match(name.strip()):
            raise ValueError('Wrong name {}'.format(name))
        
    @staticmethod
    def validate_query(query:str, error_text:str=None):
        """
        Check if the query contains the unexpected commands as DROP TABLE, ALTER TABLE, or UPDATE.
        If the data manipulation words were found the query considered to be invalid and ValueError 
        is raised.
        
        :param query: The query to be validated.
        :type query: str
        :param error_text: The test to be shown if exception is raised.
        :type error_text: str
        :raises: ValueError
        
        """
        if SQLDataManager.RE_QUERY.search(query.lower()):
            if error_text is None:
                raise ValueError("The query {} contains unexpected statement.".format(query))
            else:
                raise ValueError(error_text)
        