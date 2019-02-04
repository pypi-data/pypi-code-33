import json
from functools import partial


def parse_routes(oa_file, package_name: str) -> list:
    """Parse OpenAPI file and return a list of routes.

    This function expects the following directory structure in the application:
    `{package_name}/views/{x-view}`
    where `x-view` is the filename for the handlers specified in the OpenAPI
    file.

    :param oa_file: OpenAPI dict
    :type oa_file: dict
    :param package_name: package name
    :type package_name: str
    :return: list of routes
    :rtype: list
    """
    routes = []
    for route in oa_file["paths"]:
        r = oa_file["paths"][route]
        for method in r:
            h_file = r[method]["x-view"]
            handler = r[method]["operationId"]
            try:
                params = r[method]["parameters"]
            except KeyError:
                params = []

            out = {
                "route": route,
                "method": method.upper(),
                "handler": handler,
                "renderer": "json",
                "view": f"{package_name}.views.{h_file}.{handler}",
                "handler_file": h_file,
                "params": params,
                "grouped_params": group_params_by_query_method(
                    r[method]["parameters"] if params else {}
                ),
            }
            routes.append(out)
    return routes


def load_json_file(filename: str) -> dict:
    """Load an OpenAPI JSON file.

    :param filename: filename
    :type filename: str
    :return: OpenAPI file
    :rtype: dict
    """
    with open(filename, "r", encoding="utf-8") as jsonfile:
        return json.load(jsonfile)


def group_params_by_query_method(params: list) -> dict:
    """Group parameters in openapi file by query type.

    The grouping ensures that each parameter is fetched from the url path or query
    string as it is defined in the openapi spec.
    Types: "path", "query_required", "query_optional", "query_multiple"

    :param params: parameters
    :type params: list
    :return: grouped parameters
    :rtype: dict
    """
    param_types = {}
    for param in params:
        add_to_type_group = partial(
            add_object_to_grouping, item=param, grouping=param_types
        )
        if param["in"] == "path":
            param_types = add_to_type_group(group_name="path")
        elif param["in"] == "query" and param["schema"]["type"] == "array":
            param_types = add_to_type_group(group_name="query_multiple")
        elif param["in"] == "query" and param["required"] is True:
            param_types = add_to_type_group(group_name="query_required")
        elif param["in"] == "query" and param["required"] is False:
            param_types = add_to_type_group(group_name="query_optional")

    return param_types


def add_object_to_grouping(
    item: object, grouping: dict, group_name: str
) -> dict:
    """Add item to grouping with group name.

    :param item: item to add to grouping
    :type item: object
    :param grouping: previously grouped items
    :type grouping: dict
    :param group_name: group to append to
    :type group_name: str
    :return: grouped items
    :rtype: dict
    """
    group = grouping.get(group_name, [])
    group.append(item)
    grouping[group_name] = group
    return grouping
