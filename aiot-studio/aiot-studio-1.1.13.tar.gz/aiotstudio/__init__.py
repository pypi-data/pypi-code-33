
__author__ = "mnubo, inc."

try:
    import pkg_resources
    __version__ = pkg_resources.get_distribution("aiot-studio").version
except:
    __version__ = "N/A"