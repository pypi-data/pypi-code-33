# -*- coding: utf-8 -*-
"""
TestHierarchyHelper
"""
import pytest
import pyprimed

@pytest.mark.unit
class TestHierarchyHelper:
	def test_collect_ancestors(self):
		from pyprimed.models.base import HierarchyHelper
		
		class MyParent(HierarchyHelper):
			def __init__(self, parent):
				self._parent = parent

		class MyChild(HierarchyHelper):
			def __init__(self, parent):
				self._parent = parent

		class MyGrandChild(HierarchyHelper):
			def __init__(self, parent):
				self._parent = parent

		P = MyParent(parent=None)
		C = MyChild(parent=P)
		G = MyGrandChild(parent=C)

		assert len(P._collect_ancestors()) == 1
		assert P._collect_ancestors()[0] is P
		
		assert len(C._collect_ancestors()) == 2
		assert C._collect_ancestors()[0] is P
		assert C._collect_ancestors()[1] is C

		assert len(G._collect_ancestors()) == 3
		assert G._collect_ancestors()[0] is P
		assert G._collect_ancestors()[1] is C
		assert G._collect_ancestors()[2] is G