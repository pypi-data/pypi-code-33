"""
Tests for `centreonapi` module.
"""
import pytest
import responses
import json
import os
from centreonapi.centreon import Centreon
from centreonapi.webservice import Webservice
from centreonapi.webservice.configuration.host import Hosts, Host, HostMacro, HostTemplate
from centreonapi.webservice.configuration.poller import Poller
from centreonapi.webservice.configuration.hostgroups import HostGroup
from centreonapi.webservice.configuration.contact import ContactGroup, Contact
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
        responses.add(
            responses.POST,
            'http://api.domain.tld/centreon/api/index.php?action=authenticate',
            body=wsresponses, status=200, content_type='application/json')

        myconn = Webservice.getInstance(url, username, password)
        myconn.auth()
        assert mytoken == myconn.auth_token


class TestHosts:
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
    def test_hosts_list(self, centreon_con):
        with open(resource_dir / 'test_hosts_list.json') as data:
            wsresponses = json.load(data)
        responses.add(
            responses.POST,
            self.clapi_url,
            json=wsresponses, status=200, content_type='application/json')
        _, res = centreon_con.hosts.get('mail-uranus-frontend')
        assert res.id == "12"

    @responses.activate
    def test_hosts_not_exist(self, centreon_con):
        with open(resource_dir / 'test_hosts_list.json') as data:
            wsresponses = json.load(data)
        responses.add(
            responses.POST,
            self.clapi_url,
            json=wsresponses, status=200, content_type='application/json')
        state, res = centreon_con.hosts.get('empty')
        assert state == False
        assert res == None

    def test_hosts_add(self, centreon_con):
        values = [
            "new_host.tld",
            "new_host",
            "127.0.0.7",
            "OS-Linux-SNMP-custom|OS-Linux-SNMP-disk",
            "Central",
            "hg"
        ]
        data = dict()
        data['action'] = 'add'
        data['object'] = 'HOST'
        data['values'] = values

        with patch('requests.post') as patched_post:
            centreon_con.hosts.add(
                "new_host.tld",
                "new_host",
                "127.0.0.7",
                "Central",
                ["OS-Linux-SNMP-custom", "OS-Linux-SNMP-disk"],
                ["hg"],
                post_refresh=False
            )
            patched_post.assert_called_with(
                self.clapi_url,
                headers=self.headers,
                data=json.dumps(data),
                verify=True
            )

    def test_hosts_delete(self, centreon_con):
        data = dict()
        data['action'] = 'del'
        data['object'] = 'HOST'
        data['values'] = 'my_deleted_host'

        with patch('requests.post') as patched_post:
            centreon_con.hosts.delete('my_deleted_host', post_refresh=False)
            patched_post.assert_called_with(
                self.clapi_url,
                headers=self.headers,
                data=json.dumps(data),
                verify=True
            )

    @pytest.fixture()
    def host_load_data(self):
        with open(resource_dir / 'test_host_obj.json') as hdata:
            return Host(json.load(hdata))

    def test_hosts_delete_with_obj(self, centreon_con, host_load_data):
        host = host_load_data
        data = dict()
        data['action'] = 'del'
        data['object'] = 'HOST'
        data['values'] = 'mail-uranus-frontend'

        with patch('requests.post') as patched_post:
            centreon_con.hosts.delete(host, post_refresh=False)
            patched_post.assert_called_with(
                self.clapi_url,
                headers=self.headers,
                data=json.dumps(data),
                verify=True
            )


