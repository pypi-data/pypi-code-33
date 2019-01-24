from __future__ import print_function

import os
import subprocess
import configparser


from ..logger import logger
from ..util import run as _run, Path


def git_to_hggit(url):
    logger.info(
        "Seems like a git repository, attempting to use hg-git extension."
    )
    if url.startswith("https"):
        url = url.replace("https", "git")
    elif url.startswith("ssh"):
        url = "git+" + url

    return url


def clone(src, dest=None, hgopts=None, hggit=True):
    if dest is not None and os.path.exists(dest):
        logger.warning("Skipping {}: directory exists!".format(dest))
        return

    if "git" in src:
        if hggit:
            src = git_to_hggit(src)
        else:
            _run("git clone {} {}".format(src, dest))
            return

    _run("hg clone {} {} {}".format(src, dest, hgopts))


def set_remote(dest, src, hgopts=None, hggit=True):
    path = Path(src) / ".hg" / "hgrc"
    if not hggit and not path.exists():
        os.chdir(src)
        subprocess.call(["git", "remote", "set-url", "--push", "origin", dest])
        subprocess.call(["git", "remote", "-v"])
        os.chdir("..")
        return

    config = configparser.ConfigParser()
    config.read(str(path))
    if dest != "None":
        if "git" in dest:
            dest = git_to_hggit(dest)
            config.set("paths", "github", dest)
        else:
            config.set("paths", "origin", dest)

    if not config.has_section("extensions"):
        config.add_section("extensions")

    config.set("extensions", "hgext.bookmarks", "")
    config.set("extensions", "hggit", "")
    with open(str(path), "w") as configfile:
        config.write(configfile)

    os.chdir(src)
    subprocess.call(["hg", "paths"])
    os.chdir("..")


def pull(src, dest, update=True, output=False, hgopts=None, hggit=True):
    os.chdir(dest)
    if "git" in src:
        if not hggit:
            cmd = "git pull " + src
            output = _run(cmd, output)
            os.chdir("..")
            return output
        else:
            src = git_to_hggit(src)

    cmd = "hg pull " + src + hgopts

    if update:
        cmd += " -u"

    output = _run(cmd, output)
    os.chdir("..")
    return output


def push(dest, src, hgopts=None, hggit=True, branch="default"):
    os.chdir(src)
    logger.info(src)
    if dest == "None":
        logger.info("Destination is None.")
        os.chdir("..")
        return

    elif "git" in dest:
        if not hggit:
            cmd = "git push " + dest
            output = _run(cmd)
            os.chdir("..")
            return

        if branch == "default":
            _run("hg bookmark -r default master")
        else:
            output = _run("hg branches", output=True)
            if branch in output:
                output = _run("hg bookmark -r " + branch + " branch-" + branch)
            else:
                logger.warning("Branch", branch, "is closed or does not exist.")
                os.chdir("..")
                return

        dest = git_to_hggit(dest)

    _run("hg push " + dest + hgopts + " -b " + branch)

    os.chdir("..")


def sync(src, pull_repo, push_repo, hgopts=None, hggit=True, branch="default"):
    output = pull(pull_repo, src, output=True, hgopts=hgopts, hggit=hggit)
    if all([string not in output for string in ["no changes", "abort"]]):
        push(push_repo, src, hgopts=hgopts, hggit=hggit, branch=branch)
