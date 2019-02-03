from os.path import join, dirname
from fabric.state import env


def config():
    env.hosts = ["samuelk@himec04.cs.kuleuven.be"]
    env.password = "2R5-w6Z-Lo7-REx"

    env.remote_root = "/home/samuelk/projects/smtlearn/"
    env.remote_python = env.remote_root + "env4/bin/python"
    env.remote_activate = env.remote_root + "env4/bin/activate"


