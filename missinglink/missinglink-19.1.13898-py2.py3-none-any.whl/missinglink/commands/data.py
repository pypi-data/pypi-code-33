# -*- coding: utf8 -*-
import os
from contextlib import closing
from uuid import uuid4

import click
import sys

import humanize

from missinglink.core.api import ApiCaller
from missinglink.core.avro_utils import AvroWriter

from missinglink.legit.data_sync import DataSync, InvalidJsonFile, status_with_timing
from missinglink.legit import MetadataOperationError
from missinglink.legit.metadata_files import MetadataFiles
from tqdm import tqdm
from missinglink.commands.commons import add_to_data_if_not_none, output_result
from missinglink.legit.data_volume import create_data_volume, with_repo, default_data_volume_path, with_repo_dynamic, \
    map_volume
from missinglink.legit.path_utils import expend_and_validate_path, safe_make_dirs, safe_rm_tree, \
    DestPathEnum, has_moniker, bucket_print_name, enumerate_paths_with_info, AccessDenied, enumerate_paths
import json

from missinglink.commands.utilities.options import CommonOptions, DataVolumeOptions


@click.group('data')
def data_commands():
    pass


def __expend_and_validate_path(path, expand_vars=True, validate_path=True, abs_path=True):
    try:
        return expend_and_validate_path(path, expand_vars, validate_path, abs_path)
    except (IOError, OSError):
        click.echo('Folder not found %s' % path, err=True)
        sys.exit(1)


@data_commands.command('map')
@DataVolumeOptions.data_volume_id_argument()
@DataVolumeOptions.data_path_option()
@click.pass_context
def _cmd_add_data_path(ctx, volume_id, data_path):
    config = map_volume(ctx, volume_id, data_path)

    display_name = config.general_config.get('display_name', 'No display name provided')
    click.echo('Initialized data volume %s (%s)' % (config.volume_id, display_name))


@data_commands.command('create')
@CommonOptions.display_name_option()
@CommonOptions.description_option()
@CommonOptions.org_option()
@DataVolumeOptions.data_path_option(required=False)
@click.option('--bucket')
@click.option('--linked/--embedded', is_flag=True, default=False)
@click.pass_context
def _cmd_create_data_volume(ctx, display_name, description, org, data_path, bucket, linked):
    data = {}

    add_to_data_if_not_none(data, display_name, "display_name")
    add_to_data_if_not_none(data, org, "org")
    add_to_data_if_not_none(data, description, "description")
    add_to_data_if_not_none(data, not linked, "embedded")

    expiration = ctx.obj.config.readonly_items('data_volumes').get('expiration')
    if expiration:
        data['expiration'] = expiration

    if bucket is not None:
        data['bucket'] = bucket

    result = ApiCaller.call(ctx.obj, ctx.obj.session, 'post', 'data_volumes', data)

    data_volume_id = result['id']

    data_path = __expend_and_validate_path(data_path)

    params = {}
    if bucket:
        params['object_store'] = {'bucket_name': bucket}

    create_data_volume(data_volume_id, data_path, linked, display_name, description, **params)

    output_result(ctx, result)


@data_commands.command('config')
@DataVolumeOptions.data_volume_id_argument()
@click.option('--edit', is_flag=True)
def edit_config_file(volume_id, edit):
    path = os.path.join(default_data_volume_path(volume_id), 'config')

    if edit:
        os.system('open -a TextEdit %s' % path)
        return

    with open(path) as f:
        click.echo(f.read())


@data_commands.command('commit')
@DataVolumeOptions.data_volume_id_argument()
@click.option('--message', '-m', required=False)
@DataVolumeOptions.isolation_token_option()
@click.pass_context
def commit_data_volume(ctx, volume_id, message, isolation_token):
    with with_repo_dynamic(ctx, volume_id) as repo:
        result = repo.commit(message, isolation_token) or {}

        if 'commit_id' not in result:
            click.echo('no changeset detected', err=True)

        output_result(ctx, result)


def process_moniker_data_path(data_path):
    from six.moves.urllib.parse import urlparse, urlunparse

    if not has_moniker(data_path):
        return data_path

    parts = urlparse(data_path)

    return urlunparse((parts.scheme, parts.netloc, '', '', '', ''))


