#! /usr/bin/python
# -*- coding: utf-8 -*-
'''
Created on 2014年7月22日

@author: zhouzhichao
'''

from polynome import Polynome
import unittest

class TestPolynome(unittest.TestCase):
	def setUp(self):
		print "setUp TestPolynome test case."
	def tearDown(self):
		print "tearDown TestPolynome test case."
	def test_mul(self):
		p1, p2 = Polynome(value="1010110101011"), Polynome(value="1010101011")
		p = p1.mul(p2)
		print p1.order, p2.order
		print p1.printf(),p2.printf(),p.printf()

	def test_printf(self):
		value = "1010110101011"
		polynome = "x^12+x^10+x^8+x^7+x^5+x^3+x^1+x^0"

		p = Polynome(value=value)
		self.assertEqual(value, p.printf())
		self.assertEqual(value, p.printf(binary=True))
		self.assertEqual(polynome, p.printf(polynome=True))
		self.assertEqual(value, p.printf(polynome=True, binary=True))
		self.assertEqual(value[::-1], p.printf(binary=True, desc=True))
		self.assertEqual(value[::-1], p.printf(desc=True))
		self.assertEqual("+".join(polynome.split("+")[::-1]), p.printf(polynome=True, desc=True))

		p = Polynome(order=12)
		value = "0"*12
		polynome = ""

		self.assertEqual(value, p.printf())
		self.assertEqual(value, p.printf(binary=True))
		self.assertEqual(polynome, p.printf(polynome=True))
		self.assertEqual(value, p.printf(polynome=True, binary=True))
		self.assertEqual(value[::-1], p.printf(binary=True, desc=True))
		self.assertEqual(value[::-1], p.printf(desc=True))
		self.assertEqual("+".join(polynome.split("+")[::-1]), p.printf(polynome=True, desc=True))

if __name__ == '__main__': 
	unittest.main()