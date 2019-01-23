# pylint: disable=too-many-arguments
from reliabilly.components.tools.newrelic_http_client import NewRelicHttpClient


def get_default_monitoring_client(api_key):
    return NewRelicHttpClient(api_key)


class DataMonitoringClient:
    def __init__(self, api_key, client=None):
        self.client = client
        if not self.client:
            self.client = get_default_monitoring_client(api_key)

    @staticmethod
    def generate_payload(release_number, release_status, release_environment, run_display_url, git_url):
        return {
            "eventType": "ReleaseEvent",
            "environment": release_environment.lower(),
            "build_status": release_status.lower(),
            "release_number": release_number,
            "git_repo": git_url,
            "build_pipeline": run_display_url,
        }

    def create_event(self, release_number, release_status, release_environment, run_display_url, git_url):
        payload = self.generate_payload(release_number, release_status, release_environment, run_display_url, git_url)
        return self.client.create_event(payload)