def __print_transfer_info(repo):
    embedded = repo.data_volume_config.object_store_config.get('embedded')

    if embedded:
        bucket_name = repo.data_volume_config.object_store_config.get('bucket_name')

        if bucket_name:
            click.echo('Transfer files from %s to %s' % (bucket_print_name(repo.data_path), bucket_print_name(bucket_name)), err=True)
        else:
            click.echo('Transfer files from %s to MissingLink secure bucket' % (bucket_print_name(repo.data_path),), err=True)
    else:
        click.echo('Indexing files from %s' % (bucket_print_name(repo.data_path)), err=True)


@data_commands.command('set-metadata')
@DataVolumeOptions.data_path_option()
@click.option('--append/--replace', default=False, help='In case metadata data with the same key already exists, `--append` will not replace it, and `--replace` will. Defaults to `--replace`')
@click.option('--metadata-string', '-ms', multiple=True, type=(str, str), help='string metadata(s) to update. you can provide multiple values in the key value format.')
@click.option('--metadata-num', '-mm', multiple=True, type=(str, int), help='integer metadata(s) to update. you can provide multiple values in key value format.')
@click.option('--metadata-float', '-mf', multiple=True, type=(str, float), help='float metadata(s) to update. you can provide multiple values in key value format.')
@click.option('--metadata-boolean', '-mb', multiple=True, type=(str, bool), help='boolean metadata(s) to update. you can provide multiple values in key value format.')
@click.pass_context
def set_metadata(ctx, data_path, append, metadata_num, metadata_float, metadata_boolean, metadata_string):
    new_values_dict = {}
    for key, value in metadata_num:
        new_values_dict[key] = value
    for key, value in metadata_float:
        new_values_dict[key] = value
    for key, value in metadata_boolean:
        new_values_dict[key] = value
    for key, value in metadata_string:
        new_values_dict[key] = value

    def get_current_metadata(file_path):
        if os.path.isfile(file_path + '.metadata.json'):
            try:
                with open(file_path + '.metadata.json') as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def save_meta(file_path, metadata):
        with open(file_path + '.metadata.json', 'w') as f:
            return json.dump(metadata, f)

    for root, subdirs, files in os.walk(data_path):
        for filename in files:
            if filename.endswith('.metadata.json'):
                continue
            file_path = os.path.join(root, filename)
            cur_meta = get_current_metadata(file_path)
            new_meta = {}
            if append:
                new_meta.update(new_values_dict)
                new_meta.update(cur_meta)
            else:
                new_meta.update(cur_meta)
                new_meta.update(new_values_dict)
            save_meta(file_path, new_meta)
            print('%s meta saved' % file_path)


@data_commands.command('sync')
@DataVolumeOptions.data_volume_id_argument()
@DataVolumeOptions.data_path_option()
@click.option('--commit', required=False)
@CommonOptions.processes_option()
@CommonOptions.no_progressbar_option()
@click.option('--resume', required=False)
@click.option('--isolated', is_flag=True, default=False, required=False)
@click.pass_context
def sync_to_data_volume(ctx, volume_id, data_path, commit, processes, no_progressbar, resume, isolated):
    data_path = __expend_and_validate_path(data_path, expand_vars=False)

    repo_data_path = process_moniker_data_path(data_path)

    def add_resume_token_to_user_agent():
        user_agent = ctx.obj.session.headers.get('User-Agent')
        user_agent += 'sync/%s' % data_sync.resume_token

        ctx.obj.session.headers['User-Agent'] = user_agent

    with with_repo_dynamic(ctx, volume_id, repo_data_path) as repo:
        __repo_validate_data_path(repo, volume_id)

        data_sync = DataSync(ctx, repo, no_progressbar, resume_token=resume, processes=processes)

        add_resume_token_to_user_agent()

        isolation_token = uuid4().hex if isolated else None

        try:
            files_to_upload, same_files_count = data_sync.upload_index_and_metadata(data_path, isolation_token)
        except InvalidJsonFile as ex:
            click.echo('Invalid json file %s (%s)' % (ex.filename, ex.ex), err=True)
            sys.exit(1)
        except AccessDenied as ex:
            click.echo(str(ex))
            sys.exit(1)

        def create_update_progress(progress_bar):
            def update(upload_request):
                progress_bar.update(upload_request.size)

                progress_ctx['total_upload'] += 1

                progress_bar.set_postfix_str(
                    '%s/%s' % (humanize.intcomma(progress_ctx['total_upload']), humanize.intcomma(total_files_with_same)))

            return update

        if files_to_upload is not None:
            total_files_to_upload = len(files_to_upload)
            total_files_with_same = total_files_to_upload + same_files_count
            progress_ctx = {'total_upload': same_files_count}
            total_files_to_upload_size = sum([file_info['size'] for file_info in files_to_upload])
            if total_files_to_upload > 0:
                __print_transfer_info(repo)

                with tqdm(total=total_files_to_upload_size, desc='Syncing files', unit_scale=True, unit='B', ncols=80, disable=no_progressbar) as bar:
                    callback = create_update_progress(bar)
                    data_sync.upload_in_batches(files_to_upload, callback=callback, isolation_token=isolation_token)
            else:
                click.echo('No change detected, nothing to upload (metadata only change).', err=True)

        def do_commit():
            return repo.commit(commit, isolation_token)

        commit_results = {}
        if commit is not None:
            commit_results = status_with_timing('Server process metadata', do_commit)

        results = {}

        if commit_results:
            results.update(commit_results)

        if isolation_token is not None:
            results["isolationToken"] = isolation_token

        output_result(ctx, results)


