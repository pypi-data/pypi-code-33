# -*- coding: utf-8 -*-
"""
TestResource
"""
import pytest
import pyprimed


@pytest.mark.unit
class TestRelationshipCollection:

    def test_nonnested_path(self, pio):
        model = pyprimed.models.model.Model(parent=pio, uid="xyz")
        universe = pyprimed.models.universe.Universe(parent=pio, uid="123")

        assert pio\
            .predictions\
            .on(model=model, universe=universe)\
            .path == "predictions?model.uid=xyz&universe.uid=123"


@pytest.mark.unit
class TestUsingRelationshipCollection:

    def test_using(self, monkeypatch, pio):
        model = pyprimed.models.model.Model(parent=pio, uid="xyz")
        universe = pyprimed.models.universe.Universe(parent=pio, uid="123")

        def mockmember(*args, **kwargs):
            assert args == (1,2,3)

        monkeypatch.setattr(universe.targets, 'upsert', mockmember)

        pio\
            .predictions\
            .on(model=model, universe=universe)\
            .using(*[1,2,3])
