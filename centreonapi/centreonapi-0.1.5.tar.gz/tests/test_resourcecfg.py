"""
Tests for `centreonapi` module.
"""
import pytest
import responses
import json
import os
from centreonapi.centreon import Centreon
from centreonapi.webservice import Webservice
from centreonapi.webservice.configuration.resourcecfg import ResourceCFG
from mock import patch
from path import Path


if os.path.isdir('tests'):
    config_dir = Path('tests')
    resource_dir = Path('tests/resources')
else:
    config_dir = Path('.')
    resource_dir = Path('./resources')


class TestConnect:
    @responses.activate
    def test_connection(self):
        url = "http://api.domain.tld/centreon"
        username = "mytest"
        password = "mypass"
        mytoken = "NTc1MDU3MGE3M2JiODIuMjA4OTA2OTc="
        wsresponses = '{"authToken": "NTc1MDU3MGE3M2JiODIuMjA4OTA2OTc="}'
        responses.add(responses.POST,
                      'http://api.domain.tld/centreon/api/index.php?action=authenticate',
                      body=wsresponses, status=200, content_type='application/json')

        myconn = Webservice.getInstance(url, username, password)
        myconn.auth()
        assert mytoken == myconn.auth_token


class TestResourceCFG:

    clapi_url = 'http://api.domain.tld/centreon/api/index.php?action=action&object=centreon_clapi'
    headers = {
                  'Content-Type': 'application/json',
                  'centreon-auth-token': 'NTc1MDU3MGE3M2JiODIuMjA4OTA2OTc='
                }


    @pytest.fixture()
    @responses.activate
    def centreon_con(self):
        url = "http://api.domain.tld/centreon"
        username = "mytest"
        password = "mypass"

        wsresponses = '{"authToken": "NTc1MDU3MGE3M2JiODIuMjA4OTA2OTc="}'
        responses.add(responses.POST,
                      'http://api.domain.tld/centreon/api/index.php?action=authenticate',
                      body=wsresponses, status=200, content_type='application/json')
        return Centreon(url, username, password)

    @responses.activate
    def test_resourcecfg_get_one(self, centreon_con):
        with open(resource_dir / 'test_resourcecfg_list.json') as data:
            wsresponses = json.load(data)
        responses.add(responses.POST,
                      'http://api.domain.tld/centreon/api/index.php?action=action&object=centreon_clapi',
                      json=wsresponses, status=200, content_type='application/json')

        _, res = centreon_con.resourcecfgs.get('$_HOSTSNMPVERSION$')
        assert res.name == "$_HOSTSNMPVERSION$"

    @responses.activate
    def test_resourcecfg_building_line(self, centreon_con):
        with open(resource_dir / 'test_resourcecfg_list.json') as data:
            wsresponses = json.load(data)
        responses.add(responses.POST,
                      'http://api.domain.tld/centreon/api/index.php?action=action&object=centreon_clapi',
                      json=wsresponses, status=200, content_type='application/json')

        _, res = centreon_con.resourcecfgs.get('_HOSTSNMPVERSION')
        assert res.name == "$_HOSTSNMPVERSION$"

    @responses.activate
    def test_resourcecfg_not_exist(self, centreon_con):
        with open(resource_dir / 'test_resourcecfg_list.json') as data:
            wsresponses = json.load(data)
        responses.add(responses.POST,
                      'http://api.domain.tld/centreon/api/index.php?action=action&object=centreon_clapi',
                      json=wsresponses, status=200, content_type='application/json')
        state, res = centreon_con.resourcecfgs.get('empty')
        assert state == False
        assert res == None


    clapi_url = 'http://api.domain.tld/centreon/api/index.php?action=action&object=centreon_clapi'
    headers = {
        'Content-Type': 'application/json',
        'centreon-auth-token': 'NTc1MDU3MGE3M2JiODIuMjA4OTA2OTc='
        }

    def test_resourcecfg_add(self, centreon_con):
        values = [
            'resource_test',
            'ressource_value',
            'Central',
            'comment'
        ]
        data = {}
        data['action'] = 'add'
        data['object'] = 'RESOURCECFG'
        data['values'] = values

        with patch('requests.post') as patched_post:
            centreon_con.resourcecfgs.add("resource_test",
                                          "ressource_value",
                                          "Central",
                                          "comment",
                                          post_refresh=False
                                          )
            patched_post.assert_called_with(self.clapi_url, headers=self.headers, data=json.dumps(data), verify=True)

    def test_resourcecfg_delete(self, centreon_con):
        data = {}
        data['action'] = 'del'
        data['object'] = 'RESOURCECFG'
        data['values'] = '42'

        with patch('requests.post') as patched_post:
            centreon_con.resourcecfgs.delete('42', post_refresh=False)
            patched_post.assert_called_with(self.clapi_url, headers=self.headers, data=json.dumps(data), verify=True)

    @responses.activate
    def test_resourcecfg_setparam(self):
        with open(resource_dir / 'test_resourcecfg_1.json') as data:
            res = ResourceCFG(json.load(data))
        values = [
            res.id,
            'instance',
            'Central',
        ]
        data = {}
        data['action'] = 'setparam'
        data['object'] = 'RESOURCECFG'
        data['values'] = values

        with patch('requests.post') as patched_post:
            res.setparam('instance', 'Central')
            patched_post.assert_called_with(self.clapi_url, headers=self.headers, data=json.dumps(data), verify=True)


