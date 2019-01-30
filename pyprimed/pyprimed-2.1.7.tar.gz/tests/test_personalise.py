# -*- coding: utf-8 -*-
"""
TestPersonalise
"""
import os
import json
import pytest
import pyprimed


@pytest.mark.unit
class TestPersonalise:
    def test_personalise(self, monkeypatch, pio):
        def mock_request(*args, **kwargs):
            assert kwargs['operation'] == 'PERSONALISE'
            assert kwargs['path'] == 'personalise'
            assert kwargs['params'] == {'abvariant': 'illo_AWGRUH', 'campaign': 'tempore_VOQSMX',
                'limit': 3, 'signals': json.dumps({'signal1': 'voluptatem_FEJSUB', 'signal2': 'atque_VYMYLS'})}
            assert 'X-Authorization-Key' in kwargs['headers']
            assert 'X-Authorization-Signature' in kwargs['headers']
            assert 'X-Authorization-Nonce' in kwargs['headers']

            experiment = {
                'name': '',
                'salt': '',
                'abmembership_strategy': '',
                'abselectors': 'A B C',
                'matched_abselector': { 'matched_abselector_key': '' },
                'abvariant': 'illo_AWGRUH'
            }

            return {'abvariant': 'illo_AWGRUH', 'guuid': 'guuid', 'campaign': 'tempore_VOQSMX', 'query_latency_ms': 123.0, 'experiment': experiment}

        campaign = pyprimed.models.campaign.Campaign(
            parent=pio, uid='123', key='tempore_VOQSMX')

        monkeypatch.setattr(pio, '_dispatch_request', mock_request)
        results = campaign.personalise(pubkey='mypubkey', secretkey='mysecretkey', abvariant='illo_AWGRUH', signals={'signal1': 'voluptatem_FEJSUB', 'signal2': 'atque_VYMYLS'}, limit=3)

    def test_personalise_result_wrapper(self, monkeypatch, pio):
        def mock_personalise_request(*args, **kwargs):
            sample_response_path = os.path.dirname(__file__) + '/samples/personalise_response.json'
            return json.loads(open(sample_response_path, 'r').read())['response_data']

        campaign = pyprimed.models.campaign.Campaign(
            parent=pio, uid='123', key='tempore_VOQSMX')
        
        monkeypatch.setattr(pio, '_dispatch_request', mock_personalise_request)
        results = campaign.personalise(pubkey='mypubkey', secretkey='mysecretkey', abvariant='illo_AWGRUH', signals={'signal1': 'voluptatem_FEJSUB', 'signal2': 'atque_VYMYLS'}, limit=3)

        assert results.abvariant == {'dithering': False, 'label': 'illo_AWGRUH', 'recency': False}
        assert results.guuid == '000507da-15d7-48dc-b511-3554ce7388b9'
        assert results.campaign == 'tempore_VOQSMX'
        assert results.latency == 104.13
        assert len(results) == 3

        assert not results.first.dithering
        assert results.first.fscore == 0.7152
        assert results.first.recency_factor == 1.0
        assert results.first.ruuid == '2353273c-a044-4415-b5d4-71ed3154098c'
        assert results.first.target['uid'] == 'f5e74da5ce3f4500a39f1871a93eb471'
        assert len(results.first.components) == 2
