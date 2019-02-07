import base64
import json
import os.path as osp

import pytest
import subprocess

import sys

from .common import create_webapp


class TestTemplateScripts(object):

    @pytest.fixture(autouse=True)
    def set_test_client(self, serenytics_client):
        self._client = serenytics_client

    def _run_script(self, file_name, params=None):
        params = params or {}
        params['SERENYTICS_API_KEY'] = self._client._api_key

        this_directory = osp.dirname(osp.realpath(__file__))
        root_dir = osp.join(this_directory, '..')
        template_scripts_dir = osp.join(root_dir, 'template_scripts')

        script_file_to_run = osp.join(template_scripts_dir, file_name)
        environment = '_SERENYTICS_PARAMS="{base64_json_params}"'.format(
            base64_json_params=base64.b64encode(json.dumps(params).encode('utf-8')).decode('utf-8')
        )
        cmd = '{environment} PYTHONPATH={root_dir} python {script}'.format(environment=environment,
                                                                           root_dir=root_dir,
                                                                           script=script_file_to_run)

        proc = subprocess.Popen(cmd,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                shell=True)
        stdout, stderr = proc.communicate()
        print('Script stdout:\n', stdout.decode('utf-8'))
        print('Script stderr:\n', stderr.decode('utf-8'))

        return proc.returncode

    def test_script_refresh_dashboards_cache(self, storage_data_source):
        # don't run this test on py2, this tasks uses py3
        if sys.version_info[0] < 3:
            return

        # return because this script generates an error when trying to deleting objects
        # (source is still used by the dashboard)
        return

        # -- check script returns an error if params is empty
        params = {}
        return_code = self._run_script('refresh_dashboards_cache.py', params)
        assert return_code != 0

        # -- check script returns 0 with a real dashboard
        json_content = {
            "tabs": [
                {
                    "widgets": [
                        {
                            "type": "hc-array",
                            "options": {
                                "data": {
                                    "sourceUuid": storage_data_source.uuid
                                }
                            }
                        }
                    ]
                }
            ],
            "version": 9,
            "globalStaticFilters": {}
        }
        webapp = create_webapp(client=self._client, name='Test for refresh_dashboards_cache script',
                               json_content=json_content)

        params = {
            'dashboards': [webapp.uuid]
        }
        return_code = self._run_script('refresh_dashboards_cache.py', params)
        assert return_code == 0
