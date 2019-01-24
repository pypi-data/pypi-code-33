# coding: utf-8

import os
import unittest

from tma import pool


class StockPoolTest(unittest.TestCase):
    def setUp(self):
        path = "test.pool"
        if os.path.exists(path):
            os.remove(path)
        self.pool = pool.StockPool(path)

    def tearDown(self):
        os.remove(self.pool.path)
        os.remove(self.pool.path_hist)

    def test_add(self):
        share = {
            "code": '600122',
            "name": '宏图高科',
            "level": '3',  # 1, 2, 3
            "date": "2018-05-27",  # 入选日期
            "reason": "sb",  # 入选理由
            "price": "20"  # 入选时的价格
        }
        self.pool.add(share)
        self.assertDictEqual(share, self.pool.level3['600122'][0])

    def test_add_many(self):
        shares = [
            {
                "code": '600122',
                "name": '宏图高科',
                "level": '1',  # 1, 2, 3
                "date": "2018-05-27",  # 入选日期
                "reason": "sb",  # 入选理由
                "price": "20"  # 入选时的价格
            },
            {
                "code": '600122',
                "name": '宏图高科',
                "level": '2',  # 1, 2, 3
                "date": "2018-05-27",  # 入选日期
                "reason": "sb",  # 入选理由
                "price": "20"  # 入选时的价格
            },
            {
                "code": '600122',
                "name": '宏图高科',
                "level": '3',  # 1, 2, 3
                "date": "2018-05-27",  # 入选日期
                "reason": "sb",  # 入选理由
                "price": "20"  # 入选时的价格
            },
            {
                "code": '600122',
                "name": '宏图高科',
                "level": '3',  # 1, 2, 3
                "date": "2018-05-27",  # 入选日期
                "reason": "sb",  # 入选理由
                "price": "20"  # 入选时的价格
            },
            {
                "code": '600122',
                "name": '宏图高科',
                "level": '3',  # 1, 2, 3
                "date": "2018-05-27",  # 入选日期
                "reason": "sb",  # 入选理由
                "price": "20"  # 入选时的价格
            }
        ]
        self.pool.add_many(shares)
        self.assertEqual(3, len(self.pool.level3['600122']))
        self.assertDictEqual(shares[0], self.pool.level1['600122'][0])
        self.assertDictEqual(shares[1], self.pool.level2['600122'][0])

    def test_remove(self):
        share = {
            "code": '600122',
            "name": '宏图高科',
            "level": '3',  # 1, 2, 3
            "date": "2018-05-27",  # 入选日期
            "reason": "sb",  # 入选理由
            "price": "20"  # 入选时的价格
        }
        self.pool.add(share)
        self.assertDictEqual(share, self.pool.level3['600122'][0])
        self.pool.remove(code='600122', level='3')
        self.assertEqual(self.pool.level3, {})

    def test_empty(self):
        shares = [
            {
                "code": '600122',
                "name": '宏图高科',
                "level": '1',  # 1, 2, 3
                "date": "2018-05-27",  # 入选日期
                "reason": "sb",  # 入选理由
                "price": "20"  # 入选时的价格
            },
            {
                "code": '600122',
                "name": '宏图高科',
                "level": '2',  # 1, 2, 3
                "date": "2018-05-27",  # 入选日期
                "reason": "sb",  # 入选理由
                "price": "20"  # 入选时的价格
            },
            {
                "code": '600122',
                "name": '宏图高科',
                "level": '3',  # 1, 2, 3
                "date": "2018-05-27",  # 入选日期
                "reason": "sb",  # 入选理由
                "price": "20"  # 入选时的价格
            },
            {
                "code": '600122',
                "name": '宏图高科',
                "level": '3',  # 1, 2, 3
                "date": "2018-05-27",  # 入选日期
                "reason": "sb",  # 入选理由
                "price": "20"  # 入选时的价格
            },
            {
                "code": '600122',
                "name": '宏图高科',
                "level": '3',  # 1, 2, 3
                "date": "2018-05-27",  # 入选日期
                "reason": "sb",  # 入选理由
                "price": "20"  # 入选时的价格
            }
        ]
        self.pool.add_many(shares)
        self.pool.empty()
        self.assertEqual(self.pool.level3, {})
        self.assertEqual(self.pool.level2, {})
        self.assertEqual(self.pool.level1, {})
        # self.assertEqual(self.pool.is_empty(), True)

if __name__ == "__main__":
    unittest.main()
