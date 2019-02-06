import datetime
import os

from jinja2 import Environment, PackageLoader


def load_template(template_name: str):
    """Load template from template folder.

    :param template_name: template name
    :type template_name: str
    :return: template
    :rtype: jinja2 template
    """
    pkg_loader = PackageLoader(__name__)
    env = Environment(loader=pkg_loader)
    env.globals["now"] = datetime.datetime.now
    return env.get_template(template_name)


def views(routes: list, package_name: str):
    """Create `views.py` from the supplied routes list.

    :param routes: routes to create file with
    :type routes: list
    :param package_name: package name
    :type package_name: str
    :return: file created
    :rtype: bool
    """
    template = load_template("views.j2")
    content = template.render(views=routes)

    filename = os.path.join(package_name, "views", "views.py")
    with open(filename, "x", encoding="utf-8") as file:
        file.write(content)

    print(f"\nCreated file: '{filename}' with views:\n")
    for r in routes:
        print(f" - {r['handler']}")


def routes(routes: list, package_name: str):
    """Create `routes.py` for given routes in package.

    :param routes: routes to create file with
    :type routes: list
    :param package_name: package name
    :type package_name: str
    :return: file created
    :rtype: bool
    """
    template = load_template("routes.j2")

    content = template.render(routes=routes)

    filename = os.path.join(package_name, "routes", "routes.py")
    with open(filename, "w", encoding="utf-8") as file:
        file.write(content)

    print(f"\nCreated file: '{filename}' with routes:\n")
    for r in routes:
        print(f" - {r['handler']}: {r['method']} '{r['route']}'")


def test_routes(routes: list, package_name):
    """Create 'test_routes_routes.py' for given routes in package.

    :param routes: routes to create file with
    :type routes: list
    :param package_name: package name
    :type package_name: str
    :return: file created
    :rtype: bool
    """
    grouped_routes = group_routes_by(routes=routes, param="handler_file")
    t = load_template("test_routes.j2")
    content = t.render(routes=grouped_routes, package_name=package_name)

    filename = os.path.join("tests", "test_routes.py")
    with open(filename, "w", encoding="utf-8") as file:
        file.write(content)

    print(f"\nCreated file: '{filename}'\n")


def group_routes_by(routes: list, param: str) -> dict:
    """Group routes by parameter.

    Create different groupings to accomodate different templates

    :param routes: routes
    :type routes: list
    :param param: parameter to group by
    :type param: str
    :return: grouped routes
    :rtype: dict
    """
    grouped_routes = {}
    for route in routes:
        grouped_by_param = grouped_routes.get(route[param], [])
        grouped_by_param.append(route)
        grouped_routes[route[param]] = grouped_by_param
    return grouped_routes
