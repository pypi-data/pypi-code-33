#!/usr/bin/env python

from vmaas_report.rpm_backend import RpmBackend
from vmaas_report.vmaas_api import VmaasApi

def main():
    rpm_backend = RpmBackend()
    vmaas_api = VmaasApi()
    print("installed packages: %s" % rpm_backend.installed_packages)
    print("installed packages total: %s" % len(rpm_backend.installed_packages))
    print("enabled repos: %s" % rpm_backend.enabled_repos)
    print("releasever: %s" % rpm_backend.releasever)
    print("basearch: %s" % rpm_backend.basearch)
    vmaas_api.print_status()

if __name__ == "__main__":
    main()
