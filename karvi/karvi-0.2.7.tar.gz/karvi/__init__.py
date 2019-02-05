name = "karvi"
__version__ = "0.2.7"


def get_templates_dir():
    import os

    dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates/")
    return dir


def get_version():
    import subprocess

    try:
        hash = subprocess.check_output(["git", "describe", "--tags"])
        hash = hash.decode("utf-8").strip()
    except subprocess.CalledProcessError:
        hash = __version__

    if hash == __version__:
        version = __version__
    else:
        hash = hash.split("-", 3)
        version = "{}.dev{}".format(hash[0], hash[1])
    return version