@data_commands.command('add')
@DataVolumeOptions.data_volume_id_argument()
@click.option('--files', '-f', multiple=True)
@click.option('--commit', required=False)
@CommonOptions.processes_option()
@CommonOptions.no_progressbar_option()
@click.pass_context
def add_to_data_volume(ctx, volume_id, files, commit, processes, no_progressbar):
    all_files = list(enumerate_paths_with_info(files))
    total_files = len(all_files)

    def do_commit():
        return repo.commit(commit)

    def create_bar():
        return tqdm(total=total_files, desc="Adding files", unit=' files', ncols=80, disable=no_progressbar)

    def create_repo():
        return with_repo(ctx.obj.config, volume_id, session=ctx.obj.session)

    with create_bar() as bar, create_repo() as repo:
        data_sync = DataSync(ctx, repo, no_progressbar)
        if processes != -1:
            repo.data_volume_config.object_store_config['processes'] = processes

        data_sync.upload_in_batches(all_files, total_files, callback=lambda x: bar.update())

        commit_results = {}
        if commit is not None:
            commit_results = status_with_timing('Commit', do_commit)

        output_result(ctx, commit_results)


@data_commands.command('clone')
@DataVolumeOptions.data_volume_id_argument()
@click.option('--dest-folder', '-d', required=True)
@click.option('--dest-file', '-df', default='$@name', show_default=True)
@click.option('--query', '-q', required=False)
@click.option('--delete', is_flag=True, required=False)
@click.option('--batch-size', required=False, default=-1)
@CommonOptions.processes_option()
@CommonOptions.no_progressbar_option()
@DataVolumeOptions.isolation_token_option()
@click.pass_context
def clone_data(ctx, volume_id, dest_folder, dest_file, query, delete, batch_size, processes, no_progressbar, isolation_token):
    if delete and (dest_folder in ('.', './', '/', os.path.expanduser('~'), '~', '~/')):
        raise click.BadParameter("for protection --dest can't point into current directory while using delete")

    dest_folder = __expend_and_validate_path(dest_folder, expand_vars=False, validate_path=False)

    root_dest = DestPathEnum.find_root(dest_folder)
    dest_pattern = DestPathEnum.get_dest_path(dest_folder, dest_file)

    if delete:
        safe_rm_tree(root_dest)

    safe_make_dirs(root_dest)

    with with_repo_dynamic(ctx, volume_id) as repo:
        data_sync = DataSync(ctx, repo, no_progressbar)
        try:
            phase_meta = data_sync.download_all(query, root_dest, dest_pattern, batch_size, processes, isolation_token=isolation_token)
        except MetadataOperationError as ex:
            click.echo(ex, err=True)
            sys.exit(1)

        data_sync.save_metadata(root_dest, phase_meta)


@data_commands.group('metadata')
def metadata_commands():
    pass


def stats_from_json(now, json_data):
    return os.stat_result((
        0,  # mode
        0,  # inode
        0,  # device
        0,  # hard links
        0,  # owner uid
        0,  # gid
        len(json_data),  # size
        0,  # atime
        now,
        now,
    ))


