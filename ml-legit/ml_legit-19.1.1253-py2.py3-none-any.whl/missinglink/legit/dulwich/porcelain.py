 # porcelain.py -- Porcelain-like layer on top of Dulwich
# Copyright (C) 2013 Jelmer Vernooij <jelmer@samba.org>
#
# Dulwich is dual-licensed under the Apache License, Version 2.0 and the GNU
# General Public License as public by the Free Software Foundation; version 2.0
# or (at your option) any later version. You can redistribute it and/or
# modify it under the terms of either of these two licenses.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# You should have received a copy of the licenses; if not, see
# <http://www.gnu.org/licenses/> for a copy of the GNU General Public License
# and <http://www.apache.org/licenses/LICENSE-2.0> for a copy of the Apache
# License, Version 2.0.
#

"""Simple wrapper that provides porcelain-like functions on top of Dulwich.

Currently implemented:
 * archive
 * add
 * branch{_create,_delete,_list}
 * check-ignore
 * clone
 * commit
 * commit-tree
 * daemon
 * diff-tree
 * fetch
 * init
 * ls-remote
 * ls-tree
 * pull
 * push
 * rm
 * remote{_add}
 * receive-pack
 * reset
 * rev-list
 * tag{_create,_delete,_list}
 * upload-pack
 * update-server-info
 * status
 * symbolic-ref

These functions are meant to behave similarly to the git subcommands.
Differences in behaviour are considered bugs.
"""

from collections import namedtuple
from contextlib import (
    closing,
    contextmanager,
)
import os
import posixpath
import stat
import sys
import time

from .archive import (
    tar_stream,
    )
from .client import (
    get_transport_and_path,
    )
from .diff_tree import (
    CHANGE_ADD,
    CHANGE_DELETE,
    CHANGE_MODIFY,
    CHANGE_RENAME,
    CHANGE_COPY,
    RENAME_CHANGE_TYPES,
    )
from .errors import (
    SendPackError,
    UpdateRefsError,
    )
from .ignore import IgnoreFilterManager
from .index import (
    get_unstaged_changes,
    )
from .object_store import (
    tree_lookup_path,
    )
from .objects import (
    Commit,
    Tag,
    format_timezone,
    parse_timezone,
    pretty_format_tree_entry,
    )
from .objectspec import (
    parse_object,
    parse_reftuples,
    )
from .pack import (
    write_pack_index,
    write_pack_objects,
    )
from .patch import write_tree_diff
from .protocol import (
    Protocol,
    ZERO_SHA,
    )
from .refs import ANNOTATED_TAG_SUFFIX
from .repo import (BaseRepo, Repo)
from .server import (
    FileSystemBackend,
    TCPGitServer,
    ReceivePackHandler,
    UploadPackHandler,
    update_server_info as server_update_server_info,
    )


# Module level tuple definition for status output
GitStatus = namedtuple('GitStatus', 'staged unstaged untracked')


default_bytes_out_stream = getattr(sys.stdout, 'buffer', sys.stdout)
default_bytes_err_stream = getattr(sys.stderr, 'buffer', sys.stderr)


DEFAULT_ENCODING = 'utf-8'


class RemoteExists(Exception):
    """Raised when the remote already exists."""


def open_repo(path_or_repo):
    """Open an argument that can be a repository or a path for a repository."""
    if isinstance(path_or_repo, BaseRepo):
        return path_or_repo
    return Repo(path_or_repo)


@contextmanager
def _noop_context_manager(obj):
    """Context manager that has the same api as closing but does nothing."""
    yield obj


def open_repo_closing(path_or_repo, data_path=None):
    """Open an argument that can be a repository or a path for a repository.
    returns a context manager that will close the repo on exit if the argument
    is a path, else does nothing if the argument is a repo.
    """
    if isinstance(path_or_repo, BaseRepo):
        return _noop_context_manager(path_or_repo)

    assert data_path is not None
    return closing(Repo(path_or_repo, data_path))


