# coding:utf-8
from tablestore import *
import sys
class otsapi(object):
    def __init__(self,ots_endpoint,ots_id,ots_secret,ots_instance):
        self.client = OTSClient(ots_endpoint, ots_id, ots_secret, ots_instance)

    def update_row(self,table_name,k,v,function ="PUT"):
        '''
        更新某行数据的具体列
        :param k: [('gid',1), ('uid',"101")]
        :param v:[('name', 'David'), ('address', 'Hongkong')]
        :param:function:PUT,DELETE,DELETE_ALL

        :return:
        '''
        primary_key = k
        update_of_attribute_columns = {
            function: v,
        }
        row = Row(primary_key, update_of_attribute_columns)
        condition = Condition(RowExistenceExpectation.IGNORE, SingleColumnCondition(k[0][0], k[0][1],
                                                                                    ComparatorType.EQUAL))  # update row only when this row is exist
        consumed, return_row = self.client.update_row(table_name, row, condition)
        print('Update succeed, consume %s write cu.' % consumed.write)

    def get_row(self,table_name,primary_key,columns_to_get):
        '''

        :param table_name:
        :param primary_key:[('gid', 1), ('uid', '101')]
        :param columns_to_get :['name', 'address',
                          'age'] # given a list of columns to get, or empty list if you want to get entire row.
        :return:返回具体的列数据
        '''

        consumed, return_row, next_token = self.client.get_row(table_name, primary_key, columns_to_get, None, 1)
        print('Read succeed, consume %s read cu.' % consumed.read)

        print('Value of attribute: %s' % return_row.attribute_columns)
        return return_row.attribute_columns

    def batch_get_row(self,table_name,rows_to_get,columns_to_get,):
        '''
        批量读
        :param table_name:
        :param rows_to_get: [[('gid', i)],[('gid', 2)]]
        :param columns_to_get: ['name', 'mobile', 'address', 'age']
        :return:
        '''
        # try get 10 rows from exist table and 10 rows from not-exist table
        # rows_to_get = []
        # for i in range(0, 10):
        #     primary_key = [('gid', i), ('uid', i + 1)]
        #     rows_to_get.append(primary_key)

        # cond = CompositeColumnCondition(LogicalOperator.AND)
        # cond.add_sub_condition(SingleColumnCondition("name", "John", ComparatorType.EQUAL))
        # cond.add_sub_condition(SingleColumnCondition("address", 'China', ComparatorType.EQUAL))

        request = BatchGetRowRequest()
        request.add(TableInBatchGetRowItem(table_name, rows_to_get, columns_to_get, max_version=1))
        result = self.client.batch_get_row(request)

        print('Result status: %s' % (result.is_all_succeed()))

        table_result_0 = result.get_result_by_table(table_name)


        print('Check first table\'s result:')
        for item in table_result_0:
            if item.is_ok:
                print(
                    'Read succeed, PrimaryKey: %s, Attributes: %s' % (item.row.primary_key, item.row.attribute_columns))
            else:
                print('Read failed, error code: %s, error message: %s' % (item.error_code, item.error_message))



    def put_row(self,table_name,primary_key,attribute_columns):
        '''

        :param primary_key: [('gid', 1), ('uid', 101)]
        :param attribute_columns: [('name', '萧峰'), ('mobile', 15100000000), ('address', bytearray('China')),
                             ('female', False), ('age', 29.7)]
        :return:
        '''

        row = Row(primary_key, attribute_columns)

        condition = Condition(RowExistenceExpectation.EXPECT_NOT_EXIST,
                              SingleColumnCondition(primary_key[0][0], primary_key[0][1], ComparatorType.EQUAL))
        consumed, return_row = self.client.put_row(table_name, row, condition)
        print(u'Write succeed, consume %s write cu.' % consumed.write)
        return consumed.write

    def batchwriterow(self,table_name,primary_keylist,attribute_columnslist):
        '''

        :param table_name:
        :param primary_keylist: 二维数组，每个数组中是主键值对
        :param attribute_columnslist: 二维数组，每个数组中是要写入的col数据
        :return:
        '''
        put_row_items=[]
        for i in range(primary_keylist.__len__()):
            row = Row(primary_keylist[i], attribute_columnslist[i])
            condition = Condition(RowExistenceExpectation.IGNORE)
            item = PutRowItem(row, condition)
            put_row_items.append(item)
        try:
            req = BatchWriteRowRequest()
            req.add(TableInBatchWriteRowItem(table_name, put_row_items))

            result = self.client.batch_write_row(req)
        except:
            return False
        else:

            print('Result status: %s' % (result.is_all_succeed()))
            print('check first table\'s put results:')
            succ, fail = result.get_put()
            succcount = 0
            failcount = 0
            for item in succ:
                succcount += 1
            for item in fail:
                failcount +=1
            if failcount ==0 :
                return True
            else:
                print("success:%d,fail:%d" %(succcount,failcount))
                return False
    def batchupdaterow(self,table_name,primary_keylist,attribute_columnslist):
        '''
        批量更新
        :param table_name:
        :param primary_keylist: 二维数组，每个数组中是主键值对
        :param attribute_columnslist: 二维数组，每个数组中是要写入的col数据
        :return:
        '''
        put_row_items=[]
        for i in range(primary_keylist.__len__()):
            attribute_columns={'put':attribute_columnslist[i]}
            row = Row(primary_keylist[i], attribute_columns)
            condition = Condition(RowExistenceExpectation.IGNORE)
            item = UpdateRowItem(row, condition)
            put_row_items.append(item)
        try:
            req = BatchWriteRowRequest()
            req.add(TableInBatchWriteRowItem(table_name, put_row_items))

            result = self.client.batch_write_row(req)
        except:
            print(sys.exc_info())
            return False
        else:

            print('Result status: %s' % (result.is_all_succeed()))
            print('check first table\'s put results:')
            succ, fail = result.get_put()
            succcount = 0
            failcount = 0
            for item in succ:
                succcount += 1
            for item in fail:
                failcount +=1
            if failcount ==0 :
                return True
            else:
                print("success:%d,fail:%d" %(succcount,failcount))
                return False



