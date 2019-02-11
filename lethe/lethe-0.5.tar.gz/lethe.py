#!/usr/bin/env python3
"""
Git snapshotting tool
"""

import subprocess
import tempfile
import datetime
import argparse
from itertools import chain
from typing import List
import sys


__author__ = 'Jan Petykeiwicz'
version = 0.5


def _run(command: str or List[str], **kwargs):
    """
    Wrapper for subprocess.run():
    - Accepts args as either a list of strings or space-delimited string
    - Captures and returns stdouti
    """
    if isinstance(command, str):
        args = command.split()
    else:
        args = command
#    print('run', ' '.join(args))
    result = subprocess.run(args, stdout=subprocess.PIPE, **kwargs)
    return result.stdout.decode().strip()


def get_root(cwd: str=None) -> str:
    """
    Get the root directory of a git repository
    """
    root = _run('git rev-parse --show-toplevel', cwd=cwd)
    if not root:
        raise Exception('Must be run from inside git repository!')
    return root


def get_obj(ref: str, cwd: str=None) -> str:
    """
    Transform a ref into its corresponding hash using git-rev-parse
    """
    sha =  _run('git rev-parse --quiet --verify'.split() + [ref], cwd=cwd)
    return sha


def get_commit(ref: str, cwd: str=None) -> str:
    """
    Transform a ref to a commit into its corresponding hash using git-rev-parse
    """
    return get_obj(ref, cwd=cwd)


def get_tree(ref: str, cwd: str=None) -> str:
    """
    Take a ref to a commit, and return the hash of the tree it points to
    """
    return get_obj(ref + ':', cwd=cwd)


def commit_tree(tree: str,
                parents: List[str],
                message: str = None,
                cwd: str = None,
                ) -> str:
    """
    Create a commit pointing to the given tree, with the specified parent commits and message.
    Return the hash of the created commit.
    """
    if message is None:
        message = 'snapshot ' + str(datetime.datetime.now())

    pargs = list(chain.from_iterable(('-p', p) for p in parents))
    commit = _run(['git', 'commit-tree', tree, *pargs, '-m', message], cwd=cwd)            # Create commit
    return commit


def update_ref(target_ref: str,
               target_commit: str,
               old_commit: str = None,
               message: str = 'new snapshot',
               cwd: str = None,
               ) -> str:
    """
    Update target_ref to point to target_commit, optionally verifying that
        it points old_commit before the update.
    Returns the resulting ref.
    """
    cmd = ['git', 'update-ref', '-m', message, target_ref, target_commit]
    if old_commit is not None:
        cmd.append(old_commit)
    result_ref = _run(cmd, cwd=cwd)
    return result_ref


def deref_symref(ref: str, cwd: str=None) -> str:
    """
    Dereference a symbolic ref
    """
    return _run(['git', 'symbolic-ref', '--quiet', ref], cwd=cwd)


def find_merge_base(commits: List[str], cwd: str=None) -> str:
    """
    Find the "best common ancestor" commit.
    """
    base = _run(['git', 'merge-base', *commits], cwd=cwd)
    return base


def snap_tree(cwd: str=None) -> str:
    """
    Create a new tree, consisting of all non-ignored files in the repository.
    Return the hash of the tree.
    """
    with tempfile.TemporaryDirectory() as tmp_dir:
        env = {'GIT_INDEX_FILE': tmp_dir + '/git-snapshot-index'}

        # TODO: Mayve need cwd=get_root(cwd) here?
        _run('git add --all', env=env, cwd=cwd)
        tree = _run('git write-tree', env=env, cwd=cwd)
    return tree


def snap_ref(parent_refs: List[str],
             target_refs: List[str],
             message: str = None,
             cwd: str = None,
             ) -> str:
    """
    <message> is used as the commit message.
    """
    new_tree = snap_tree(cwd=cwd)
    parent_commits = [c for c in [get_commit(p, cwd=cwd) for p in parent_refs] if c]
    old_commits = [get_commit(t, cwd=cwd) for t in target_refs]

    extant_old_commits = list(set(c for c in old_commits if c))
    new_parents = list(set(p for p in parent_commits
                           if p != find_merge_base([p] + extant_old_commits, cwd=cwd)))

#    if not new_parents:
#        tree_unchanged = all(new_tree == get_tree(c, cwd=cwd) for c in old_commits)
#        if tree_unchanged:
#            return new_tree

    commit = commit_tree(new_tree, extant_old_commits + new_parents, message, cwd=cwd)

    for target_ref, old_commit in zip(target_refs, old_commits):
        # update ref to point to commit, or create new ref
        old_or_none = old_commit if old_commit else None
        update_ref(target_ref, commit, old_commit=old_or_none, cwd=cwd)

    return commit



def snap(parent_refs: List[str] = None,
         target_refs: List[str] = None,
         message: str = None,
         cwd: str = None,
         ) -> str:
    """
    Create a new commit of all non-ignored files in the repository.

    <parent_refs> default to ['HEAD'].
    If there are any symbolic refs in <parent_refs>, the refs
        they point to are added to <parent_refs>.

    All commits pointed to by existing <parent_refs> and <target_refs>,
        become parents of the newly created commit.

    <target_refs> are created/updated to point the commit.
        Default is
            'refs/lethe/head_name' for each parent ref of the form
                'refs/heads/head_name', and
            'refs/lethe/path/to/ref' for each parent ref of the form
                'refs/path/to/ref'.
    <message> is used as the commit message.
    """
    if parent_refs is None:
        parent_refs = ['HEAD']

    parent_refs += [r for r in [deref_symref(s, cwd=cwd) for s in parent_refs] if r]

    if target_refs is None:
        target_refs = []
        for p in parent_refs:
            if p.startswith('refs/'):
                p = p[len('refs/'):]

            target_refs.append('refs/lethe/' + p)

    commit = snap_ref(parent_refs, target_refs, message=message, cwd=cwd)
    return commit


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--parent', '-p', action='append', default=['HEAD'])
    parser.add_argument('--target', '-t', action='append')
    parser.add_argument('--message', '-m')
    parser.add_argument('--repo', '-r')

    args = parser.parse_args()

    print(snap(parent_refs=args.parent,
               target_refs=args.target,
               message=args.message,
               cwd=args.repo))
    return 0


if __name__ == '__main__':
    main()