def path_to_tree_path(repopath, path):
    """Convert a path to a path usable in e.g. an index.

    :param repo: Repository
    :param path: A path
    :return: A path formatted for use in e.g. an index
    """
    os.path.relpath(path, repopath)
    if os.path.sep != '/':
        path = path.replace(os.path.sep, '/')
    return path.encode(sys.getfilesystemencoding())


def archive(repo, committish=None, outstream=default_bytes_out_stream,
            errstream=default_bytes_err_stream):
    """Create an archive.

    :param repo: Path of repository for which to generate an archive.
    :param committish: Commit SHA1 or ref to use
    :param outstream: Output stream (defaults to stdout)
    :param errstream: Error stream (defaults to stderr)
    """

    if committish is None:
        committish = "HEAD"
    with open_repo_closing(repo) as repo_obj:
        c = repo_obj[committish]
        for chunk in tar_stream(
                repo_obj.object_store, repo_obj.object_store[c.tree],
                c.commit_time):
            outstream.write(chunk)


def update_server_info(repo="."):
    """Update server info files for a repository.

    :param repo: path to the repository
    """
    with open_repo_closing(repo) as r:
        server_update_server_info(r)


def symbolic_ref(repo, ref_name, force=False):
    """Set git symbolic ref into HEAD.

    :param repo: path to the repository
    :param ref_name: short name of the new ref
    :param force: force settings without checking if it exists in refs/heads
    """
    with open_repo_closing(repo) as repo_obj:
        ref_path = b'refs/heads/' + ref_name
        if not force and ref_path not in repo_obj.refs.keys():
            raise ValueError('fatal: ref `%s` is not a ref' % ref_name)
        repo_obj.refs.set_symbolic_ref(b'HEAD', ref_path)


def commit(repo=".", message=None, author=None, committer=None):
    """Create a new commit.

    :param repo: Path to repository
    :param message: Optional commit message
    :param author: Optional author name and email
    :param committer: Optional committer name and email
    :return: SHA1 of the new commit
    """
    # FIXME: Support --all argument
    # FIXME: Support --signoff argument
    with open_repo_closing(repo) as r:
        return r.do_commit(message=make_bytes(message), author=author, committer=committer)


def commit_tree(repo, tree, message=None, author=None, committer=None):
    """Create a new commit object.

    :param repo: Path to repository
    :param tree: An existing tree object
    :param author: Optional author name and email
    :param committer: Optional committer name and email
    """
    with open_repo_closing(repo) as r:
        return r.do_commit(
            message=message, tree=tree, committer=committer, author=author)


def init(path=".", bare=False):
    """Create a new git repository.

    :param path: Path to repository.
    :param bare: Whether to create a bare repository.
    :return: A Repo instance
    """
    if not os.path.exists(path):
        os.mkdir(path)

    if bare:
        return Repo.init_bare(path)
    else:
        return Repo.init(path)


