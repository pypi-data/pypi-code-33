import unittest
from looqbox.database.database_functions import looq_sql_in, looq_sql_between


class TestSQLIn(unittest.TestCase):

    def test_sql_in(self):
        """
        Test looq_sql_in function
        """
        par1 = [1, 2, 3, 4, 5]
        query1 = "select * from database where 1=1 " + looq_sql_in("and par1 in", par1)
        correct_query1 = "select * from database where 1=1 and par1 in (1, 2, 3, 4, 5)"

        par2 = [1, 2, 3]
        par3 = 1
        query2 = "select * from database where 1=1 " + looq_sql_in("and par2 in", par2) + \
                 looq_sql_in(" and par3 in", par3)
        correct_query2 = "select * from database where 1=1 and par2 in (1, 2, 3) and par3 in (1)"

        self.assertEqual(query1, correct_query1)
        self.assertEqual(query2, correct_query2)

    def test_sql_between(self):
        """
        Test looq_sql_between function
        """
        par1 = [1, 2]
        query1 = "select * from database where 1=1" + looq_sql_between(" and par1", par1)
        correct_query1 = "select * from database where 1=1 and par1 between 1 and 2"

        par2 = ['2018-01-01', '2018-02-02']
        query2 = "select * from database where 1=1" + looq_sql_between(" and date", par2)
        correct_query2 = "select * from database where 1=1 and date between '2018-01-01' and '2018-02-02'"

        par3 = ['2018-01-01']
        par4 = [1, 2, 3, 4]
        self.assertEqual(query1, correct_query1)
        self.assertEqual(query2, correct_query2)
        with self.assertRaises(Exception):
            "select * from database where 1=1" + looq_sql_between(" and date", par3)
            "select * from database where 1=1" + looq_sql_between(" and date", par4)

