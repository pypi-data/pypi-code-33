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
    
    def _prepare_updates_request(self):
        return {
            "package_list": self.rpm_backend.installed_packages,
            "repository_list": self.rpm_backend.enabled_repos,
            "releasever": self.rpm_backend.releasever,
            "basearch": self.rpm_backend.basearch
        }
    
    def _prepare_errata_request(self, errata):
        return {
            "errata_list": errata,
        }

    def evaluate_updates(self):
        response = json.loads(self.vmaas_api.get_updates(self._prepare_updates_request()))
        vulnerable_packages = set()
        available_errata = set()
        for old_pkg in response["update_list"]:
            new_pkgs = response["update_list"][old_pkg].get("available_updates", [])
            if new_pkgs:
                vulnerable_packages.add(old_pkg)
                for new_pkg in new_pkgs:
                    available_errata.add(new_pkg["erratum"])

        if vulnerable_packages:
            found_cves = set()
            response = json.loads(self.vmaas_api.get_errata({"errata_list": list(available_errata)}))
            for erratum in response["errata_list"].values():
                found_cves.update(erratum["cve_list"])

            print("Vulnerable packages:")
            for package in sorted(vulnerable_packages):
                print("  %s" % package)

            print("\nAvailable security errata:")
            for erratum in sorted(available_errata):
                print("  %s" % erratum)
            
            print("\nFound CVEs:")
            for cve in sorted(found_cves):
                print("  %s" % cve)
        else:
            print("No vulnerabilities found.")