def clone(source, target=None, bare=False, checkout=None,
          errstream=default_bytes_err_stream, outstream=None,
          origin=b"origin"):
    """Clone a local or remote git repository.

    :param source: Path or URL for source repository
    :param target: Path to target repository (optional)
    :param bare: Whether or not to create a bare repository
    :param checkout: Whether or not to check-out HEAD after cloning
    :param errstream: Optional stream to write progress to
    :param outstream: Optional stream to write progress to (deprecated)
    :return: The new repository
    """
    if outstream is not None:
        import warnings
        warnings.warn(
            "outstream= has been deprecated in favour of errstream=.",
            DeprecationWarning, stacklevel=3)
        errstream = outstream

    if checkout is None:
        checkout = (not bare)
    if checkout and bare:
        raise ValueError("checkout and bare are incompatible")
    client, host_path = get_transport_and_path(source)

    if target is None:
        target = host_path.split("/")[-1]

    if not os.path.exists(target):
        os.mkdir(target)

    if bare:
        r = Repo.init_bare(target)
    else:
        r = Repo.init(target)
    try:
        remote_refs = client.fetch(
            host_path, r, determine_wants=r.object_store.determine_wants_all,
            progress=errstream.write)
        r.refs.import_refs(
            b'refs/remotes/' + origin,
            {n[len(b'refs/heads/'):]: v for (n, v) in remote_refs.items()
                if n.startswith(b'refs/heads/')})
        r.refs.import_refs(
            b'refs/tags',
            {n[len(b'refs/tags/'):]: v for (n, v) in remote_refs.items()
                if n.startswith(b'refs/tags/') and
                not n.endswith(ANNOTATED_TAG_SUFFIX)})
        if b"HEAD" in remote_refs and not bare:
            # TODO(jelmer): Support symref capability,
            # https://github.com/jelmer/dulwich/issues/485
            r[b"HEAD"] = remote_refs[b"HEAD"]
        target_config = r.get_config()
        if not isinstance(source, bytes):
            source = source.encode(DEFAULT_ENCODING)
        target_config.set((b'remote', b'origin'), b'url', source)
        target_config.set(
            (b'remote', b'origin'), b'fetch',
            b'+refs/heads/*:refs/remotes/origin/*')
        target_config.write_to_path()
        if checkout and b"HEAD" in r.refs:
            errstream.write(b'Checking out HEAD\n')
            r.reset_index()
    except:
        r.close()
        raise

    return r


def get_rel_path(repo, paths=None):
    ignored = set()

    ignore_manager = repo.get_ignore_filter_manager()
    if not paths:
         paths = list(get_untracked_paths(os.getcwd(), r.data_path, r.open_index()))

    relpaths = []

    if not isinstance(paths, list):
         paths = [paths]

    for p in paths:
        relpath = os.path.relpath(p, repo.data_path)
        # FIXME: Support patterns, directories.
        if ignore_manager.is_ignored(relpath):
            ignored.add(relpath)
            continue

        relpaths.append(relpath)

    return relpaths, ignored


def commit_decode(commit, contents, default_encoding=DEFAULT_ENCODING):
    if commit.encoding is not None:
        return contents.decode(commit.encoding, "replace")
    return contents.decode(default_encoding, "replace")


def print_commit(commit, decode, outstream=sys.stdout):
    """Write a human-readable commit log entry.

    :param commit: A `Commit` object
    :param outstream: A stream file to write to
    """
    outstream.write("-" * 50 + "\n")
    outstream.write("commit: " + commit.id.decode('ascii') + "\n")
    if len(commit.parents) > 1:
        outstream.write(
            "merge: " +
            "...".join([c.decode('ascii') for c in commit.parents[1:]]) + "\n")
    outstream.write("Author: " + decode(commit.author) + "\n")
    if commit.author != commit.committer:
        outstream.write("Committer: " + decode(commit.committer) + "\n")

    time_tuple = time.gmtime(commit.author_time + commit.author_timezone)
    time_str = time.strftime("%a %b %d %Y %H:%M:%S", time_tuple)
    timezone_str = format_timezone(commit.author_timezone).decode('ascii')
    outstream.write("Date:   " + time_str + " " + timezone_str + "\n")
    outstream.write("\n")
    outstream.write(decode(commit.message) + "\n")
    outstream.write("\n")


def print_tag(tag, decode, outstream=sys.stdout):
    """Write a human-readable tag.

    :param tag: A `Tag` object
    :param decode: Function for decoding bytes to unicode string
    :param outstream: A stream to write to
    """
    outstream.write("Tagger: " + decode(tag.tagger) + "\n")
    outstream.write("Date:   " + decode(tag.tag_time) + "\n")
    outstream.write("\n")
    outstream.write(decode(tag.message) + "\n")
    outstream.write("\n")


def show_blob(repo, blob, decode, outstream=sys.stdout):
    """Write a blob to a stream.

    :param repo: A `Repo` object
    :param blob: A `Blob` object
    :param decode: Function for decoding bytes to unicode string
    :param outstream: A stream file to write to
    """
    outstream.write(decode(blob.data))


