import os
import sys
import subprocess
import platform
import typing
import requests


def python_packages() -> typing.List[str]:
    """Return a list of python packages, formatted as package==version."""
    output = subprocess.check_output(["pip3", "freeze"])
    return [line.decode("utf-8") for line in output.splitlines()]


def platform_info() -> typing.List[str]:
    """Return a list of python packages, formatted as package==version."""
    uname = platform.uname()
    return {
        "system": uname.system,
        "node": uname.node,
        "release": uname.release,
        "version": uname.version,
        "machine": uname.machine,
        "processor": uname.processor,
    }


def python_info() -> typing.List[str]:
    """Return a list of python packages, formatted as package==version."""
    return {
        "implementation": platform.python_implementation(),
        "version": platform.python_version(),
        "packages": python_packages(),
        "path": sys.path,
    }


def collect():
    return {"platform": platform_info(), "python": python_info()}


def main():
    url = os.environ.get("VERSIE_URL", "https://versie.io")
    app_id = os.environ.get("VERSIE_APP_ID")
    app_env = os.environ.get("VERSIE_ENVIRONMENT")

    if app_id:
        print(f"Submitting version information to {url}")
        data = collect()
        data["app_env"] = app_env
        try:
            response = requests.post(
                f"{url}/api/application/{app_id}/data", json=data
            )
            response.raise_for_status()
        except requests.RequestException:
            print(f"Versie error: Failed to submit, HTTP code {response.status_code}")
    else:
        print("Warning: no app_id specified, skipping data collection")

    if len(sys.argv) < 2:
        return
    os.execvp(sys.argv[1], sys.argv[1:])
