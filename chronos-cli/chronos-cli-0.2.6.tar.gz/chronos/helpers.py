"""
Helper functions for chronos CLI.
"""

import subprocess
from subprocess import CalledProcessError
import re

from .semver import SemVer
from .conventional_commits import patterns


class NoGitCommitSinceLastTagException(BaseException):
    """
    Exception meant to alert the user that their are no new commits since the
    last tag.
    """
    pass


class GitTagDoesNotExistError(ValueError):
    """
    Error meant to alert the user that the tag they have specified does not
    exist in the Git repository.
    """
    pass


class NoGitTagsException(BaseException):
    """
    Exception meant to alert the user that the repository does not contain any
    valid Git tags.
    """
    pass


class InvalidTagFormatException(BaseException):
    """
    Exception raised when none of the Git tags present in the repository
    contain a SemVer.
    """
    pass


def git_tags() -> str:
    """
    Calls ``git tag -l --sort=-v:refname`` (sorts output) and returns the
    output as a UTF-8 encoded string. Raises a NoGitTagsException if the
    repository doesn't contain any Git tags.
    """
    try:
        subprocess.check_call(['git', 'fetch', '--tags'])
    except CalledProcessError:
        pass

    cmd = ['git', 'tag', '--list', '--sort=-v:refname']
    rv = subprocess.check_output(cmd).decode('utf-8')

    if rv == '':
        raise NoGitTagsException('No Git tags are present in current repo.')

    return rv


def git_tag_to_semver(git_tag: str) -> SemVer:
    """
    :git_tag: A string representation of a Git tag.

    Searches a Git tag's string representation for a SemVer, and returns that
    as a SemVer object.
    """
    pattern = re.compile(r'[0-9]+\.[0-9]+\.[0-9]+$')
    match = pattern.search(git_tag)
    if match:
        version = match.group(0)
    else:
        raise InvalidTagFormatException('Tag passed contains no SemVer.')

    return SemVer.from_str(version)


def last_git_release_tag(git_tags: str) -> str:
    """
    :git_tags: chronos.helpers.git_tags() function output.

    Returns the latest Git tag ending with a SemVer as a string.
    """
    semver_re = re.compile(r'[0-9]+\.[0-9]+\.[0-9]+$')
    str_ver = []
    for i in git_tags.split():
        if semver_re.search(i):
            str_ver.append(i)

    try:
        return str_ver[0]
    except IndexError:
        raise NoGitTagsException


def git_commits_since_last_tag(last_tag: str) -> dict:
    """
    :last_tag: The Git tag that should serve as the starting point for the
    commit log lookup.

    Calls ``git log <last_tag>.. --format='%H %s'`` and returns the output as a
    dict of hash-message pairs.
    """
    try:
        cmd = ['git', 'log', last_tag + '..', "--format='%H %s'"]
        commit_log = subprocess.check_output(cmd).decode('utf-8')
    except CalledProcessError:
        raise GitTagDoesNotExistError('No such tag:', last_tag)

    if not commit_log:
        raise NoGitCommitSinceLastTagException('No commits since last tag.')

    pattern = re.compile(r'([a-f0-9]{40})\ (.*)')

    rv = {}
    for line in commit_log.split('\n'):
        match = pattern.search(line)
        if match:
            commit_hash = match.group(1)
            commit_msg = match.group(2)
            rv[commit_hash] = commit_msg

    return rv


def parse_commit_log(commit_log: dict) -> str:
    """
    :commit_log: chronos.helpers.git_commits_since_last_tag() output.

    Parse Git log and return either 'maj', 'min', or 'pat'.
    """
    rv = 'pat'

    cc_patterns = patterns()

    for value in commit_log.values():
        if re.search(cc_patterns['feat'], value):
            rv = 'min'
        if re.search(cc_patterns['BREAKING CHANGE'], value):
            rv = 'maj'

    return rv