def show_commit(repo, commit, decode, outstream=sys.stdout):
    """Show a commit to a stream.

    :param repo: A `Repo` object
    :param commit: A `Commit` object
    :param decode: Function for decoding bytes to unicode string
    :param outstream: Stream to write to
    """
    print_commit(commit, decode=decode, outstream=outstream)
    parent_commit = repo[commit.parents[0]]
    write_tree_diff(
        outstream, repo.object_store, parent_commit.tree, commit.tree)


def show_tree(repo, tree, decode, outstream=sys.stdout):
    """Print a tree to a stream.

    :param repo: A `Repo` object
    :param tree: A `Tree` object
    :param decode: Function for decoding bytes to unicode string
    :param outstream: Stream to write to
    """
    for n in tree:
        outstream.write(decode(n) + "\n")


def show_tag(repo, tag, decode, outstream=sys.stdout):
    """Print a tag to a stream.

    :param repo: A `Repo` object
    :param tag: A `Tag` object
    :param decode: Function for decoding bytes to unicode string
    :param outstream: Stream to write to
    """
    print_tag(tag, decode, outstream)
    show_object(repo, repo[tag.object[1]], outstream)


def show_object(repo, obj, decode, outstream):
    return {
        b"tree": show_tree,
        b"blob": show_blob,
        b"commit": show_commit,
        b"tag": show_tag,
            }[obj.type_name](repo, obj, decode, outstream)


def print_name_status(changes):
    """Print a simple status summary, listing changed files.
    """
    for change in changes:
        if not change:
            continue
        if isinstance(change, list):
            change = change[0]
        if change.type == CHANGE_ADD:
            path1 = change.new.path
            path2 = ''
            kind = 'A'
        elif change.type == CHANGE_DELETE:
            path1 = change.old.path
            path2 = ''
            kind = 'D'
        elif change.type == CHANGE_MODIFY:
            path1 = change.new.path
            path2 = ''
            kind = 'M'
        elif change.type in RENAME_CHANGE_TYPES:
            path1 = change.old.path
            path2 = change.new.path
            if change.type == CHANGE_RENAME:
                kind = 'R'
            elif change.type == CHANGE_COPY:
                kind = 'C'
        yield '%-8s%-20s%-20s' % (kind, path1, path2)


def log(repo=".", paths=None, outstream=sys.stdout, max_entries=None,
        reverse=False, name_status=False):
    """Write commit logs.

    :param repo: Path to repository
    :param paths: Optional set of specific paths to print entries for
    :param outstream: Stream to write log output to
    :param reverse: Reverse order in which entries are printed
    :param name_status: Print name status
    :param max_entries: Optional maximum number of entries to display
    """
    with open_repo_closing(repo) as r:
        walker = r.get_walker(
            max_entries=max_entries, paths=paths, reverse=reverse)
        for entry in walker:
            def decode(x):
                return commit_decode(entry.commit, x)
            print_commit(entry.commit, decode, outstream)
            if name_status:
                outstream.writelines(
                    [l+'\n' for l in print_name_status(entry.changes())])


# TODO(jelmer): better default for encoding?
def show(repo=".", objects=None, outstream=sys.stdout,
         default_encoding=DEFAULT_ENCODING):
    """Print the changes in a commit.

    :param repo: Path to repository
    :param objects: Objects to show (defaults to [HEAD])
    :param outstream: Stream to write to
    :param default_encoding: Default encoding to use if none is set in the
        commit
    """
    if objects is None:
        objects = ["HEAD"]
    if not isinstance(objects, list):
        objects = [objects]
    with open_repo_closing(repo) as r:
        for objectish in objects:
            o = parse_object(r, objectish)
            if isinstance(o, Commit):
                def decode(x):
                    return commit_decode(o, x, default_encoding)
            else:
                def decode(x):
                    return x.decode(default_encoding)
            show_object(r, o, decode, outstream)


