from MysqlFunk import MysqlFunk

dbconfig = {
        'user': 'main',
        'password': '',
        'host': '127.0.0.1',
        'database': 'army_knife'
            }

test = MysqlFunk(**dbconfig)

insert = "insert into test (date_time,text,text2) values (now(),'test','test')"
test.commit_statement(insert)

select = "select * from test"
results = test.query_statement(select)

for result in results:
    print(result)