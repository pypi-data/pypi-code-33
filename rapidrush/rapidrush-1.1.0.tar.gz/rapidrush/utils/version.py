# Copyright (c) 2019 bluelief.
# This source code is licensed under the MIT license.

import datetime
import os
import platform
import subprocess
import sys


repo_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def get_version(version):
    main = ".".join(map(str, version[0:3]))

    sub = ""
    if version[3] != "stable":
        mapping = {"alpha": "a", "beta": "b", "rc": "rc"}
        sub = mapping[version[3]] + str(version[4])

    return main + sub


def git_commit_hash():
    # Another way: 'git rev-parse HEAD'
    git_log = subprocess.Popen(
        "git log --pretty=format:%H -1 HEAD",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=True,
        cwd=repo_dir,
        universal_newlines=True,
    )
    commit_hash = git_log.communicate()[0].strip()

    return commit_hash


def git_commit_date():
    git_log = subprocess.Popen(
        "git log --pretty=format:%ct -1 HEAD",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=True,
        cwd=repo_dir,
        universal_newlines=True,
    )
    timestamp = git_log.communicate()[0]
    try:
        timestamp = datetime.datetime.utcfromtimestamp(int(timestamp))
    except ValueError:
        return None

    return timestamp.strftime("%Y-%m-%d__%H:%M:%S").strip()


def git_commit_count():
    git_log = subprocess.Popen(
        "git rev-list HEAD --count",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=True,
        cwd=repo_dir,
        universal_newlines=True,
    )
    commit_count = git_log.communicate()[0].strip()

    return commit_count


def git_describe():
    git_log = subprocess.Popen(
        "git describe --tags",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=True,
        cwd=repo_dir,
        universal_newlines=True,
    )
    commit_hash = git_log.communicate()[0].strip()

    return commit_hash