def diff_tree(repo, old_tree, new_tree, outstream=sys.stdout):
    """Compares the content and mode of blobs found via two tree objects.

    :param repo: Path to repository
    :param old_tree: Id of old tree
    :param new_tree: Id of new tree
    :param outstream: Stream to write to
    """
    with open_repo_closing(repo) as r:
        write_tree_diff(outstream, r.object_store, old_tree, new_tree)


def make_bytes(c):
    if not isinstance(c, bytes):
        return c.encode(DEFAULT_ENCODING)

    return c


def rev_list(repo, commits, outstream=sys.stdout, data_path=None):
    """Lists commit objects in reverse chronological order.

    :param repo: Path to repository
    :param commits: Commits over which to iterate
    :param outstream: Stream to write to
    """

    if not isinstance(commits, list):
        commits = [commits]

    with open_repo_closing(repo, data_path) as r:
        for entry in r.get_walker(include=[r[make_bytes(c)].id for c in commits]):
            outstream.write(str(entry.commit.id + b"\n"))


def tag(*args, **kwargs):
    import warnings
    warnings.warn("tag has been deprecated in favour of tag_create.",
                  DeprecationWarning)
    return tag_create(*args, **kwargs)


def tag_create(
        repo, tag, author=None, message=None, annotated=False,
        objectish="HEAD", tag_time=None, tag_timezone=None):
    """Creates a tag in git via dulwich calls:

    :param repo: Path to repository
    :param tag: tag string
    :param author: tag author (optional, if annotated is set)
    :param message: tag message (optional)
    :param annotated: whether to create an annotated tag
    :param objectish: object the tag should point at, defaults to HEAD
    :param tag_time: Optional time for annotated tag
    :param tag_timezone: Optional timezone for annotated tag
    """

    with open_repo_closing(repo) as r:
        object = parse_object(r, objectish)

        if annotated:
            # Create the tag object
            tag_obj = Tag()
            if author is None:
                # TODO(jelmer): Don't use repo private method.
                author = r._get_user_identity()
            tag_obj.tagger = author
            tag_obj.message = message
            tag_obj.name = tag
            tag_obj.object = (type(object), object.id)
            if tag_time is None:
                tag_time = int(time.time())
            tag_obj.tag_time = tag_time
            if tag_timezone is None:
                # TODO(jelmer) Use current user timezone rather than UTC
                tag_timezone = 0
            elif isinstance(tag_timezone, str):
                tag_timezone = parse_timezone(tag_timezone)
            tag_obj.tag_timezone = tag_timezone
            r.object_store.add_object(tag_obj)
            tag_id = tag_obj.id
        else:
            tag_id = object.id

        r.refs[b'refs/tags/' + tag] = tag_id


def list_tags(*args, **kwargs):
    import warnings
    warnings.warn("list_tags has been deprecated in favour of tag_list.",
                  DeprecationWarning)
    return tag_list(*args, **kwargs)


def tag_list(repo, outstream=sys.stdout):
    """List all tags.

    :param repo: Path to repository
    :param outstream: Stream to write tags to
    """
    with open_repo_closing(repo) as r:
        tags = sorted(r.refs.as_dict(b"refs/tags"))
        return tags


def tag_delete(repo, name):
    """Remove a tag.

    :param repo: Path to repository
    :param name: Name of tag to remove
    """
    with open_repo_closing(repo) as r:
        if isinstance(name, bytes):
            names = [name]
        elif isinstance(name, list):
            names = name
        else:
            raise TypeError("Unexpected tag name type %r" % name)
        for name in names:
            del r.refs[b"refs/tags/" + name]


def reset(repo, mode, committish="HEAD"):
    """Reset current HEAD to the specified state.

    :param repo: Path to repository
    :param mode: Mode ("hard", "soft", "mixed")
    """

    if mode != "hard":
        raise ValueError("hard is the only mode currently supported")

    with open_repo_closing(repo) as r:
        tree = r[committish].tree
        r.reset_index(tree)


