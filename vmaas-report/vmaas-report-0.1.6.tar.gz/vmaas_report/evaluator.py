import json

from vmaas_report.rpm_backend import RpmBackend
from vmaas_report.vmaas_api import VmaasApi


class Evaluator:
    def __init__(self):
        self.vmaas_api = VmaasApi()
        self.rpm_backend = RpmBackend()

    def print_status(self):
        print("VMAAS_SERVER: %s" % self.vmaas_api.server)
        print("VMaaS server version: %s" % self.vmaas_api.get_version())
        db_change = json.loads(self.vmaas_api.get_db_change())
        print("Database data:")
        print("  CVEs changed: %s" % str(db_change["cve_changes"]))
        print("  Errata changed: %s" % str(db_change["errata_changes"]))
        print("  Repositories changed: %s" % str(db_change["repository_changes"]))
        print("  Last change: %s" % str(db_change["last_change"]))
        print("  Exported: %s" % str(db_change["exported"]))
    
    def _prepare_vmaas_request(self):
        return {
            "package_list": self.rpm_backend.installed_packages,
            "repository_list": self.rpm_backend.enabled_repos,
            "releasever": self.rpm_backend.releasever,
            "basearch": self.rpm_backend.basearch
        }

    def evaluate_updates(self):
        response = json.loads(self.vmaas_api.get_updates(self._prepare_vmaas_request()))
        vulnerable_packages = []
        for update in response["update_list"]:
            if response["update_list"][update]["available_updates"]:
                vulnerable_packages.append(update)
        
        if vulnerable_packages:
            print("Vulnerable packages:")
            for package in sorted(vulnerable_packages):
                print("  %s" % package)
        else:
            print("No vulnerabilities found.")