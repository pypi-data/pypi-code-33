import pandas
import pyodbc
import re
from sqlparse import parse

from ftk.datasources import ForecastDataSource, SQLDataManager, DataTransformerMixin

class ForecastSQLDataSource(ForecastDataSource):
    """.
    The wrapper of the SQLDataSource, which returns the TimeSeriesDataFrame
    or ForecastDataFrame if it has the metadata.
    
    Forecast<StorageType>DataSource classes read data from external storage.
    Forecast<StorageType>DataSink classes write data to external storage.
    They are inherited from DataTransformerMixin which implements the abstract method transform() and exact methods fit(), fit_transform(), predict() from the Transformer interface.
    SQLDataManager abstracts out the database connection capability for both ForecastSQLDataSource and ForecastSQLDataSink, which inherit from it.
    ForecastDataSource and ForecastDataSink abstract reconstruction of TimeSeriesDataFrame from the pandas.DataFrame and serialization of TimeSeriesDataFrame
    back to pandas.DataFrame of given the metadata provided by user. If the metadata were not provided the plane pandas.DataFrame
    will be loaded or saved.
    The set of grain columns for filtering also can be provided.
    For example: transform(X=None, run_tag='run1', location=['Mars', 'Venus'], life_form=['mold'])
    will take only data with the tuples with values of location equal to Mars and Venus and life_form equals to mold.
    
    :param connection_str: The connection string used by pyodbc to connect to the database.
                           See the SQLDataTransformer.conn_string() method.
    :type connection_str: str
    :param time_colname: The time_colname to create TimeSeriesDataFrame.
    :type time_colname: str
    :param query: The SQL querty to be used to download the data.
                  NOTE there should be no unnamed columns in the query.
                  For example the query 
                  SELECT COUNT(1) FROM planets GROUP BY type
                  will result in error.
                  It should have alias for count field:
                  SELECT COUNT(1) as number_of_type FROM planets GROUP BY type
    :type query: str
    :param table: The table to retrieve.
    :type table: str
    :param grain_colnames: The grain colnames to create TimeSeriesDataFrame.
    :type grain_colnames: list
    :param ts_value_colname: The Time series value column name.
    :type ts_value_colname: str
    :param origin_time_colname: The column name for the origin time to create TimeSeriesDataFrame. 
    :type origin_time_colname: str
    :param pred_point: The point forecast column name. The metadata fore ForecastDataFrame. 
    :type pred_point: str
    :param pred_dist: The distribution forecast column name. The metadata fore ForecastDataFrame.
    :type pred_dist: str
    :param model_colnames: The name of model colname. The metadata fore MultiForecastDataFrame.
    :type model_colnames: list
    :param deduplicate: Deduplicate the index.
    :type deduplicate: bool
    :param run_tag: Run tag is an identifier of the pipeline run. If it is defined the table will be limited by the given run.
                    The run_tag column will be dropped from the output DataFrame.
                    Run identifier may not be longer then 255 symbols.
                    *Note* The run_tag used in the constructor is not used! Set run_tag in the transform method.
    :type run_tag: str
    :raises: ValueError
        
    """
    def __init__(self, 
                 sql_manager,
                 time_colname=None,
                 query=None,
                 table=None,
                 grain_colnames=None,
                 ts_value_colname=None,
                 origin_time_colname=None,
                 pred_point=None,
                 pred_dist=None,
                 model_colnames=None,
                 deduplicate=False,
                 run_tag=None,
                 value_filters={}):
        """Constructor.
        Create the instance of ForecastSQLDataSource. The query or table but not both should be filled out, otherwise the
        ValueError will be thrown.
        :param sql_manager: The SQLDataManager object to make connections to the database.
        :type sql_manager: SQLDataManager
        :param time_colname: The time_colname to create TimeSeriesDataFrame.
        :type time_colname: str
        :param query: The SQL querty to be used to download the data.
        :type query: str
        :param table: The table to retrieve.
        :type table: str
        :param grain_colnames: The grain colnames to create TimeSeriesDataFrame.
        :type grain_colnames: list
        :param ts_value_colname: The Time series value column name.
        :type ts_value_colname: str
        :param origin_time_colname: The column name for the origin time to create TimeSeriesDataFrame. 
        :type origin_time_colname: str
        :param pred_point: The point forecast column name. The metadata fore ForecastDataFrame. 
        :type pred_point: str
        :param pred_dist: The distribution forecast column name. The metadata fore ForecastDataFrame.
        :type pred_dist: str
        :param model_colnames: The name of model colname. The metadata fore MultiForecastDataFrame.
        :type model_colnames: list
        :param deduplicate: Deduplicate the index.
        :type deduplicate: bool
        :param run_tag:Run tag is an identifier of the pipeline run. If it is defined the table will be limited by the given run.
                       The run_tag column will be dropped from the output DataFrame.
                       Run identifier may not be longer then 255 symbols.
        :type run_tag: str
        :param value_filters: The dictionary of columns to be used for data set filtering: column_name->[list of grain to filter]
        :type value_filters: dict
        :raises: ValueError
        
        """
        
        if (query is None) == (table is None):
            raise ValueError("The query or table but not both should be provided.")
        if query:
            SQLDataManager.validate_query(query)
        self._query = query    
        if table:
            SQLDataManager.validate_name(table)
            self._query = "SELECT * from {}".format(table)
        self._sql_data_manager = sql_manager
        self._value_filters=value_filters
        super(ForecastSQLDataSource, self).__init__(time_colname = time_colname,
                                                    grain_colnames = grain_colnames or [],
                                                    ts_value_colname = ts_value_colname,
                                                    origin_time_colname = origin_time_colname,
                                                    pred_point = pred_point,
                                                    pred_dist = pred_dist,
                                                    model_colnames = model_colnames,
                                                    deduplicate=deduplicate,
                                                    run_tag=run_tag)
    
    @property
    def value_filters(self):
        """
        Set or get the dictionary of allowed grain columns. If it is None, all column values are allowed.
        
        :rtype: dict
        """
        return self._value_filters
    
    @value_filters.setter
    def value_filters(self, grains:dict):
        """
        Setter
        
        """
        self._value_filters = grains
        
    @property
    def query(self):
        """
          Return the query string.
          
          :rtype: str
          
        """
        return self._query 
    

    def load_data(self, X=None, **kwargs):    
        """
        Retrieve the data from the SQL database.
        If X is connection info, then ignore connection string
        provided in constructor and use that.
        The dictionary of columns and possible values also can be given for the purpose of data filtering.
        For example: transform(X=None, run_tag='run1', value_filters={'location':['Mars', 'Venus'], 'life_form':['mold'])
        will take only data with the value tuples having the location equal to Mars and Venus and life_form equals to mold. 
        
        :param X: Connection string.
        :type X: str
        :param run_tag: Run tag is an identifier of the pipeline run. If it is defined the table will be limited by the given run.
                        The run_tag column will be dropped from the output DataFrame.
                        Run identifier may not be longer then 255 symbols.
        :type run_tag: str
        :returns: the table with data.
        :rtype: pandas.DataFrame
        :raises: ValueError

        """
        DataTransformerMixin.check_run_tag(**kwargs)
        cnxn = None
        if not X is None and isinstance(X, str) and not re.match('DRIVER={.+};SERVER={.+};DATABASE={.+};UID={.+};PWD={.*}', X) is None:
            cnxn = pyodbc.connect(X)
        else:
            cnxn = pyodbc.connect(self._sql_data_manager.connection_str)
        
        query=self.query 
        if self.query[-1] == ';':
            query = query[:-1]
        kw_dict=dict(kwargs)
        #If we are filtering by the tag, add tag to the request.
        if kw_dict.get(DataTransformerMixin.TAG_VAR) and not re.search("^select\\s+[*]", query, re.IGNORECASE):
            sqlstatement=parse(query)[0]
            found_tag=False
            is_group_by=False
            found_group_tag=False
            #Go throug sql tokens and search for DataTransformerMixin.TAG_FIELD. If it is not there, add it.
            current_command=''
            for token in sqlstatement.tokens:
                #If we reached the FROM statement, no need to search further.
                if token.normalized in ('FROM', 'SELECT', 'GROUP', 'WHERE'):
                    current_command=token.normalized
                if token.normalized=='GROUP':
                    is_group_by=True
                if token.value=='*':
                    if current_command=='SELECT':
                        found_tag=True
                    elif current_command=='GROUP':
                        is_group_by=True
                #Look one level down. Do we have DataTransformerMixin.TAG_FIELD in the list?
                #The select column name is an IdentifierList which has child tokens.
                if token.is_group:
                    for idents in token.tokens:
                        if idents.value.lower()==DataTransformerMixin.TAG_FIELD.lower():
                            found_tag=found_tag or current_command=='SELECT'
                            found_group_tag= found_group_tag or current_command=='GROUP'
                            break
                if (current_command=='SELECT' or current_command=='GROUP') and token.value.lower()==DataTransformerMixin.TAG_FIELD.lower():
                    found_tag=found_tag or current_command=='SELECT'
                    found_group_tag= found_group_tag or current_command=='GROUP'
                if found_tag and (not is_group_by or found_group_tag):
                    break
            #If the token was not found, add it before FROM statement.
            if not found_tag:
                query = re.sub("\\s+from\\s+", ", {} from ".format(DataTransformerMixin.TAG_FIELD), query, flags=re.IGNORECASE)
            #If there was a GROUP BY statement and there were no RUN_TAG, add it to the statement.
            if is_group_by and not found_group_tag:
                query = re.sub("group by\\s+", " group by {}, ".format(DataTransformerMixin.TAG_FIELD), query, flags=re.IGNORECASE)
            
        clause_list = ['SELECT * FROM ({}) subquery '.format(query)]
        statement=parse(self.query)[0]
        params=[]
        #Filter data by run tag
        if 'value_filters' in kwargs.keys():
            self.value_filters=kwargs.get('value_filters')
        if kw_dict.get(DataTransformerMixin.TAG_VAR):
            # we will construct a list of query parameters called 'params', so that read_sql can fill them in.
            clause_list = self._add_where_or_and(clause_list, "{}=?".format(DataTransformerMixin.TAG_FIELD))
            params.append(kw_dict.get(DataTransformerMixin.TAG_VAR))
            del kw_dict[DataTransformerMixin.TAG_VAR]
        
        for k, v in self.value_filters.items():
            # we will construct a list of query parameters called 'params', so that read_sql can fill them in.
            for colval in v:
                params.append(colval)
            SQLDataManager.validate_name(k)
            str_val="({} IN ({}))".format(k, ", ".join(['?' for i in range(len(v))]))
            clause_list = self._add_where_or_and(clause_list, str_val)
       
        if params:
            data = pandas.read_sql(" ".join(clause_list), cnxn, params=tuple(params))
        else:
            data = pandas.read_sql(" ".join(clause_list), cnxn)
        
        if DataTransformerMixin.TAG_FIELD in list(data.columns.values):
            data = data.drop([DataTransformerMixin.TAG_FIELD], axis=1)
        return data
    
    def _add_where_or_and(self, query_list:list, condition:str):
        """
        Add the WHERE clause to the list if add_where is true,
        add AND to the end of list otherwise.
        
        :param query_list: Ther list to add the clause to.
        :type query_list: list
        :param condition: The condition to be added.
        :type condition: str
        :returns: The new list of expressions.
        :rtype: list
        """
        if len(query_list)==1:
            query_list.append("WHERE {}".format(condition))
        else:
            query_list.append("AND {}".format(condition))
        return query_list
        