def pull(repo, remote_location=None, refspecs=None,
         outstream=default_bytes_out_stream,
         errstream=default_bytes_err_stream):
    """Pull from remote via dulwich.client

    :param repo: Path to repository
    :param remote_location: Location of the remote
    :param refspec: refspecs to fetch
    :param outstream: A stream file to write to output
    :param errstream: A stream file to write to errors
    """
    # Open the repo
    with open_repo_closing(repo) as r:
        if remote_location is None:
            # TODO(jelmer): Lookup 'remote' for current branch in config
            raise NotImplementedError(
                "looking up remote from branch config not supported yet")
        if refspecs is None:
            refspecs = [b"HEAD"]
        selected_refs = []

        def determine_wants(remote_refs):
            selected_refs.extend(
                parse_reftuples(remote_refs, r.refs, refspecs))
            return [remote_refs[lh] for (lh, rh, force) in selected_refs]
        client, path = get_transport_and_path(remote_location)
        remote_refs = client.fetch(
            path, r, progress=errstream.write, determine_wants=determine_wants)
        for (lh, rh, force) in selected_refs:
            r.refs[rh] = remote_refs[lh]
        if selected_refs:
            r[b'HEAD'] = remote_refs[selected_refs[0][1]]

        # Perform 'git checkout .' - syncs staged changes
        tree = r[b"HEAD"].tree
        r.reset_index(tree=tree)


def status(repo=".", ignored=False):
    """Returns staged, unstaged, and untracked changes relative to the HEAD.

    :param repo: Path to repository or repository object
    :param ignored: Whether to include ignoed files in `untracked`
    :return: GitStatus tuple,
        staged -    list of staged paths (diff index/HEAD)
        unstaged -  list of unstaged paths (diff index/working-tree)
        untracked - list of untracked, un-ignored & non-.git paths
    """
    with open_repo_closing(repo) as r:
        # 1. Get status of staged
        tracked_changes = get_tree_changes(r)
        # 2. Get status of unstaged
        index = r.open_index()
        unstaged_changes = list(get_unstaged_changes(index, r.path))
        ignore_manager = IgnoreFilterManager.from_repo(r)
        untracked_paths = get_untracked_paths(r.path, r.path, index)
        if ignored:
            untracked_changes = list(untracked_paths)
        else:
            untracked_changes = [
                    p for p in untracked_paths
                    if not ignore_manager.is_ignored(p)]
        return GitStatus(tracked_changes, unstaged_changes, untracked_changes)


def get_untracked_paths(frompath, basepath, index):
    """Get untracked paths.

    ;param frompath: Path to walk
    :param basepath: Path to compare to
    :param index: Index to check against
    """
    # If nothing is specified, add all non-ignored files.
    for dirpath, dirnames, filenames in os.walk(frompath):
        # Skip .git and below.
        if '.git' in dirnames:
            dirnames.remove('.git')
            if dirpath != basepath:
                continue
        if '.git' in filenames:
            filenames.remove('.git')
            if dirpath != basepath:
                continue
        for filename in filenames:
            ap = os.path.join(dirpath, filename)
            ip = path_to_tree_path(basepath, ap)
            if ip not in index:
                yield os.path.relpath(ap, frompath)


def get_tree_changes(repo):
    """Return add/delete/modify changes to tree by comparing index to HEAD.

    :param repo: repo path or object
    :return: dict with lists for each type of change
    """
    with open_repo_closing(repo) as r:
        index = r.open_index()

        # Compares the Index to the HEAD & determines changes
        # Iterate through the changes and report add/delete/modify
        # TODO: call out to dulwich.diff_tree somehow.
        tracked_changes = {
            'add': [],
            'delete': [],
            'modify': [],
        }
        try:
            tree_id = r[b'HEAD'].tree
        except KeyError:
            tree_id = None

        for change in index.changes_from_tree(r.object_store, tree_id):
            if not change[0][0]:
                tracked_changes['add'].append(change[0][1])
            elif not change[0][1]:
                tracked_changes['delete'].append(change[0][0])
            elif change[0][0] == change[0][1]:
                tracked_changes['modify'].append(change[0][0])
            else:
                raise AssertionError('git mv ops not yet supported')
        return tracked_changes