class TestHost():
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

    @pytest.fixture()
    def host_load_data(self):
        with open(resource_dir / 'test_host_obj.json') as hdata:
            return Host(json.load(hdata))

    @responses.activate
    def test_host_getmacro(self, host_load_data):
        host = host_load_data
        with open(resource_dir / 'test_host_macros.json') as data:
            wsresponses = json.load(data)
        responses.add(responses.POST,
                      self.clapi_url,
                      json=wsresponses, status=200, content_type='application/json')
        _, res = host.getmacro()
        assert res["$_HOSTMATTERMOST_CHAN$"].name == "MATTERMOST_CHAN"

    def test_host_setmacro(self, host_load_data):
        host = host_load_data
        data = dict()
        data['action'] = 'setmacro'
        data['object'] = 'HOST'
        data['values'] = [host.name, 'MACRO_TEST', 'VALUE_TEST', '0', 'DESC']

        with patch('requests.post') as patched_post:
            host.setmacro('MACRO_TEST', 'VALUE_TEST', '0', 'DESC')
            patched_post.assert_called_with(
                self.clapi_url,
                headers=self.headers,
                data=json.dumps(data),
                verify=True
            )

    def test_host_delmacro(self, host_load_data):
        host = host_load_data
        with open(resource_dir / 'test_host_macro.json') as m:
            macro = HostMacro(json.load(m))
        data = dict()
        data['action'] = 'delmacro'
        data['object'] = 'HOST'
        data['values'] = [host.name, 'NRPEPORT']

        with patch('requests.post') as patched_post:
            host.deletemacro(macro)
            patched_post.assert_called_with(
                self.clapi_url,
                headers=self.headers,
                data=json.dumps(data),
                verify=True
            )

    @responses.activate
    def test_host_gettemplate(self, host_load_data):
        host = host_load_data
        with open(resource_dir / 'test_host_templates.json') as data:
            wsresponses = json.load(data)
        responses.add(responses.POST,
                      self.clapi_url,
                      json=wsresponses, status=200, content_type='application/json')
        _, res = host.gettemplate()
        print(res)
        assert res["OS-Linux-SNMP-custom"].id == "6"


    def test_host_settemplate(self, host_load_data):
        host = host_load_data
        templates = list()
        with open(resource_dir / 'test_host_template.json') as htlp:
            tmp = json.load(htlp)
            for tlp in tmp:
                print(tlp)
                templates.append(HostTemplate(tlp))

        data = dict()
        data['action'] = 'settemplate'
        data['object'] = 'HOST'
        data['values'] = [
            "mail-uranus-frontend",
            "OS-Linux-SNMP-custom|OS-Linux-SNMP-Disk-/"]

        with patch('requests.post') as patched_post:
            host.settemplate(templates)
            patched_post.assert_called_with(
                self.clapi_url,
                headers=self.headers,
                data=json.dumps(data),
                verify=True
            )

    def test_host_addtemplate(self, host_load_data):
        host = host_load_data
        templates = list()
        with open(resource_dir / 'test_host_template.json') as htlp:
            tmp = json.load(htlp)
            for tlp in tmp:
                print(tlp)
                templates.append(HostTemplate(tlp))

        data = dict()
        data['action'] = 'addtemplate'
        data['object'] = 'HOST'
        data['values'] = [
            "mail-uranus-frontend",
            "OS-Linux-SNMP-custom|OS-Linux-SNMP-Disk-/"]

        with patch('requests.post') as patched_post:
            host.addtemplate(templates)
            patched_post.assert_called_with(
                self.clapi_url,
                headers=self.headers,
                data=json.dumps(data),
                verify=True
            )

    def test_host_deteletemplate(self, host_load_data):
        host = host_load_data
        templates = list()
        with open(resource_dir / 'test_host_template.json') as htlp:
            tmp = json.load(htlp)
            for tlp in tmp:
                templates.append(HostTemplate(tlp))

        data = dict()
        data['action'] = 'deltemplate'
        data['object'] = 'HOST'
        data['values'] = [
            "mail-uranus-frontend",
            "OS-Linux-SNMP-custom|OS-Linux-SNMP-Disk-/"]

        with patch('requests.post') as patched_post:
            host.deletetemplate(templates)
            patched_post.assert_called_with(
                self.clapi_url,
                headers=self.headers,
                data=json.dumps(data),
                verify=True
            )

    def test_host_applytemplate(self, host_load_data):
        host = host_load_data
        data = dict()
        data['action'] = 'applytpl'
        data['object'] = 'HOST'
        data['values'] = "mail-uranus-frontend"

        with patch('requests.post') as patched_post:
            host.applytemplate()
            patched_post.assert_called_with(
                self.clapi_url,
                headers=self.headers,
                data=json.dumps(data),
                verify=True
            )

    def test_host_enable(self, host_load_data):
        host = host_load_data
        data = dict()
        data['action'] = 'enable'
        data['object'] = 'HOST'
        data['values'] = "mail-uranus-frontend"

        with patch('requests.post') as patched_post:
            host.enable()
            patched_post.assert_called_with(
                self.clapi_url,
                headers=self.headers,
                data=json.dumps(data),
                verify=True
            )

    def test_host_disable(self, host_load_data):
        host = host_load_data
        data = dict()
        data['action'] = 'disable'
        data['object'] = 'HOST'
        data['values'] = "mail-uranus-frontend"

        with patch('requests.post') as patched_post:
            host.disable()
            patched_post.assert_called_with(
                self.clapi_url,
                headers=self.headers,
                data=json.dumps(data),
                verify=True
            )

    def test_host_setinstance(self, host_load_data):
        host = host_load_data
        with open(resource_dir / 'test_host_poller.json') as instances:
            instance = Poller(json.load(instances))

        data = dict()
        data['action'] = 'setinstance'
        data['object'] = 'HOST'
        data['values'] = ["mail-uranus-frontend", "Central"]

        with patch('requests.post') as patched_post:
            host.setinstance(instance)
            patched_post.assert_called_with(
                self.clapi_url,
                headers=self.headers,
                data=json.dumps(data),
                verify=True
            )

    @responses.activate
    def test_host_getparents(self, host_load_data):
        host = host_load_data
        with open(resource_dir / 'test_host_parents.json') as data:
                wsresponses = json.load(data)
        responses.add(responses.POST,
                      self.clapi_url,
                      json=wsresponses, status=200, content_type='application/json')
        _, res = host.getparent()
        assert res['mail-neptune-frontend'].id == "13"

    def test_host_addparent(self, host_load_data):
        host = host_load_data
        with open(resource_dir / 'test_host_parent.json') as parent:
            parents = Host(json.load(parent))

        data = dict()
        data['action'] = 'addparent'
        data['object'] = 'HOST'
        data['values'] = ["mail-uranus-frontend", "mail-neptune-frontend"]

        with patch('requests.post') as patched_post:
            host.addparent(parents)
            patched_post.assert_called_with(
                self.clapi_url,
                headers=self.headers,
                data=json.dumps(data),
                verify=True
            )

    def test_host_setparent(self, host_load_data):
        host = host_load_data
        with open(resource_dir / 'test_host_parent.json') as parent:
            parents = Host(json.load(parent))

        data = dict()
        data['action'] = 'setparent'
        data['object'] = 'HOST'
        data['values'] = ["mail-uranus-frontend", "mail-neptune-frontend"]

        with patch('requests.post') as patched_post:
            host.setparent(parents)
            patched_post.assert_called_with(
                self.clapi_url,
                headers=self.headers,
                data=json.dumps(data),
                verify=True
            )

    def test_host_setparent(self, host_load_data):
        host = host_load_data
        with open(resource_dir / 'test_host_parent.json') as parent:
            parents = Host(json.load(parent))

        data = dict()
        data['action'] = 'delparent'
        data['object'] = 'HOST'
        data['values'] = ["mail-uranus-frontend", "mail-neptune-frontend"]

        with patch('requests.post') as patched_post:
            host.deleteparent(parents)
            patched_post.assert_called_with(
                self.clapi_url,
                headers=self.headers,
                data=json.dumps(data),
                verify=True
            )

    @responses.activate
    def test_host_gethostgroup(self, host_load_data):
        host = host_load_data
        with open(resource_dir / "test_host_hostgroups.json") as data:
            wsresponses = json.load(data)
        responses.add(responses.POST,
                          self.clapi_url,
                          json=wsresponses, status=200, content_type='application/json')
        _, res = host.gethostgroup()
        assert res['centreon-prj'].id == "115"

    def test_host_addparent(self, host_load_data):
        host = host_load_data
        with open(resource_dir / 'test_host_hostgroup.json') as hg:
            hgs = HostGroup(json.load(hg))

        data = dict()
        data['action'] = 'addhostgroup'
        data['object'] = 'HOST'
        data['values'] = ["mail-uranus-frontend", "centreon-prod"]

        with patch('requests.post') as patched_post:
            host.addhostgroup(hgs)
            patched_post.assert_called_with(
                self.clapi_url,
                headers=self.headers,
                data=json.dumps(data),
                verify=True
            )

    def test_host_setparent(self, host_load_data):
        host = host_load_data
        with open(resource_dir / 'test_host_hostgroup.json') as hg:
            hgs = HostGroup(json.load(hg))

        data = dict()
        data['action'] = 'sethostgroup'
        data['object'] = 'HOST'
        data['values'] = ["mail-uranus-frontend", "centreon-prod"]

        with patch('requests.post') as patched_post:
            host.sethostgroup(hgs)
            patched_post.assert_called_with(
                self.clapi_url,
                headers=self.headers,
                data=json.dumps(data),
                verify=True
            )

    def test_host_deletehostgroup(self, host_load_data):
        host = host_load_data
        with open(resource_dir / 'test_host_hostgroup.json') as hg:
            hgs = HostGroup(json.load(hg))

        data = dict()
        data['action'] = 'delhostgroup'
        data['object'] = 'HOST'
        data['values'] = ["mail-uranus-frontend", "centreon-prod"]

        with patch('requests.post') as patched_post:
            host.deletehostgroup(hgs)
            patched_post.assert_called_with(
                self.clapi_url,
                headers=self.headers,
                data=json.dumps(data),
                verify=True
            )

    @responses.activate
    def test_host_getcontactgroup(self, host_load_data):
        host = host_load_data
        with open(resource_dir / "test_host_contactgroups.json") as data:
            wsresponses = json.load(data)
        responses.add(
            responses.POST,
            self.clapi_url,
            json=wsresponses, status=200, content_type='application/json')
        _, res = host.getcontactgroup()
        assert res['astreinte'].id == "9"

    def test_host_addcontactgroupt(self, host_load_data):
        host = host_load_data
        with open(resource_dir / 'test_host_contactgroup.json') as cg:
            cgs = ContactGroup(json.load(cg))

        data = dict()
        data['action'] = 'addcontactgroup'
        data['object'] = 'HOST'
        data['values'] = ["mail-uranus-frontend", "astreinte"]

        with patch('requests.post') as patched_post:
            host.addcontactgroup(cgs)
            patched_post.assert_called_with(
                self.clapi_url,
                headers=self.headers,
                data=json.dumps(data),
                verify=True
            )

    def test_host_setcontactgroup(self, host_load_data):
        host = host_load_data
        with open(resource_dir / 'test_host_contactgroup.json') as cg:
            cgs = ContactGroup(json.load(cg))

        data = dict()
        data['action'] = 'setcontactgroup'
        data['object'] = 'HOST'
        data['values'] = ["mail-uranus-frontend", "astreinte"]

        with patch('requests.post') as patched_post:
            host.setcontactgroup(cgs)
            patched_post.assert_called_with(
                self.clapi_url,
                headers=self.headers,
                data=json.dumps(data),
                verify=True
            )

    def test_host_deletecontactgroup(self, host_load_data):
        host = host_load_data
        with open(resource_dir / 'test_host_contactgroup.json') as cg:
            cgs = ContactGroup(json.load(cg))

        data = dict()
        data['action'] = 'delcontactgroup'
        data['object'] = 'HOST'
        data['values'] = ["mail-uranus-frontend", "astreinte"]

        with patch('requests.post') as patched_post:
            host.deletecontactgroup(cgs)
            patched_post.assert_called_with(
                self.clapi_url,
                headers=self.headers,
                data=json.dumps(data),
                verify=True
            )

    @responses.activate
    def test_host_getcontact(self, host_load_data):
        host = host_load_data
        with open(resource_dir / "test_host_contacts.json") as data:
            wsresponses = json.load(data)
        responses.add(
            responses.POST,
            self.clapi_url,
            json=wsresponses, status=200, content_type='application/json')
        _, res = host.getcontact()
        assert res['astreinte'].id == "27"

    def test_host_addcontact(self, host_load_data):
        host = host_load_data
        with open(resource_dir / 'test_host_contact.json') as c:
            cs = Contact(json.load(c))

        data = dict()
        data['action'] = 'addcontact'
        data['object'] = 'HOST'
        data['values'] = ["mail-uranus-frontend", "g15x"]

        with patch('requests.post') as patched_post:
            host.addcontact(cs)
            patched_post.assert_called_with(
                self.clapi_url,
                headers=self.headers,
                data=json.dumps(data),
                verify=True
            )

    def test_host_setcontact(self, host_load_data):
        host = host_load_data
        with open(resource_dir / 'test_host_contact.json') as c:
            cs = Contact(json.load(c))

        data = dict()
        data['action'] = 'setcontact'
        data['object'] = 'HOST'
        data['values'] = ["mail-uranus-frontend", "g15x"]

        with patch('requests.post') as patched_post:
            host.setcontact(cs)
            patched_post.assert_called_with(
                self.clapi_url,
                headers=self.headers,
                data=json.dumps(data),
                verify=True
            )

    def test_host_deletecontact(self, host_load_data):
        host = host_load_data
        with open(resource_dir / 'test_host_contact.json') as c:
            cs = Contact(json.load(c))

        data = dict()
        data['action'] = 'delcontact'
        data['object'] = 'HOST'
        data['values'] = ["mail-uranus-frontend", "g15x"]

        with patch('requests.post') as patched_post:
            host.deletecontact(cs)
            patched_post.assert_called_with(
                self.clapi_url,
                headers=self.headers,
                data=json.dumps(data),
                verify=True
            )

    def test_host_setparam(self, host_load_data):
        host = host_load_data

        data = dict()
        data['action'] = 'setparam'
        data['object'] = 'HOST'
        data['values'] = ["mail-uranus-frontend", "notes", "tested"]

        with patch('requests.post') as patched_post:
            host.setparam("notes", "tested")
            patched_post.assert_called_with(
                self.clapi_url,
                headers=self.headers,
                data=json.dumps(data),
                verify=True
            )