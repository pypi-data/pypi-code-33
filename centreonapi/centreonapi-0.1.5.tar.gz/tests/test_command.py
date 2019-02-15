"""
Tests for `centreonapi` module.
"""
import pytest
import responses
import json
import os
from centreonapi.centreon import Centreon
from centreonapi.centreon import Webservice
from centreonapi.webservice.configuration.command import Command
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


class TestCommands:
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
    def test_command_list(self, centreon_con):
        with open(resource_dir / 'test_commands_list.json') as data:
            wsresponses = json.load(data)
        responses.add(responses.POST,
                      'http://api.domain.tld/centreon/api/index.php?action=action&object=centreon_clapi',
                      json=wsresponses, status=200, content_type='application/json')

        _, res = centreon_con.commands.get('OS-Linux-SNMP-Memory')
        assert res.id == "111"

    @responses.activate
    def test_command_not_exist(self, centreon_con):
        with open(resource_dir / 'test_commands_list.json') as data:
            wsresponses = json.load(data)
        responses.add(responses.POST,
                      'http://api.domain.tld/centreon/api/index.php?action=action&object=centreon_clapi',
                      json=wsresponses, status=200, content_type='application/json')
        state, cmd = centreon_con.commands.get("empty")
        assert state == False

    def test_command_add(self, centreon_con):
        values = [
            'command_test',
            'check',
            '/my/plugins my command'
        ]
        data = {}
        data['action'] = 'add'
        data['object'] = 'CMD'
        data['values'] = values

        with patch('requests.post') as patched_post:
            centreon_con.commands.add("command_test",
                                          "check",
                                          "/my/plugins my command",
                                          post_refresh=False
                                          )
            patched_post.assert_called_with(self.clapi_url, headers=self.headers, data=json.dumps(data), verify=True)

    def test_command_delete(self, centreon_con):
        data = {}
        data['action'] = 'del'
        data['object'] = 'CMD'
        data['values'] = 'command_test'

        with patch('requests.post') as patched_post:
            centreon_con.commands.delete('command_test', post_refresh=False)
            patched_post.assert_called_with(self.clapi_url, headers=self.headers, data=json.dumps(data), verify=True)

    @responses.activate
    def test_command_setparam(self):
        with open(resource_dir / 'test_commands_1.json') as data:
            cmd = Command(json.load(data))
        values = [
            cmd.name,
            'type',
            'notif',
        ]
        data = {}
        data['action'] = 'setparam'
        data['object'] = 'CMD'
        data['values'] = values

        with patch('requests.post') as patched_post:
            cmd.setparam('type', 'notif')
            patched_post.assert_called_with(self.clapi_url, headers=self.headers, data=json.dumps(data), verify=True)