def daemon(path=".", address=None, port=None):
    """Run a daemon serving Git requests over TCP/IP.

    :param path: Path to the directory to serve.
    :param address: Optional address to listen on (defaults to ::)
    :param port: Optional port to listen on (defaults to TCP_GIT_PORT)
    """
    # TODO(jelmer): Support git-daemon-export-ok and --export-all.
    backend = FileSystemBackend(path)
    server = TCPGitServer(backend, address, port)
    server.serve_forever()


def web_daemon(path=".", address=None, port=None):
    """Run a daemon serving Git requests over HTTP.

    :param path: Path to the directory to serve
    :param address: Optional address to listen on (defaults to ::)
    :param port: Optional port to listen on (defaults to 80)
    """
    from .web import (
        make_wsgi_chain,
        make_server,
        WSGIRequestHandlerLogger,
        WSGIServerLogger)

    backend = FileSystemBackend(path)
    app = make_wsgi_chain(backend)
    server = make_server(address, port, app,
                         handler_class=WSGIRequestHandlerLogger,
                         server_class=WSGIServerLogger)
    server.serve_forever()


def upload_pack(path=".", inf=None, outf=None):
    """Upload a pack file after negotiating its contents using smart protocol.

    :param path: Path to the repository
    :param inf: Input stream to communicate with client
    :param outf: Output stream to communicate with client
    """
    if outf is None:
        outf = getattr(sys.stdout, 'buffer', sys.stdout)
    if inf is None:
        inf = getattr(sys.stdin, 'buffer', sys.stdin)
    path = os.path.expanduser(path)
    backend = FileSystemBackend(path)

    def send_fn(data):
        outf.write(data)
        outf.flush()
    proto = Protocol(inf.read, send_fn)
    handler = UploadPackHandler(backend, [path], proto)
    # FIXME: Catch exceptions and write a single-line summary to outf.
    handler.handle()
    return 0


def receive_pack(path=".", inf=None, outf=None):
    """Receive a pack file after negotiating its contents using smart protocol.

    :param path: Path to the repository
    :param inf: Input stream to communicate with client
    :param outf: Output stream to communicate with client
    """
    if outf is None:
        outf = getattr(sys.stdout, 'buffer', sys.stdout)
    if inf is None:
        inf = getattr(sys.stdin, 'buffer', sys.stdin)
    path = os.path.expanduser(path)
    backend = FileSystemBackend(path)

    def send_fn(data):
        outf.write(data)
        outf.flush()
    proto = Protocol(inf.read, send_fn)
    handler = ReceivePackHandler(backend, [path], proto)
    # FIXME: Catch exceptions and write a single-line summary to outf.
    handler.handle()
    return 0


def branch_delete(repo, name):
    """Delete a branch.

    :param repo: Path to the repository
    :param name: Name of the branch
    """
    with open_repo_closing(repo) as r:
        if isinstance(name, bytes):
            names = [name]
        elif isinstance(name, list):
            names = name
        else:
            raise TypeError("Unexpected branch name type %r" % name)
        for name in names:
            del r.refs[b"refs/heads/" + name]


def branch_create(repo, name, objectish=None, force=False):
    """Create a branch.

    :param repo: Path to the repository
    :param name: Name of the new branch
    :param objectish: Target object to point new branch at (defaults to HEAD)
    :param force: Force creation of branch, even if it already exists
    """
    with open_repo_closing(repo) as r:
        if objectish is None:
            objectish = "HEAD"
        object = parse_object(r, objectish)
        refname = b"refs/heads/" + name
        if refname in r.refs and not force:
            raise KeyError("Branch with name %s already exists." % name)
        r.refs[refname] = object.id


