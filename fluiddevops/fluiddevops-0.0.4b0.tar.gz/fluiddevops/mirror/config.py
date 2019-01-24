from __future__ import print_function

from builtins import input

import configparser
import sys
import re
from os.path import join, exists, abspath


def get_repos(sections):
    return [r.split(":")[1] for r in sections if r.startswith("repo")]


def get_default_config(pull_base, push_base, repos, hggit=True):
    config = configparser.ConfigParser()

    config.add_section("defaults")
    config.set("defaults", "pull_base", pull_base)
    config.set("defaults", "push_base", push_base)
    config.set("defaults", "ssh", "ssh -oStrictHostKeyChecking=no")
    config.set("defaults", "use_hg_git", str(hggit))

    if isinstance(repos, str):
        # Split , ; or space separated values
        repos = re.findall(r"[^,;\s]+", repos)
    for repo in repos:
        section = ":".join(("repo", repo))
        config.add_section(section)
        config.set(section, "pull", "")
        config.set(section, "push", "")

    return config


def init_config(path, hggit=True, **kwargs):
    path = str(path)
    if exists(path):
        print("Already exists!", path)
        return

    default = {}
    default["pull_base"] = "https://bitbucket.org/fluiddyn"
    default["push_base"] = "ssh://hg@bitbucket.org/fluiddyn"
    default["repos"] = "fluiddyn, fluidfft, fluidsim"

    # Ask
    if "pull_base" not in kwargs:
        kwargs["pull_base"] = input(
            "Base URL to pull from (default: {}) :".format(default["pull_base"])
        )

    if "push_base" not in kwargs:
        kwargs["push_base"] = input(
            "Base URL to push to (default: {}) :".format(default["push_base"])
        )

    if "repos" not in kwargs:
        kwargs["repos"] = input(
            "Repositories to mirror (default: {}) :".format(default["repos"])
        )

    for k, v in kwargs.items():
        if v == "":
            kwargs[k] = default[k]

    kwargs["hggit"] = hggit
    config = get_default_config(**kwargs)
    with open(abspath(path), "w") as configfile:
        config.write(configfile)

    print("\nCreated {}. Now run:\n\tfluidmirror clone".format(path))


def read_config(path, output=False):
    config = configparser.ConfigParser()
    path = str(path)
    if not exists(path):
        raise OSError(path + " not found")

    config.read(path)

    pull_base = config["defaults"]["pull_base"]
    push_base = config["defaults"]["push_base"]
    repos = get_repos(config.sections())

    for repo in repos:
        if output:
            print("\nrepo:", repo)

        key = "repo:" + repo
        pull = config[key]["pull"]
        if pull == "":
            pull = join(pull_base, repo)
            config.set(key, "pull", pull)

        push = config["repo:" + repo]["push"]
        if push == "":
            push = join(push_base, repo)
            config.set(key, "push", push)

        if output:
            print("pull:", pull)
            print("push:", push)

    return config


if __name__ == "__main__":
    read_config(sys.argv[1])
