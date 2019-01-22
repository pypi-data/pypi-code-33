import sqlalchemy as sa

from ..config import Base



class ModelFieldTypes(Base):
    __tablename__ = 'model_field_types'
    
    id = sa.Column(sa.Integer, primary_key=True)
    
    binary_1 = sa.Column('new_binary_1', sa.Binary, nullable=True)
    binary_2 = sa.Column('new_binary_2', sa.BINARY, nullable=True)
    binary_3 = sa.Column('new_binary_3', sa.LargeBinary, nullable=True)
    binary_4 = sa.Column('new_binary_4', sa.VARBINARY, nullable=True)
    
    string_1 = sa.Column('new_string_1', sa.String, nullable=True)
    string_2 = sa.Column('new_string_2', sa.Unicode, nullable=True)
    string_3 = sa.Column('new_string_3', sa.VARCHAR, nullable=True)
    string_4 = sa.Column('new_string_4', sa.NVARCHAR, nullable=True)
    string_5 = sa.Column('new_string_5', sa.CHAR, nullable=True)
    string_6 = sa.Column('new_string_6', sa.NCHAR, nullable=True)
    
    text_1 = sa.Column('new_text_1', sa.Text, nullable=True)
    text_2 = sa.Column('new_text_2', sa.TEXT, nullable=True)
    text_3 = sa.Column('new_text_3', sa.UnicodeText, nullable=True)
    text_4 = sa.Column('new_text_4', sa.CLOB, nullable=True)
    
    integer_1 = sa.Column('new_integer_1', sa.Integer, nullable=True)
    integer_2 = sa.Column('new_integer_2', sa.INT, nullable=True)
    integer_3 = sa.Column('new_integer_3', sa.INTEGER, nullable=True)
    integer_4 = sa.Column('new_integer_4', sa.BigInteger, nullable=True)
    integer_5 = sa.Column('new_integer_5', sa.BIGINT, nullable=True)
    integer_6 = sa.Column('new_integer_6', sa.SmallInteger, nullable=True)
    integer_7 = sa.Column('new_integer_7', sa.SMALLINT, nullable=True)
    
    boolean_1 = sa.Column('new_boolean_1', sa.Boolean, nullable=True)
    boolean_2 = sa.Column('new_boolean_2', sa.BOOLEAN, nullable=True)
    
    float_1 = sa.Column('new_float_1', sa.Float, nullable=True)
    float_2 = sa.Column('new_float_2', sa.FLOAT, nullable=True)
    float_3 = sa.Column('new_float_3', sa.REAL, nullable=True)
    float_4 = sa.Column('new_float_4', sa.DECIMAL, nullable=True)
    float_5 = sa.Column('new_float_5', sa.Numeric, nullable=True)
    float_6 = sa.Column('new_float_6', sa.NUMERIC, nullable=True)
    
    date_1 = sa.Column('new_date_1', sa.Date, nullable=True)
    date_2 = sa.Column('new_date_2', sa.DATE, nullable=True)
    
    time_1 = sa.Column('new_time_1', sa.Time, nullable=True)
    time_2 = sa.Column('new_time_2', sa.TIME, nullable=True)
    
    datetime_1 = sa.Column('new_datetime_1', sa.DateTime, nullable=True)
    datetime_2 = sa.Column('new_datetime_2', sa.DATETIME, nullable=True)
    datetime_3 = sa.Column('new_datetime_3', sa.TIMESTAMP, nullable=True)
    


