# -*- coding: utf-8 -*-
# *******************************************************
#   ____                     _               _
#  / ___|___  _ __ ___   ___| |_   _ __ ___ | |
# | |   / _ \| '_ ` _ \ / _ \ __| | '_ ` _ \| |
# | |__| (_) | | | | | |  __/ |_ _| | | | | | |
#  \____\___/|_| |_| |_|\___|\__(_)_| |_| |_|_|
#
#  Sign up for free at http://www.comet.ml
#  Copyright (C) 2015-2019 Comet ML INC
#  This file can not be copied and/or distributed without the express
#  permission of Comet ML Inc.
# *******************************************************

"""
This module contains git related functions

"""

import logging
import os
import os.path
import sys
from io import BytesIO

import dulwich.errors
import dulwich.objects
import dulwich.patch
import dulwich.porcelain
import dulwich.repo
from six.moves.urllib.parse import urlparse

LOGGER = logging.getLogger(__name__)

EMPTY_BLOB = dulwich.objects.Blob.from_string(b"")


def _patched_path_to_tree_path(repopath, path):
    """Convert a path to a path usable in e.g. an index.
    :param repopath: Repository
    :param path: A path
    :return: A path formatted for use in e.g. an index
    """
    if os.path.isabs(path):
        path = os.path.relpath(path, repopath)
    if os.path.sep != "/":
        path = path.replace(os.path.sep, "/")
    return path.encode(sys.getfilesystemencoding())


def to_utf8(str_or_bytes):
    if hasattr(str_or_bytes, "decode"):
        return str_or_bytes.decode("utf-8", errors="replace")

    return str_or_bytes


def get_user(repo):
    """ Retrieve the configured user from a dulwich git repository
    """
    try:
        # The user name might not be valid UTF-8
        return to_utf8(repo.get_config_stack().get("user", "name"))

    except KeyError:
        return None


def get_root(repo):
    """ Retrieve the hash of the repo root to uniquely identify the git
    repository
    """

    # Check if the repository is empty
    if len(repo.get_refs()) == 0:
        return None

    # Get walker needs at least the HEAD ref to be present
    walker = repo.get_walker()

    entry = None

    # Iterate on the lazy iterator to get to the last one
    for entry in walker:
        pass

    assert entry is not None

    # SHA should always be valid utf-8
    return to_utf8(entry.commit.id)


def get_branch(repo):
    """ Retrieve the current branch of a dulwich repository
    """
    refs = repo.get_refs()

    # Check if the repository is empty
    if len(repo.get_refs()) == 0:
        return None

    head = repo.head()

    for ref, sha in refs.items():
        if sha == head and ref != b"HEAD":
            return to_utf8(ref)


def get_git_commit(repo):
    try:
        # SHA should always be valid utf-8
        return to_utf8(repo.head())

    except KeyError:
        return None


def git_status(repo):
    try:
        # Monkey-patch a dulwich method, see
        # https://github.com/dulwich/dulwich/pull/601 for an explanation why
        original = dulwich.porcelain.path_to_tree_path
        dulwich.porcelain.path_to_tree_path = _patched_path_to_tree_path

        status = dulwich.porcelain.status(repo)

        staged = {
            key: [to_utf8(path) for path in items]
            for (key, items) in status.staged.items()
        }
        unstaged = [to_utf8(path) for path in status.unstaged]
        untracked = [to_utf8(path) for path in status.untracked]

        return {"staged": staged, "unstaged": unstaged, "untracked": untracked}

    finally:
        dulwich.porcelain.path_to_tree_path = original


def get_origin_url(repo):
    repo_config = repo.get_config()
    try:
        # The origin url might not be valid UTF-8
        return to_utf8(repo_config.get((b"remote", b"origin"), "url"))

    except KeyError:
        return None


def get_repo_name(origin_url):
    if origin_url is None:
        return None

    # First parse the url to get rid of possible HTTP comments or arguments
    parsed_url = urlparse(origin_url)
    # Remove potential leading /
    path = parsed_url.path.rstrip("/")
    repo_name = path.split("/")[-1]

    # Remove potential leading .git
    if repo_name.endswith(".git"):
        repo_name = repo_name[:-4]
    return repo_name


def gen_diff_header(paths, modes, shas):
    """Write a blob diff header.

    :param paths: Tuple with old and new path
    :param modes: Tuple with old and new modes
    :param shas: Tuple with old and new shas

    Patched, see https://github.com/dulwich/dulwich/issues/642 for explanation
    """
    (old_path, new_path) = paths
    (old_mode, new_mode) = modes
    (old_sha, new_sha) = shas
    shortid = dulwich.patch.shortid
    yield b"diff --git " + old_path + b" " + new_path + b"\n"

    if old_mode != new_mode:
        if new_mode is not None:
            if old_mode is not None:
                yield ("old file mode %o\n" % old_mode).encode("ascii")

            yield ("new file mode %o\n" % new_mode).encode("ascii")

        else:
            yield ("deleted file mode %o\n" % old_mode).encode("ascii")

    yield b"index " + shortid(old_sha) + b".." + shortid(new_sha)

    if new_mode is not None and old_mode is not None:
        yield (" %o" % new_mode).encode("ascii")

    yield b"\n"