@data_commands.command('query')
@DataVolumeOptions.data_volume_id_argument()
@click.option('--query', '-q')
@click.option('--batch-size', required=False, default=-1)
@click.option('--as-dict/--as-list', is_flag=True, required=False, default=False)
@click.option('--silent', is_flag=True, required=False, default=False)
@click.pass_context
def query_metadata(ctx, volume_id, query, batch_size, as_dict, silent):
    if as_dict and ctx.obj.output_format != 'json':
        raise click.BadParameter("--as-dict most come with global flag --output-format json")

    def get_all_results():
        for item in download_iter.fetch_all():
            if as_dict:
                yield item['@path'], item
            else:
                yield item

    try:
        with with_repo_dynamic(ctx, volume_id) as repo:
            data_sync = DataSync(ctx, repo, no_progressbar=True)

            download_iter = data_sync.create_download_iter(query, batch_size, silent=silent)

            output_result(ctx, get_all_results())
    except MetadataOperationError as ex:
        click.echo(str(ex), err=True)
        sys.exit(1)


def chunks(l, n):
    result = []
    for item in l:
        result.append(item)

        if len(result) == n:
            yield result
            result = []

    if result:
        yield result


class File2(click.File):
    def convert(self, value, param, ctx):
        from chardet.universaldetector import UniversalDetector

        value = os.path.expanduser(value)

        with closing(UniversalDetector()) as detector:
            with open(value, 'rb') as f:
                data = f.read(1024)
                detector.feed(data)

        self.encoding = detector.result['encoding']

        return super(File2, self).convert(value, param, ctx)


def __repo_validate_data_path(repo, volume_id):
    if repo.data_path:
        return

    msg = 'Data volume {0} was not mapped on this machine, ' \
          'you should call "ml data map {0} --data_path [root path of data]" ' \
          'in order to work with the volume locally'.format(volume_id)
    click.echo(msg, err=True)
    sys.exit(1)


# noinspection PyShadowingBuiltins
@metadata_commands.command('add')
@DataVolumeOptions.data_volume_id_argument()
@click.option('--files', '-f', multiple=True)
@click.option('--data', '-d', required=False, callback=CommonOptions.validate_json)
@click.option('--data-point', '-dp', multiple=True)
@click.option('--data-file', '-df', required=False, type=File2(encoding='utf-16'))
@click.option('--property', '-p', required=False, type=(str, str), multiple=True)
@click.option('--property-int', '-pi', required=False, type=(str, int), multiple=True)
@click.option('--property-float', '-pf', required=False, type=(str, float), multiple=True)
@click.option('--update/--replace', is_flag=True, default=True, required=False)
@CommonOptions.no_progressbar_option()
@click.pass_context
def add_to_metadata(
        ctx, volume_id, files, data, data_point, data_file, property, property_int, property_float, update, no_progressbar):

    def get_per_data_entry():
        data_per_entry = data or {}

        for props in (property, property_int, property_float):
            if not props:
                continue

            for prop_name, prop_val in props:
                data_per_entry[prop_name] = prop_val

        return data_per_entry

    def json_data_from_files(data_path, files, data_per_entry):
        def rel_path_if_needed(path):
            if os.path.isabs(path):
                return os.path.relpath(path, data_path)

            return path

        for file_path in enumerate_paths(files):
            file_path = rel_path_if_needed(file_path)
            yield file_path, data_per_entry

    def get_current_data_file():
        data_list = []

        if data_file:
            json_data = json.load(data_file)

            for key, val in json_data.items():
                val = MetadataFiles.convert_data_unsupported_type(val)
                data_list.append((key, val))
        else:
            per_entry_data = get_per_data_entry()
            per_entry_data = MetadataFiles.convert_data_unsupported_type(per_entry_data)
            if files:
                entries = list(files)

                __repo_validate_data_path(repo, volume_id)
                json_data = json_data_from_files(repo.data_path, entries, per_entry_data)

                data_list.extend(json_data)

            for data_point_name in (data_point or []):
                data_list.append((data_point_name, per_entry_data))

        with closing(AvroWriter()) as avro_writer:
            avro_writer.append_data(data_list)

        return avro_writer.stream

    with with_repo_dynamic(ctx, volume_id) as repo:
        file_obj = get_current_data_file()
        data_sync = DataSync(ctx, repo, no_progressbar)
        data_sync.upload_and_update_metadata(file_obj, file_type='avro')


@data_commands.command('list')
@click.pass_context
def list_data_volumes(ctx):
    projects = ApiCaller.call(ctx.obj, ctx.obj.session, 'get', 'data_volumes')

    output_result(ctx, projects.get('volumes', []), ['id', 'display_name', 'description', 'org'])
