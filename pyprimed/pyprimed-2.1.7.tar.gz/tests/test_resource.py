# -*- coding: utf-8 -*-
"""
TestResource
"""
import pytest
import pyprimed

@pytest.mark.unit
class TestResource:
    def test_nonnested_uri(self, pio):
        model = pyprimed.models.model.Model(parent=pio.models, uid="xyz")
        assert model.uri == "models/xyz"

    def test_nested_uri(self, pio):
        model = pyprimed.models.model.Model(parent=pio.models, uid="xyz")
        signal = pyprimed.models.signal.Signal(parent=model.signals, uid="123")
        assert signal.uri == "signals/123"

    def test_refresh(self, monkeypatch, pio):
        def mockrequest(*args, **kwargs):
            assert kwargs['operation'] == 'GET'
            assert kwargs['path'] == 'models/xyz'

            return {
                'uid': '8d55c3f929e846529e9a8ad7cfed4e04',
                'name': 'cbf',
                'description': 'cbf_model',
                'created_at': '2018-07-03T11:34:35.506575+00:00',
                'num_signals': 10,
                'num_predictions': 30,
                'max_signals_threshold': 1000,
                'owner': {
                    'uid': 'c9993b671ce842d48f0afe5c135268d6'
                },
                'abvariants': [
                    {
                    'uid': '6ad7cb45eef24d74b42a8cc7e939cd4f',
                    'weight': 0.9
                    }
                ]
            }

        monkeypatch.setattr(pio, '_dispatch_request', mockrequest)

        model = pyprimed.models.model.Model(parent=pio.models, uid='xyz',
            name='name', description='description', created_at='1',
            num_signals=0, num_predictions=0, max_signals_threshold=0)
        model._refresh()

        assert model.uid == '8d55c3f929e846529e9a8ad7cfed4e04'
        assert model.name == 'cbf'
        assert model.description == 'cbf_model'
        assert model.created_at == '2018-07-03T11:34:35.506575+00:00'
        assert model.num_signals == 10
        assert model.num_predictions == 30
        assert model.max_signals_threshold == 1000
        assert model.owner == {'uid': 'c9993b671ce842d48f0afe5c135268d6'}
