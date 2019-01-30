# -*- coding: utf-8 -*-
"""
TestRequest
"""
import json
import pytest
import pyprimed

from pyprimed.exceptions import ServerError


@pytest.mark.unit
class TestRequest:
	def test_unallowed_method(self, pio):
		from pyprimed.exceptions import MethodNotAllowedExpection
		with pytest.raises(MethodNotAllowedExpection):
			pio.models.upsert([])
