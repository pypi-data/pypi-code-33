from cc_connector_cli.connector_cli import run_connector
from red_connector_xnat.http import Http
from red_connector_xnat.version import VERSION


def main():
    run_connector(Http, version=VERSION)


if __name__ == '__main__':
    main()
