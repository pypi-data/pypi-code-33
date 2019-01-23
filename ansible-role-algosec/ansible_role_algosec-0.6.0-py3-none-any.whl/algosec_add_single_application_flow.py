import traceback

import urllib3
from ansible.module_utils.basic import AnsibleModule

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

try:
    from algosec.api_clients.business_flow import BusinessFlowAPIClient
    from algosec.errors import AlgoSecAPIError, EmptyFlowSearch
    from algosec.models import RequestedFlow
    from algosec.flow_comparison_logic import IsEqualToFlowComparisonLogic

    HAS_LIB = True
except ImportError:
    HAS_LIB = False


def main():
    module = AnsibleModule(
        supports_check_mode=True,
        argument_spec=dict(
            # arguments used for creating the flow
            ip_address=dict(required=True),
            user=dict(required=True, aliases=["username"]),
            password=dict(aliases=["pass", "pwd"], required=True, no_log=True),
            certify_ssl=dict(type="bool", default=False),
            app_name=dict(required=True),
            name=dict(required=True),
            sources=dict(type="list", required=True),
            destinations=dict(type="list", required=True),
            services=dict(type="list", required=True),
            users=dict(type="list", required=False, default=[]),
            network_applications=dict(type="list", required=False, default=[]),
            comment=dict(required=False, default="Flow created by AlgoSecAnsible"),
            apply_draft=dict(type="bool", default=True),
        ),
    )

    if not HAS_LIB:
        module.fail_json(msg="algoec package is required for this module")

    app_name = module.params["app_name"]
    flow_name = module.params["name"]
    try:
        api = BusinessFlowAPIClient(
            module.params["ip_address"],
            module.params["user"],
            module.params["password"],
            module.params["certify_ssl"],
        )
        latest_revision_id = api.get_application_revision_id_by_name(app_name)

        requested_flow = RequestedFlow(
            name=flow_name,
            sources=module.params["sources"],
            destinations=module.params["destinations"],
            network_users=module.params["users"],
            network_applications=module.params["network_applications"],
            network_services=module.params["services"],
            comment=module.params["comment"],
        )
        # requested_flow.populate(api)

        try:
            flow = api.get_flow_by_name(latest_revision_id, flow_name)
            if IsEqualToFlowComparisonLogic.is_equal(requested_flow, flow):
                # Flow exists and is equal to the requested flow
                flow_has_changed, flow_upsert_needed = False, False
            else:
                # Flow exists and is different than the requested flow
                flow_has_changed, flow_upsert_needed = True, True
        except EmptyFlowSearch:
            # Flow does not exist, create it
            flow_has_changed, flow_upsert_needed = False, True

        if not flow_upsert_needed:
            changed = False
            message = "Flow already exists on AlgoSec BusinessFlow."
        elif module.check_mode:
            changed = False
            message = "Flow creation/update postponed since check mode is on"
        else:
            if flow_has_changed:
                api.delete_flow_by_name(latest_revision_id, flow_name)
                latest_revision_id = api.get_application_revision_id_by_name(app_name)

            api.create_application_flow(latest_revision_id, requested_flow)

            # to finalize the application flow creation, The application"s draft version is applied
            if module.params["apply_draft"]:
                try:
                    latest_revision_id = api.get_application_revision_id_by_name(app_name)
                    api.apply_application_draft(latest_revision_id)
                except AlgoSecAPIError as e:
                    module.fail_json(
                        msg="Exception while trying to apply application draft. "
                            "It is possible that another draft was just applied. "
                            "You can run the module with apply_draft=False."
                            "\nResponse Json: {}".format(e.response_content)
                    )
            changed = True
            message = "Flow created/updated successfully!"

        module.exit_json(changed=changed, msg=message)

    except AlgoSecAPIError:
        module.fail_json(msg=(traceback.format_exc()))


if __name__ == "__main__":
    main()
