# pylint: disable=too-many-arguments
import json
from time import sleep
from requests.exceptions import RequestException
from reliabilly.components.web.http_requestor import HttpRequestor
from reliabilly.settings import Constants, Settings


VERSION_ENDPOINT = f'/{Constants.VERSION_KEY}/'


def build_from_template(template, **kwargs):
    return template.format(**kwargs)


def get_version_from_payload(payload):
    print(payload.text)
    return json.loads(payload.text).get(Constants.VERSION_KEY, None)


def get_service_versions(target_url, service_list, web_client=HttpRequestor()):
    versions = dict()
    for service in service_list:
        url = f'{target_url.strip(Constants.URL_SEPARATOR)}/{service}{VERSION_ENDPOINT}'
        try:
            result = web_client.get(url)
            if result.status_code == Constants.SUCCESS_RESPONSE_CODE:
                versions[service] = get_version_from_payload(result)
            else:
                versions[service] = None
        except RequestException:
            versions[service] = None
    return versions


def check_version_list(versions, expected_version):
    print(versions)
    versions_pass = True
    for _, read_version in versions.items():
        versions_pass &= expected_version == read_version
    return versions_pass


def run_version_check(target_url, expected_version, service_list, web_client=HttpRequestor()):
    versions = get_service_versions(target_url, service_list, web_client)
    return check_version_list(versions, expected_version)


# pylint: disable=too-many-arguments
def check_versions(target_url, expected_version, service_list, timeout=Constants.VERSION_CHECK_TIMEOUT,
                   version_func=run_version_check, sleep_time=5):
    total_time = 0
    result = version_func(target_url, expected_version, service_list)
    while not result:
        print(f'Sleeping {sleep_time} for service cut over...')
        sleep(sleep_time)
        total_time += sleep_time
        result = version_func(target_url, expected_version, service_list)
        if result:
            return result
        if total_time >= timeout:
            return False
    return result


def version():
    return build_from_template(Constants.VERSION_RESPONSE_TEMPLATE, service=Settings.SERVICE_NAME,
                               version=Settings.VERSION, build_number=Settings.BUILD_NUMBER)
