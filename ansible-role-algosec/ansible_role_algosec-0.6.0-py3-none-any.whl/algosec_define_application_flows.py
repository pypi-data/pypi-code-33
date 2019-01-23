import traceback

import urllib3
from ansible.module_utils.basic import AnsibleModule

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

try:
    from algosec.api_clients.business_flow import BusinessFlowAPIClient
    from algosec.errors import AlgoSecAPIError
    from algosec.models import RequestedFlow
    from algosec.flow_comparison_logic import IsEqualToFlowComparisonLogic

    HAS_LIB = True
except ImportError:
    HAS_LIB = False


ALLOWED_FLOW_CONNECTIVITY = "Pass"


def validate_app_flows(app_flows):
    """
    Verify the data structure of the requested app flows

    Its very common mistake that the users pass strings instead of lists of strings
    """
    REQUIRED_FLOW_FIELDS = ["sources", "destinations", "services"]
    FLOW_LIST_FIELDS = ["sources", "destinations", "services", "users", "network_applications"]
    for flow_name, flow in app_flows.items():
        for required_field in REQUIRED_FLOW_FIELDS:
            if required_field not in flow:
                raise ValueError(
                    "application flow '{}': required field '{}' is missing".format(flow_name, required_field)
                )
        for list_field in FLOW_LIST_FIELDS:
            if not isinstance(flow.get(list_field, []), (list, tuple)):
                raise ValueError(
                    "application flow '{}': field '{}' should be a list of strings. (got: {})".format(
                        flow_name,
                        list_field, str(type(list_field))
                    )
                )


def main():
    module = AnsibleModule(
        supports_check_mode=True,
        argument_spec=dict(
            ip_address=dict(required=True),
            user=dict(required=True, aliases=["username"]),
            password=dict(aliases=["pass", "pwd"], required=True, no_log=True),
            certify_ssl=dict(type="bool", default=False),
            app_name=dict(required=True),
            # flow name --> flow definition
            app_flows=dict(type="dict", required=True),
            check_connectivity=dict(type="bool", default=False)
        ),
    )

    if not HAS_LIB:
        module.fail_json(msg="algoec package is required for this module")

    # Verify the data structure of the requested app flows
    validate_app_flows(module.params["app_flows"])

    try:
        api = BusinessFlowAPIClient(
            module.params["ip_address"],
            module.params["user"],
            module.params["password"],
            module.params["certify_ssl"],
        )

        app_name = module.params["app_name"]
        requested_flows = {
            flow_name: RequestedFlow(
                name=flow_name,
                sources=flow["sources"],
                destinations=flow["destinations"],
                network_services=flow["services"],
                # Non required flow fields
                network_users=flow.get("users", []),
                network_applications=flow.get("network_applications", []),
                comment=flow.get("comment", ""),
            )
            for flow_name, flow in module.params["app_flows"].items()
        }

        app_revision_id = api.get_application_revision_id_by_name(app_name)

        # Converted to flow_name --> flow_data
        current_app_flows = {
            flow["name"]: flow
            for flow in api.get_application_flows(app_revision_id)
        }

        current_flow_names = set(current_app_flows.keys())
        requested_flow_names = set(requested_flows.keys())

        # Find the flows to remove, create and modify
        flows_to_delete = current_flow_names - requested_flow_names
        flows_to_create = requested_flow_names - current_flow_names

        # Get list of all flow names that have been modified in the new definition
        # Process only flow names that are both defined on ABF and present in the new flow definition
        modified_flows = {
            flow_name
            for flow_name in current_flow_names.intersection(requested_flow_names)
            if not IsEqualToFlowComparisonLogic.is_equal(requested_flows[flow_name], current_app_flows[flow_name])
        }

        unchanged_flows = current_flow_names - flows_to_delete.union(modified_flows)

        change_is_needed = any([flows_to_delete, flows_to_create, modified_flows])
        if not change_is_needed:
            msg = "Application flows are up-to-date on on AlgoSec BusinessFlow."
            changed = False
        elif module.check_mode:
            changed = False
            msg = "Check mode is on - flows update postponed"
        else:
            # Once we make the first change to the app, a new app revision would be created
            # We need to fetch it's ID and send all the consecutive API calls for the new revision ID
            # But, we want to update this info only once, to avoid redundant API calls.
            is_draft_revision = False

            # Delete all flows marked for deletion or modification
            for flow_name_to_delete in sorted(flows_to_delete | modified_flows):
                api.delete_flow_by_id(app_revision_id, current_app_flows[flow_name_to_delete]["flowID"])
                # update application revision if draft revision was created
                if not is_draft_revision:
                    app_revision_id = api.get_application_revision_id_by_name(app_name)
                    is_draft_revision = True
                    current_app_flows = {
                        flow["name"]: flow
                        for flow in api.get_application_flows(app_revision_id)
                    }

            # Create all flows marked for creation or modification
            for flow_name_to_create in sorted(flows_to_create | modified_flows):
                api.create_application_flow(app_revision_id, requested_flows[flow_name_to_create])
                # update application revision if draft revision was created
                if not is_draft_revision:
                    app_revision_id = api.get_application_revision_id_by_name(app_name)
                    is_draft_revision = True

            try:
                # Apply the application draft
                api.apply_application_draft(app_revision_id)
                changed = True
                msg = "App flows updated successfully and application draft was applied!"
            except AlgoSecAPIError as e:
                return module.fail_json(
                    msg="Exception while trying to apply application draft: {}".format(e.response_content)
                )

        # Query for the list of blocking flows (check only flows that were not changed)
        if module.params["check_connectivity"]:
            blocked_flows = []
            for flow_name in unchanged_flows:
                flow_connectivity = api.get_flow_connectivity(app_revision_id, current_app_flows[flow_name]["flowID"])
                if flow_connectivity["status"] != ALLOWED_FLOW_CONNECTIVITY:
                    blocked_flows.append(flow_name)

            if blocked_flows:
                module.fail_json(
                    app_name=app_name,
                    deleted_flows=len(flows_to_delete),
                    created_flows=len(flows_to_create),
                    modified_flows=len(modified_flows),
                    unchanged_flows=len(unchanged_flows),
                    blocked_flows=blocked_flows,
                    changed=changed,
                    msg="Flows defined successfully but connectivity check failed.",
                )

        module.exit_json(
            app_name=app_name,
            deleted_flows=len(flows_to_delete),
            created_flows=len(flows_to_create),
            modified_flows=len(modified_flows),
            unchanged_flows=len(unchanged_flows),
            changed=changed,
            msg=msg,
        )

    except AlgoSecAPIError:
        module.fail_json(msg=traceback.format_exc())


if __name__ == "__main__":
    main()
