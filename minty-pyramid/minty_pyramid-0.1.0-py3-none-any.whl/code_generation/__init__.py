from . import openapi
from . import generate
import click


@click.command()
@click.option(
    "--package-name",
    help="Name of package to create routes for. Package name is used to create \
import paths in package.",
)
@click.option(
    "--filename", help="OpenAPI filename (JSON file)", default="api-spec.json"
)
def generate_routes(filename, package_name):
    """Create `routes.py` and `test_routes.py` based on OpenAPI file.

    :param filename: json OpenAPI filename
    :type filename: str
    :param package_name: package name
    :type package_name: str
    """
    file = openapi.load_json_file(filename)
    routes = openapi.parse_routes(oa_file=file, package_name=package_name)
    generate.routes(routes, package_name)
    generate.test_routes(routes, package_name)


@click.command()
@click.option("--package-name", help="Name of package to create views for.")
@click.option(
    "--filename", help="OpenAPI filename (JSON file)", default="api-spec.json"
)
def generate_views(filename: str, package_name: str):
    """Generate `views.py` with handlers based on OpenAPI file.

    :param filename: json OpenAPI filename
    :type filename: str
    :param package_name: package name
    :type package_name: str
    """
    file = openapi.load_json_file(filename)
    routes = openapi.parse_routes(oa_file=file, package_name=package_name)
    generate.views(routes, package_name)
