import traceback

import urllib3
from ansible.module_utils.basic import AnsibleModule
from marshmallow import Schema, fields

NO_TRAFFIC_LINES_TO_CREATE = 0

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

try:
    from algosec.api_clients.fire_flow import FireFlowAPIClient
    from algosec.api_clients.firewall_analyzer import FirewallAnalyzerAPIClient
    from algosec.errors import AlgoSecAPIError
    from algosec.models import DeviceAllowanceState, ChangeRequestAction, ChangeRequestTrafficLine

    HAS_LIB = True
except ImportError:
    HAS_LIB = False


class TrafficLineSchema(Schema):
    """Define the schema for the traffic lines provided by the user"""
    def __init__(self, **kwargs):
        super(Schema, self).__init__(strict=True, **kwargs)

    action = fields.Boolean(required=True)
    sources = fields.List(fields.Str(), required=True)
    destinations = fields.List(fields.Str(), required=True)
    services = fields.List(fields.Str(), required=True)


def main():
    module = AnsibleModule(
        supports_check_mode=True,
        argument_spec=dict(
            ip_address=dict(required=True),
            user=dict(required=True, aliases=["username"]),
            password=dict(aliases=["pass", "pwd"], required=True, no_log=True),
            certify_ssl=dict(type="bool", default=False),
            requestor=dict(required=True),
            email=dict(required=True),
            traffic_lines=dict(type="list", required=True),
            template=dict(default=None, required=False),
        )
    )

    if not HAS_LIB:
        module.fail_json(msg="algoec package is required for this module")

    # Validate the structure of the traffic lines provided by the user
    result = TrafficLineSchema().load(module.params["traffic_lines"], many=True)
    if result.errors:
        raise ValueError("Incorrect data structure provided for traffic lines: {}".format(result.errors))
    traffic_lines = result.data

    traffic_lines_to_create = []

    try:
        afa_client = FirewallAnalyzerAPIClient(
            module.params["ip_address"],
            module.params["user"],
            module.params["password"],
            module.params["certify_ssl"],
        )

        for traffic_line in traffic_lines:
            # Make the network simulation query to see in the traffic line is needed
            query_result = afa_client.execute_traffic_simulation_query(
                source=traffic_line["sources"],
                destination=traffic_line["destinations"],
                service=traffic_line["services"],
            )

            connectivity_status = query_result['result']

            action = ChangeRequestAction.ALLOW if traffic_line["action"] else ChangeRequestAction.DROP
            # If simulation query result matches the user's request, do nothing
            if action == ChangeRequestAction.ALLOW and connectivity_status == DeviceAllowanceState.ALLOWED:
                continue
            if action == ChangeRequestAction.DROP and connectivity_status == DeviceAllowanceState.BLOCKED:
                continue

            # A change request is needed for this traffic line
            traffic_lines_to_create.append(
                ChangeRequestTrafficLine(
                    action=action,
                    sources=traffic_line["sources"],
                    destinations=traffic_line["destinations"],
                    services=traffic_line["services"],
                )
            )

    except AlgoSecAPIError:
        module.fail_json(msg="Error executing traffic simulation query:\n{}".format(traceback.format_exc()))
        return

    response = {}
    if len(traffic_lines_to_create) == NO_TRAFFIC_LINES_TO_CREATE:
        module.log("Connectivity check passed for all traffic lines. No FireFlow change request is required.")
        response["changed"] = False
    else:

        module.log(
            "Connectivity status require a change for {} traffic lines. Opening change request on AlgoSec FireFlow "
            "at {}".format(
                traffic_lines_to_create,
                module.params["ip_address"]
            )
        )
        if not module.check_mode:
            try:
                aff_client = FireFlowAPIClient(
                    module.params["ip_address"],
                    module.params["user"],
                    module.params["password"],
                    module.params["certify_ssl"],
                )
                requestor = module.params["requestor"]

                change_request_url = aff_client.create_change_request(
                    subject="Change request issued via Ansible",
                    requestor_name=requestor,
                    email=module.params["email"],
                    traffic_lines=traffic_lines_to_create,
                    description="Traffic change request created by {} directly from Ansible.".format(requestor),
                    template=module.params["template"],
                )
            except AlgoSecAPIError:
                module.fail_json(msg="Error creating change request:\n{}".format(traceback.format_exc()))
                return
            response["change_request_url"] = change_request_url
        response["changed"] = True

    module.exit_json(**response)


if __name__ == "__main__":
    main()
