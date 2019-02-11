from enum import Enum
from logging import Logger

from sidecar.const import Const
from sidecar.aws_session import AwsSession
from sidecar.utils import Utils


class AWSStatusMaintainer:
    table_data = {}

    class INSTANCE_STATE(Enum):
        START_DEPLOYMENT = 1
        RUNNING = 2

    class APP_STATE(Enum):
        NOT_STARTED = 1
        STARTED = 2
        PASSED_HEALTH_CHECK = 3
        FAILED_HEALTH_CHECK = 4

    default_table_name = 'colony-sandboxes-datatable'

    default_table_attributes = [
        {
            'AttributeName': Const.SANDBOX_ID_TAG,
            'AttributeType': 'S',
        }
    ]

    default_table_schema = [
        {
            'AttributeName': Const.SANDBOX_ID_TAG,
            'KeyType': 'HASH',
        }
    ]

    default_table_provisioned_throughput = {
        'ReadCapacityUnits': 25,
        'WriteCapacityUnits': 25
    }

    def __init__(self, awssessionservice: AwsSession, sandbox_id: str, logger: Logger, default_region: str):
        self.default_region = default_region
        self.dynamo_resource = awssessionservice.get_dynamo_resource(default_region=self.default_region)
        self.sandboxid = sandbox_id
        self._logger = logger
        self.table_name = self.default_table_name

        table = self.dynamo_resource.Table(self.default_table_name)

        try:
            Utils.wait_for(func=lambda: self._set_table_data(table, sandbox_id) is not None,
                           interval_sec=1,
                           max_retries=5,
                           error='No sandbox data available')
        except Exception:
            self._logger.exception("Failed to get sandbox data from dynamodb after 5 times")
            return

    def _set_table_data(self, table, sandbox_id):

        response = table.get_item(
            Key={
                Const.SANDBOX_ID_TAG: sandbox_id
            }
        )

        if "Item" in response:
            self.table_data = response["Item"]
            self._logger.info("dynamo table response for sandbox {id} is {data}".format(id=sandbox_id, data=response))
            return "Item"

        return None

    def update_app_instance_status(self, instance_logical_id, instance_id, app_name, status_tag, status):
        try:
            if instance_id not in self.table_data["apps"][instance_logical_id]["instances"]:
                self.table_data["apps"][instance_logical_id]["instances"][instance_id] = \
                    {
                        "apps": {}
                    }
        except Exception as ex:  # log details for debugging, related to bug #1689
            self._logger.exception('fail to update instance status. instance_logical_id: {}, table_data: {}, exc={}'
                                   .format(instance_logical_id, self.table_data, str(ex)))
            raise ex

        self.table_data["apps"][instance_logical_id]["instances"][instance_id]["apps"][app_name] = {status_tag: status}

        table = self.dynamo_resource.Table(self.default_table_name)
        response = table.update_item(
            Key={
                Const.SANDBOX_ID_TAG: self.sandboxid
            },
            UpdateExpression="set " + "apps" + " = :r",
            ExpressionAttributeValues={
                ':r': self.table_data["apps"]
            },
            ReturnValues="UPDATED_NEW"
        )

        if self.response_failed(response):
            self._logger.error(
                "Error update_app_instance_status(sandbox_id: {sandbox_id}. app_name: {app}. instance_id: {instance_id})\n"
                "Response: {data}"
                    .format(sandbox_id=self.sandboxid, app=app_name, instance_id=instance_id, data=response))

    def update_sandbox_end_status(self, sandbox_deployment_end_status: str):
        table = self.dynamo_resource.Table(self.default_table_name)

        response = table.update_item(
            Key={
                Const.SANDBOX_ID_TAG: self.sandboxid
            },
            UpdateExpression="set #f = :r, #newend = :r",
            ExpressionAttributeValues={
                ':r': sandbox_deployment_end_status
            },
            ExpressionAttributeNames={
                "#f": Const.SANDBOX_DEPLOYMENT_END_STATUS,
                "#newend": Const.SANDBOX_DEPLOYMENT_END_STATUS_v2
            },
            ReturnValues="UPDATED_NEW"
        )

        if self.response_failed(response):
            self._logger.error("Error update_sandbox_end_status(sandbox_id: {sandbox_id} status: {status})\n"
                               "Response: {data}"
                               .format(sandbox_id=self.sandboxid, status=sandbox_deployment_end_status, data=response))

    def update_sandbox_start_status(self, sandbox_start_time):
        table = self.dynamo_resource.Table(self.default_table_name)

        response = table.update_item(
            Key={
                Const.SANDBOX_ID_TAG: self.sandboxid
            },
            UpdateExpression="set #f = :r, #newstart = :r",
            ExpressionAttributeValues={
                ':r': str(sandbox_start_time)
            },
            ExpressionAttributeNames={
                "#f": Const.SANDBOX_START_TIME,
                "#newstart": Const.SANDBOX_START_TIME_v2
            },
            ReturnValues="UPDATED_NEW"
        )

        if self.response_failed(response):
            self._logger.error("Error update_sandbox_start_status(sandbox_id: {sandbox_id} status: {status})\n"
                               "Response: {data}"
                               .format(sandbox_id=self.sandboxid, status=sandbox_start_time, data=response))

    def getAllappNamesForInstance(self, logical_id: str):
        return self.table_data["spec"]["expected_apps"][logical_id]["apps"]

    def getAllappStatusForInstance(self, logical_id: str, instance_id: str):
        logical_instance = self.table_data["apps"][logical_id]["instances"]
        if instance_id in logical_instance:
            return logical_instance[instance_id]["apps"]
        else:
            return {}

    @staticmethod
    def response_failed(response: dict) -> bool:
        return not response.get("ResponseMetadata") and \
               not response.get("ResponseMetadata").get("HTTPStatusCode") == 200