def _get_unstaged_changes(files, repo):
    index = repo.open_index()

    for unstaged_file in dulwich.index.get_unstaged_changes(index, repo.path):

        file_path = os.path.join(repo.path.encode(), unstaged_file)
        if os.path.isfile(file_path):
            st = os.lstat(file_path)
            blob = dulwich.index.blob_from_path_and_stat(file_path, st)
            mode = dulwich.index.cleanup_mode(st.st_mode)

            # The file can be added in the index
            if unstaged_file in files["added"]:
                files["added"][unstaged_file] = (blob, mode)
            else:
                files["modified"][unstaged_file] = (blob, mode)
        else:
            files["removed"][unstaged_file] = (EMPTY_BLOB, None)

    return files


def _get_staged_changes(files, repo, head, tree_id):
    index = repo.open_index()
    changes = index.changes_from_tree(repo.object_store, tree_id)

    # Staged changes
    for change in changes:
        (old_path, new_path), (old_mode, new_mode), (old_sha, new_sha) = change
        if not old_path:
            blob = repo.object_store[new_sha]
            assert new_path not in files["added"]
            files["added"][new_path] = (blob, new_mode)
        elif not new_path:
            assert old_path not in files["removed"]
            files["removed"][old_path] = (EMPTY_BLOB, new_mode)
        elif old_path == new_path:
            if new_path not in files["modified"]:
                blob = repo.object_store[new_sha]
                files["modified"][new_path] = (blob, new_mode)
        else:
            raise NotImplementedError(
                "Unknown file status %r %r" % (old_path, old_mode)
            )

    return files


def _write_hunk(
    diff,
    old_path,
    new_path,
    old_mode,
    new_mode,
    old_sha,
    new_sha,
    old_content,
    new_content,
):
    diff_header = gen_diff_header(
        (old_path, new_path), (old_mode, new_mode), (old_sha, new_sha)
    )
    diff.writelines(diff_header)

    diff.writelines(
        dulwich.patch.unified_diff(old_content, new_content, old_path, new_path)
    )


def get_git_patch(repo, unstaged=True):
    files = {"added": {}, "removed": {}, "modified": {}}

    try:
        head = repo.head()
    except KeyError:
        return None

    tree_id = repo[head].tree
    tree = repo[tree_id]

    files = _get_staged_changes(files, repo, head, tree_id)

    if unstaged is True:
        files = _get_unstaged_changes(files, repo)

    LOGGER.debug("Git files changes %r", files)

    if files is None:
        return None

    no_added = len(files["added"]) == 0
    no_removed = len(files["removed"]) == 0
    no_modified = len(files["modified"]) == 0

    if no_added and no_removed and no_modified:
        return None

    # Generate the diff

    diff = BytesIO()

    for added_file, (added_blob, added_mode) in sorted(files["added"].items()):
        old_path = b"a/" + added_file
        new_path = b"b/" + added_file

        old_content = EMPTY_BLOB.splitlines()
        new_content = added_blob.splitlines()

        _write_hunk(
            diff,
            old_path=old_path,
            new_path=new_path,
            old_mode=None,
            new_mode=added_mode,
            old_sha=None,
            new_sha=added_blob.id,
            old_content=old_content,
            new_content=new_content,
        )

    for removed_file, (removed_blob, removed_mode) in sorted(files["removed"].items()):
        old_path = b"a/" + removed_file
        new_path = b"b/" + removed_file

        (old_mode, old_sha) = tree.lookup_path(repo.__getitem__, removed_file)
        old_blob = repo[old_sha]

        old_content = old_blob.splitlines()
        new_content = removed_blob.splitlines()

        _write_hunk(
            diff,
            old_path=old_path,
            new_path=new_path,
            old_mode=old_mode,
            new_mode=removed_mode,
            old_sha=old_sha,
            new_sha=None,
            old_content=old_content,
            new_content=new_content,
        )

    for modified_file, (modified_blob, modified_mode) in sorted(
        files["modified"].items()
    ):
        old_path = b"a/" + modified_file
        new_path = b"b/" + modified_file

        (old_mode, old_sha) = tree.lookup_path(repo.__getitem__, modified_file)
        old_blob = repo[old_sha]

        old_content = old_blob.splitlines()
        new_content = modified_blob.splitlines()

        _write_hunk(
            diff,
            old_path=old_path,
            new_path=new_path,
            old_mode=old_mode,
            new_mode=modified_mode,
            old_sha=old_sha,
            new_sha=modified_blob.id,
            old_content=old_content,
            new_content=new_content,
        )

    diff.seek(0)
    return diff.getvalue()


def find_git_patch(path):
    # First find the repo
    repo = find_git_repo(path)

    if not repo:
        return None

    patch = get_git_patch(repo)

    # Close the repo to close all opened fds
    repo.close()

    return patch


def find_git_repo(repo_path):
    # Early-exit if repo_path is repo root
    try:
        return dulwich.repo.Repo(repo_path)

    except dulwich.errors.NotGitRepository:
        pass

    path = repo_path
    while path:
        parent_path = os.path.dirname(path)
        # Avoid infinite loop
        if parent_path == path:
            break

        path = parent_path
        try:
            return dulwich.repo.Repo(path)

        except dulwich.errors.NotGitRepository:
            pass


def get_git_metadata(path):
    # First find the repo
    repo = find_git_repo(path)

    if not repo:
        return None

    origin = get_origin_url(repo)
    repo_name = get_repo_name(origin)

    data = {
        "user": get_user(repo),
        "root": get_root(repo),
        "branch": get_branch(repo),
        "parent": get_git_commit(repo),
        "status": None,
        "origin": origin,
        "repo_name": repo_name,
    }

    # Close the repo to close all opened fds
    repo.close()

    return data
