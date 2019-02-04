import click
from tqdm import tqdm
from pcloud import PyCloud
from pathlib import Path
import sys
import logging
import configparser
import pydoc
import datetime

__version__ = '0.7'

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

ROOT = Path('/')


def get_config():

    pth = Path.home() / '.config/pclean.ini'

    if not pth.exists():
        raise FileNotFoundError()

    cp = configparser.ConfigParser()
    cp.read(pth)

    try:
        user = cp['account']['user']
        pwd = cp['account']['password']
    except KeyError:
        raise

    return user, pwd


def to_dt(s):

    return datetime.datetime.strptime(s, '%a, %d %b %Y %H:%M:%S %z')


def lsr(pc, path, extensions=()):
    """
    Retrieves the pCloud filesystem under a given path
    saving all the metadata
    """

    if path is None:
        path = ROOT

    ds = pc.listfolder(path=path, recursive=True)

    if ds['result'] == 2005:
        raise FileNotFoundError()
    ds['metadata']['full_path'] = path

    folds = [(path, ds['metadata'])]

    while len(folds) > 0:
        cpath, fold = folds.pop(0)

        for f in fold['contents']:
            f['full_path'] = cpath / f['name']
            f['created_dt'] = to_dt(f['created'])
            f['modified_dt'] = to_dt(f['modified'])
            if f['isfolder']:
                folds.append((f['full_path'], f))
            elif len(extensions) > 0 and \
                 f['full_path'].suffix not in extensions:
                f['filter'] = True

        if len(extensions) > 0:
            fold['contents'] = [x for x in fold['contents'] if not x.get('filter', False)]

    return ds['metadata']


def hashes(ds):
    """
    Creates a map of hashes to files and folders.
    """

    folds = [ds]
    hashes = {}
    fmap = {'files': {}, 'folders': {ds['folderid']: ds}}

    while len(folds) > 0:
        fold = folds.pop(0)

        for f in fold['contents']:
            if f['isfolder']:
                fmap['folders'][f['folderid']] = f
                folds.append(f)
            elif 'hash' in f:
                fmap['files'][f['fileid']] = f
                if f['hash'] not in hashes:
                    hashes[f['hash']] = []
                hashes[f['hash']].append(f)

    return hashes, fmap


def isempty(fold):
    """
    Determines if a folder is empty by checking
    the to_delete flag on each file recursing
    through subdirectories

    Returns a list of file ids and folder ids for
    all "deleted" items or None
    """

    file_ids = set()
    folder_ids = set()

    for f in fold:
        if f['isfolder']:
            r = isempty(f['contents'])
            if r is None:
                return None

            folder_ids.add(f['folderid'])
            folder_ids.update(r[0])  # Subdirectories that are empty
            file_ids.update(r[1])    # Files that have been deleted
        else:
            if 'to_delete' not in f:
                return None

            file_ids.add(f['fileid'])

    return folder_ids, file_ids


def optimise(ds, fmap, fids):
    """
    Optimises the deletion process by identifying
    where a recursive delete can be used as opposed
    to deleting each file individually
    """

    file_map = fmap['files']
    fold_map = fmap['folders']

    folders = set()
    for fid in fids:
        file_map[fid]['to_delete'] = True
        folders.add(file_map[fid]['parentfolderid'])

    to_delete = fids.copy()
    empty_fold = set()  # Folders that we have marked as empty

    while len(folders) > 0:
        fold_id = folders.pop()
        empty = isempty(fold_map[fold_id]['contents'])
        if empty is not None:
            empty_fold.difference_update(empty[0])
            folders.difference_update(empty[0])
            to_delete.difference_update(empty[1])
            empty_fold.add(fold_id)

    return empty_fold, to_delete


def delete(pc, fold_del, file_del):

    for fid in tqdm(fold_del, 'deleting folders'):
        pc.deletefolderrecursive(folderid=fid)

    for fid in tqdm(file_del, 'deleting files'):
        pc.deletefile(fileid=fid)


def empty_hash(hashes):
    """
    Determines the hash of an empty file. We do
    this just to be sure that, should they change
    the hashing mechanism, we continue to work.
    """

    for h, groups in hashes.items():
        if groups[0]['size'] == 0:
            return h

    return None


def prune_path(ds, pth):
    """
    Removes a path from a directory
    structure returned by lsr
    """

    logging.debug('pruning %s from structure', pth)

    new_cwd = ds

    for part in pth.parts[1:]:
        cwd = new_cwd
        for i, f in enumerate(cwd.get('contents', [])):
            if f['name'] == part:
                new_cwd = f
                break
        if new_cwd is None:
            break

    if new_cwd is not None:
        log.debug('removing %s', cwd['name'])
        del cwd['contents'][i]


@click.command()
@click.argument('user')
@click.argument('password')
def auth(user, password):
    """
    Saves the pCloud login credentials
    """

    pth = Path.home() / '.config/pclean.ini'

    cp = configparser.ConfigParser()
    cp['account'] = {
        'user': user,
        'password': password
    }

    with open(pth, 'w+') as f:
        cp.write(f)

    return cp


@click.command()
@click.argument('source')
@click.argument('search', required=False)
@click.option('-n', '--no-action', is_flag=True, help='Dry run')
@click.option('-v', is_flag=True, help='Enable logging')
@click.option('-vv', is_flag=True, help='More verbose logging')
@click.option('--empty', is_flag=True,
              help='Delete empty files, files with size 0')
@click.option('--ignore-name', is_flag=True,
              help='Delete files even if their names don\'t match')
