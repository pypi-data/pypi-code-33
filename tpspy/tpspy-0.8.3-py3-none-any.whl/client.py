# -*- coding: utf-8 -*-

try:
    from urllib.parse import urljoin
except ImportError:
    from urlparse import urljoin
import requests
import json
from tpspy.message.message import ClientMessage
from tpspy.permission.permission import ClientPermission


class Client(ClientMessage, ClientPermission):
    def __init__(self, sys_id, sys_secret, tps_base_url=None):
        super(Client, self).__init__(sys_id=sys_id, sys_secret=sys_secret, tps_base_url=tps_base_url)
        self.airflow_to = ""
        self.airflow_channels = ""

    def api_tapd_tencent(self, method, path, params, api_user=None, api_pwd=None):
        url = urljoin(self.tps_base_url, "api/v1/apibridge/tapdTencent")
        resp = requests.get(url, json=dict(
            method=method,
            path=path,
            params=params,
            api_user=api_user,
            api_pwd=api_pwd,
        ), headers=self.auth_headers)
        return resp.json()

    def metrics_resource_flow_upload(self, data):
        url = urljoin(self.tps_base_url, "api/v1/metrics/resource_flow/upload")

        resp = requests.post(url, data=json.dumps(dict(
            data=data
        )), headers=self.post_headers)
        return self.resp_get_json(resp)

    def metrics_resource_flow_get(self, params):
        url = urljoin(self.tps_base_url, "api/v1/metrics/resource_flow/get")

        resp = requests.get(url, data=json.dumps(params), headers=self.get_headers)
        return self.resp_get_json(resp)

    def airflow_on_failure_callback(self, to, channels, context):
        """
        context, see: airflow/models.py: get_template_context()

        Define the callback to post on Slack if a failure is detected in the Workflow
        :return: operator.execute
        """

        print("TPS, airflow on_failure_callback in.")

        dag = str(context['dag'].dag_id)
        task_id = str(context['task'].task_id)
        execution_date = str(context['execution_date'])

        content = dict(
            title="[Airflow 告警] Airflow 任务失败",
            body="[Airflow 告警]\nAirflow 任务失败\nDAG: %s\nTASK: %s\nDATE: %s" % (
                dag, task_id, execution_date
            )
        )

        to = to
        r = self.message_send(msg_type=channels, to=to, content=content)
        print("TPS, airflow on_failure_callback, send: %s, msg: %s, resp: %s" % (to, content["body"], r))


if __name__ == "__main__":
    pass
