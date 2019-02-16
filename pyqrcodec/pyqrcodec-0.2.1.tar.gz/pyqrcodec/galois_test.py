#! /usr/bin/python
# -*- coding: utf-8 -*-
'''
Created on 2014年7月22日

@author: zhouzhichao
'''

from galois import GaloisField 
import unittest

class TestGaloisField(unittest.TestCase):
    @staticmethod
    def setUpClass():
        print "setUp TestGaloisField unittest."
        TestGaloisField.GF = GaloisField(module= 0x11d)
    @staticmethod
    def tearDownClass():
        print "tearDown TestGaloisField unittest."
    def setUp(self):
        print "setUp TestGaloisField test case."
    def tearDown(self):
        print "tearDown TestGaloisField test case."

    def test_mul(self):
        for i in xrange(1,256):
            print map(lambda x: TestGaloisField.GF.getValue(x), self.getRates(i))#self.getRates(i)

    def getRates(self, pn):
        if pn < 1: return    
        result = [0] * (pn + 1)
    
        for k in xrange(1, pn):
            for i in xrange(k, 0, -1):
                result[i] = TestGaloisField.GF.add(result[i] + k, result[i-1])
            result[0] += k
        result[0] = TestGaloisField.GF.mod(result[0])
        return result   
    
if __name__ == "__main__":
    unittest.main()