@click.option('-s', '--same', is_flag=True,
              help='Delete duplicates within the same directory')
@click.option('-m', '--modified', is_flag=True,
              help='Sort by modification time instead of creation time')
@click.option('-d', '--descending', is_flag=True,
              help='Sort in descending time order')
@click.option('-e', '--extensions', multiple=True,
              help='Only search for duplicates with the given file extensions.')
def clean(source, search, no_action, v, vv, empty,
          ignore_name, same, modified, descending, extensions):
    """
    Searches and deletes duplicate files within a pCloud account.

    pClean has several modes of operation:

    * If just a source path is specified, any duplicates files that
      are not under the source path are deleted.

    * If just a source path is specified with the --same flag, any
      duplicate files under the source path are sorted by their
      creation date and all but the oldest file is deleted.
      If --modified is specified then the modification time is used
      for sorting.
      If --descending is specified then all but the newest
      filed is deleted

    * If a source and search path are specified, any duplicate files
      that are found under the search path are deleted.
    """

    try:
        user, pwd = get_config()
    except (FileNotFoundError, KeyError):
        print('use auth to set your username and password')
        sys.exit(1)

    if vv:
        logging.basicConfig(level=logging.DEBUG)
    elif v:
        logging.basicConfig(level=logging.INFO)

    if same and search is not None:
        print('--same cannot be used in conjunction with a search path')
        sys.exit(1)

    source_pth = Path(source)
    search_pth = Path(search) if search is not None else ROOT

    if not (source_pth.is_absolute() and search_pth.is_absolute()):
        print('paths must be absolute')
        sys.exit(1)

    exts = []
    for x in extensions:
        if x.startswith('.'):
            exts.append(x)
        else:
            exts.append(f'.{x}')

    pc = PyCloud(user, pwd)

    try:
        source_files = lsr(pc, source_pth, exts)
    except FileNotFoundError:
        print(f"file not found: {source_pth}")
        sys.exit(1)
    source_hmap, source_fmap = hashes(source_files)

    if not empty:
        # If the empty flag isn't set then we remove
        # any hashes for empty files so they don't
        # match the search set
        eh = empty_hash(source_hmap)
        if eh is not None:
            log.debug('empty file hash: %s', eh)
            del(source_hmap[eh])

    if same:
        skey = 'modified_dt' if modified else 'created_dt'

        fids = set()
        # We're searching for files in the source directory
        for h, files in source_hmap.items():
            if len(files) <= 2:
                continue

            try:
                slist = sorted(files, key=lambda x: x[skey], reverse=descending)
            except:
                import pprint
                pprint.pprint(files)
                raise

            if ignore_name:
                fids.update(set([x['fileid'] for x in slist[1:]]))
            else:
                fname = slist[0]['name']
                fids.update(set([x['fileid'] for x in slist[1:] if x['name'] == fname]))

        if no_action:
            dlist = [str(source_fmap['files'][fid]['full_path']) for fid in fids]
            pydoc.pager('Files to delete\n    {}'.format("\n    ".join(dlist)))

        else:
            delete(pc, [], fids)

        sys.exit(0)

    try:
        search_files = lsr(pc, search_pth, exts)
    except FileNotFoundError:
        print(f"file not found: {search_pth}")
        sys.exit(1)

    # Prune out the source path so the there's
    # no intersection of trees
    prune_path(search_files, source_pth)

    search_hmap, search_fmap = hashes(search_files)

    source_fold_id = source_files['folderid']
    search_fold_id = search_files['folderid']

    if source_fold_id == search_fold_id or \
       source_fold_id in search_fmap['folders'] or \
       search_fold_id in source_fmap['folders']:
        logging.info('source_fold_id: %s, search_fold_id: %s, source folder '
                     'in search folders: %s, search folder in source folders: %s',
                     source_fold_id, search_fold_id,
                     source_fold_id in search_fmap['folders'],
                     search_fold_id in source_fmap['folders'])
        print('paths cannot overlap')
        sys.exit(1)

    matches = set(source_hmap.keys()).intersection(set(search_hmap.keys()))

    fids = set()
    if ignore_name:
        logging.info('deleting files with matching content')
        for match in matches:
            fids.update(set([x['fileid'] for x in search_hmap[match]]))
    else:
        logging.info('deleting files with matching names and content')
        for match in matches:
            source_names = [x['name'] for x in source_hmap[match]]
            for x in search_hmap[match]:
                if x['name'] in source_names:
                    fids.add(x['fileid'])

    fold_del, file_del = optimise(search_files, search_fmap, fids)

    if no_action:
        flist = [
            str(search_fmap['folders'][fid]['full_path']) for fid in fold_del
        ]
        dlist = [
            str(search_fmap['files'][fid]['full_path']) for fid in file_del
        ]

        msg = []
        if len(flist) > 0:
            msg.append('Directories to delete')
            msg.append("\n    ".join(flist))
        if len(dlist) > 0:
            msg.append('Files to delete')
            msg.append("\n    ".join(dlist))

        out = '\n'.join(msg)

        if sys.stdout.isatty():
            pydoc.pager(out)
        else:
            print(out)
    else:
        delete(pc, fold_del, file_del)


@click.group(invoke_without_command=True)
@click.pass_context
@click.option('-v', '--version', is_flag=True, help='Display version and exit')
def cli(ctx, version):
    if ctx.invoked_subcommand is None:
        if version:
            print(f'pclean version {__version__}')
            sys.exit(0)


cli.add_command(auth)
cli.add_command(clean)


if __name__ == '__main__':

    cli()
