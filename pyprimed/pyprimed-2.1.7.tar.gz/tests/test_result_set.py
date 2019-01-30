# -*- coding: utf-8 -*-
"""
Test ResultSet class
"""
import json
import pytest
import pyprimed
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/../")

from pyprimed.models.resultset import ResultSet, RangeParsingFailure


@pytest.mark.unit
class TestResultSet:
    def test_all(self, monkeypatch, pio):
        def mockrequest(path, params):
            assert path == "models"
            assert params == {"range": "[10, 20]", "sort": '["name", "DESC"]'}

            models = [
                {"name": "model-{i}".format(i=i), "uid": "1"} for i in range(10, 20)
            ]
            return (models, "models 10-20/100")

        monkeypatch.setattr(pio._client, "all", mockrequest)
        result_set = pio.models.all(range=[10, 20], sort=["name", "DESC"])

        assert result_set._page_start == 10
        assert result_set._page_end == 20
        assert result_set._page_size == 10
        assert len(result_set) == 100

        assert result_set[10].name == "model-10"
        assert result_set[19].name == "model-19"

    def test_filter(self, monkeypatch, pio):
        def mockrequest(path, params):
            assert path == "models"
            assert params == {
                "filter": '{"name__starts_with": "model"}',
                "range": "[15, 25]",
                "sort": '["name", "ASC"]',
            }

            models = [
                {"name": "model-{i}".format(i=i), "uid": "1"} for i in range(15, 25)
            ]
            return (models, "models 15-25/50")

        monkeypatch.setattr(pio._client, "filter", mockrequest)
        result_set = pio.models.filter(
            name__starts_with="model", range=[15, 25], sort=["name", "ASC"]
        )

        assert result_set._page_start == 15
        assert result_set._page_end == 25
        assert result_set._page_size == 10
        assert len(result_set) == 50

        assert result_set[15].name == "model-15"
        assert result_set[24].name == "model-24"

    def test_slicing(self, monkeypatch, pio):
        def mockrequest(path, params):
            assert path == "models"
            assert params == {"range": "[10, 20]", "sort": '["name", "DESC"]'}

            models = [
                {"name": "model-{i}".format(i=i), "uid": "1"} for i in range(10, 20)
            ]
            return (models, "models 10-20/100")

        monkeypatch.setattr(pio._client, "all", mockrequest)
        result_set = pio.models.all(range=[10, 20], sort=["name", "DESC"])

        for idx, model in enumerate(result_set[13:17]):
            assert model.name == "model-{i}".format(i=(13 + idx))

        assert len(result_set[13:17]) == 4

    def test_page_change(self, monkeypatch, pio):
        def mockrequest(path, params):
            start, end = eval(params["range"])
            models = [
                {"name": "model-{i}".format(i=i), "uid": "1"} for i in range(start, end)
            ]

            return (models, "models {start}-{end}/100".format(start=start, end=end))

        monkeypatch.setattr(pio._client, "all", mockrequest)
        result_set = pio.models.all(range=[10, 20], sort=["name", "DESC"])

        assert result_set._page_start == 10
        assert result_set._page_end == 20

        assert result_set[55].name == "model-55"
        assert result_set._page_start == 50
        assert result_set._page_end == 60

    def test_parse_range(self):
        parsed = ResultSet.parse_range("targets 0-10/100")

        assert parsed[0] == 0
        assert parsed[1] == 10
        assert parsed[2] == 100

        with pytest.raises(RangeParsingFailure):
            parsed = ResultSet.parse_range("")