def branch_list(repo):
    """List all branches.

    :param repo: Path to the repository
    """
    with open_repo_closing(repo) as r:
        return r.refs.keys(base=b"refs/heads/")


def fetch(repo, remote_location, outstream=sys.stdout,
          errstream=default_bytes_err_stream):
    """Fetch objects from a remote server.

    :param repo: Path to the repository
    :param remote_location: String identifying a remote server
    :param outstream: Output stream (defaults to stdout)
    :param errstream: Error stream (defaults to stderr)
    :return: Dictionary with refs on the remote
    """
    with open_repo_closing(repo) as r:
        client, path = get_transport_and_path(remote_location)
        remote_refs = client.fetch(path, r, progress=errstream.write)
    return remote_refs


def ls_remote(remote):
    """List the refs in a remote.

    :param remote: Remote repository location
    :return: Dictionary with remote refs
    """
    client, host_path = get_transport_and_path(remote)
    return client.get_refs(host_path)


def pack_objects(repo, object_ids, packf, idxf, delta_window_size=None):
    """Pack objects into a file.

    :param repo: Path to the repository
    :param object_ids: List of object ids to write
    :param packf: File-like object to write to
    :param idxf: File-like object to write to (can be None)
    """
    with open_repo_closing(repo) as r:
        entries, data_sum = write_pack_objects(
            packf,
            r.object_store.iter_shas((oid, None) for oid in object_ids),
            delta_window_size=delta_window_size)
    if idxf is not None:
        entries = sorted([(k, v[0], v[1]) for (k, v) in entries.items()])
        write_pack_index(idxf, entries, data_sum)


def ls_tree(repo, tree_ish=None, outstream=sys.stdout, recursive=False,
            name_only=False, data_path=None):
    """List contents of a tree.

    :param repo: Path to the repository
    :param tree_ish: Tree id to list
    :param outstream: Output stream (defaults to stdout)
    :param recursive: Whether to recursively list files
    :param name_only: Only print item name
    """
    def list_tree(store, treeid, base):
        for (name, mode, sha) in store[treeid].iteritems():
            if base:
                name = posixpath.join(base, name)
            if name_only:
                outstream.write(name + b"\n")
            else:
                outstream.write(pretty_format_tree_entry(name, mode, sha))
            if stat.S_ISDIR(mode):
                list_tree(store, sha, name)
    if tree_ish is None:
        tree_ish = "HEAD"

    if not isinstance(tree_ish, bytes):
        tree_ish = tree_ish.encode(DEFAULT_ENCODING)

    with open_repo_closing(repo, data_path=data_path) as r:
        c = r[tree_ish]
        treeid = c.tree
        list_tree(r.object_store, treeid, "")


def remote_add(repo, name, url):
    """Add a remote.

    :param repo: Path to the repository
    :param name: Remote name
    :param url: Remote URL
    """
    if not isinstance(name, bytes):
        name = name.encode(DEFAULT_ENCODING)
    if not isinstance(url, bytes):
        url = url.encode(DEFAULT_ENCODING)
    with open_repo_closing(repo) as r:
        c = r.get_config()
        section = (b'remote', name)
        if c.has_section(section):
            raise RemoteExists(section)
        c.set(section, b"url", url)
        c.write_to_path()


def check_ignore(repo, paths, no_index=False):
    """Debug gitignore files.

    :param repo: Path to the repository
    :param paths: List of paths to check for
    :param no_index: Don't check index
    :return: List of ignored files
    """
    with open_repo_closing(repo) as r:
        index = r.open_index()
        ignore_manager = IgnoreFilterManager.from_repo(r)
        for path in paths:
            if os.path.isdir(path):
                continue
            if os.path.isabs(path):
                path = os.path.relpath(path, r.path)
            if not no_index and path_to_tree_path(r.path, path) in index:
                continue
            if ignore_manager.is_ignored(path):
                yield path
