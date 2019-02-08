import ast
import pandas as pd
import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.postgresql import ARRAY, DOUBLE_PRECISION, NUMERIC, TEXT, BIGINT, FLOAT
import oedialect
import requests
import getpass
from test.login import OED_CREDS
print("imports complete")

# Create Engine:
OED_STRING = 'postgresql+oedialect://{creds}'.format(creds=OED_CREDS)

engine = sa.create_engine(OED_STRING)
metadata = sa.MetaData(bind=engine)

table_name = 'a_dataframe_test_martin'
schema_name = 'model_draft'


# define table
ExampleTable = sa.Table(
    table_name,
    metadata,
    sa.Column('idee', BIGINT),
    sa.Column('ct_curve', TEXT), #ARRAY(FLOAT)),
    sa.Column('source', TEXT),
    schema=schema_name
)

# create table
conn = engine.connect()
print('Connection established')
print('Creating table...')
try:
    if not engine.dialect.has_table(conn, table_name, schema_name):
        ExampleTable.create()
    else:
        print('Table already exists. skipping')
except:
    raise
    print("whoop. Table creation didn't go as planned")
finally:
    conn.close()



wind_powercurves_df = pd.read_csv('blubb.csv', encoding='utf8', sep=',')
def squareBrackets(curlyString):
    squareString = curlyString.replace('{', '[').replace('}',']')
    return(str(ast.literal_eval(squareString)))

wind_powercurves_df['ct_curve'] = wind_powercurves_df['ct_curve'].apply(squareBrackets)
#print(wind_powercurves_df)


'''
Session = sessionmaker(bind=engine)
session = Session()
print('inserting...')
try:
    insert_statement = ExampleTable.insert().values(
        [
            dict(idee=19, ct_curve=pd.Series([[1,2,3,4,5], [2,3,4,5,6], [2,3,4,5,6], [2,3,4,5,6]]), source = 'Q')
            #dict(source = 'Q')
            #dict(ct_curve=pd.Series([1,2,3]).values)
        ]
    )
    session.execute(insert_statement)
    session.commit()
    print('Insert successful!')
except Exception as e:
    session.rollback()
    raise
    print('Insert incomplete!')
finally:
    session.close()
'''

conn = engine.connect()
print("try to write to database")
try: 
    wind_powercurves_df.to_sql(table_name, conn, schema=schema_name, if_exists='replace')
    print('Inserted to ' + table_name + ' :)')
except:
    raise
    print('Insert incomplete!')
finally:
    conn.close()


# read table from db
Session = sessionmaker(bind=engine)
session = Session()
a = '✕'
try:
    print('attempting to print content of table from data base')
    a = session.query(ExampleTable).all()
except Exception as e:
    session.rollback()
    print('Reading from data base failed :(')
    print(a)
finally:
    session.close()
