import click
import os
import glob
import re
import csv
import types
import sys
import datetime
import json
from girder_client import GirderClient
from edp.composite import _ingest_runs, _ingest_samples
import importlib

class GC(GirderClient):

    def __init__(self, api_url=None, api_key=None):

        def _progress_bar(*args, **kwargs):
            bar = click.progressbar(*args, **kwargs)
            bar.bar_template = "[%(bar)s]  %(info)s  %(label)s"
            bar.show_percent = True
            bar.show_pos = True

            def formatSize(length):
                if length == 0:
                    return '%.2f' % length
                unit = ''
                # See https://en.wikipedia.org/wiki/Binary_prefix
                units = ['k', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y']
                while True:
                    if length <= 1024 or len(units) == 0:
                        break
                    unit = units.pop(0)
                    length /= 1024.
                return '%.2f%s' % (length, unit)

            def formatPos(_self):
                pos = formatSize(_self.pos)
                if _self.length_known:
                    pos += '/%s' % formatSize(_self.length)
                return pos

            bar.format_pos = types.MethodType(formatPos, bar)
            return bar

        _progress_bar.reportProgress = sys.stdout.isatty()

        super(GC, self).__init__(
            apiUrl=api_url, progressReporterCls=_progress_bar)

        self.authenticate(apiKey=api_key)

@click.group()
def cli():
    pass

def _ingest_batch(gc, data_folder, project, cycle, dir, public, summary_func):

    # Loady summary function
    if summary_func is not None:
        try:
            module_name, func_name = summary_func.rsplit('.',1)
            module = importlib.import_module(module_name)
            summary_func = getattr(module, func_name)
        except:
            click.echo(click.style('Unable to load summary function: %s' % summary_func, fg='yellow'))
            raise

    batch_name = os.path.basename(dir)

    # See if we have a MatLab struct
    struct_file = glob.glob('%s/*.mat' % dir)
    if struct_file:
        click.echo(click.style('Uploading MatLab struct file', fg='red'))
        struct_file = gc.uploadFileToFolder(data_folder['_id'], struct_file[0])

    # Create the batch
    batch = {
        'startDate': '',
        'title': batch_name,
        'motivation': '',
        'experimentalDesign': '',
        'experimentalNotes': '',
        'dataNotes': '',
        'public': public
    }

    if struct_file:
        batch['structFileId'] = struct_file['_id']

    batch = gc.post('edp/projects/%s/cycles/%s/batches' % (project, cycle), json=batch)

    click.echo(click.style('Batch created: %s' % batch['_id'], fg='red'))

    metafile_regex =  re.compile(r'^(\d{4}-\d{2}-\d{2}_.*_CH(\d+))_Metadata.csv$')
    for meta_file in glob.glob('%s/*Metadata.csv' % dir):
        name = os.path.basename(meta_file)
        match = metafile_regex.match(name)
        if match is None:
            click.echo(click.style('%s does not have expected filename format, skipping.' % meta_file, fg='yellow'))
            continue

        test_name = match.group(1)
        channel = match.group(2)
        data_file_path = meta_file.replace('_Metadata.csv', '.csv')

        with open(meta_file, 'r') as f:
            reader = csv.DictReader(f)
            row = next(reader)
            start_date = row['first_start_datetime']
            start_date = datetime.datetime.fromtimestamp(int(start_date)).strftime('%Y-%m-%d')
            cell_id = row['item_id']
            schedule_file = row['schedule_file_name']

        click.echo(click.style('Uploading meta data file', fg='blue'))
        meta_file = gc.uploadFileToFolder(data_folder['_id'], meta_file)
        click.echo(click.style('Uploading data file', fg='blue'))
        data_file = gc.uploadFileToFolder(data_folder['_id'], data_file_path)

        if summary_func is not None:
            print(data_file_path)
            summary = summary_func(data_file_path)

        test = {
            'name': test_name,
            'startDate': start_date,
            'cellId': cell_id,
            'batteryType': '',
            'channel': channel,
            'scheduleFile': schedule_file,
            'metaDataFileId': meta_file['_id'],
            'dataFileId': data_file['_id'],
            'public': 'public',
            'summary': summary
        }

        test = gc.post('edp/projects/%s/cycles/%s/batches/%s/tests' % (project, cycle, batch['_id']), json=test)

        click.echo(click.style('Test created: %s' % test['_id'], fg='blue'))

@cli.command('ingest', help='Ingest data')
@click.option('-p', '--project', default=None, help='the project id', required=True)
@click.option('-c', '--cycle', default=None, help='the cycle id', required=True)
@click.option('-d', '--dir', help='path to batch(es) to ingest',
              type=click.Path(exists=True, dir_okay=True, file_okay=False, readable=True), default='.')
@click.option('-u', '--api-url', default='http://localhost:8080/api/v1', help='RESTful API URL '
                   '(e.g https://girder.example.com/api/v1)')
@click.option('-k', '--api-key', envvar='GIRDER_API_KEY', default=None,
              help='[default: GIRDER_API_KEY env. variable]', required=True)
@click.option('-b', '--public', is_flag=True,
              help='Marked the data as public')
@click.option('-s', '--summary-func', default=None, help='Fully qualified name of function to summarize test data.')
def _ingest(project, cycle, api_url, api_key, dir, public, summary_func):
    gc = GC(api_url=api_url, api_key=api_key)

    # Try to get edp data folder
    data_folder = gc.resourceLookup('/collection/edp/data', test=True)

    # Create a private folder
    if data_folder is None:

        me = gc.get('/user/me')
        user_folder = 'Public' if public else 'Private'
        try:
            user_folder = next(gc.listFolder(me['_id'], 'user', user_folder))
        except StopIteration:
            raise Exception('Unable to find user folder: %s' % user_folder)

        data_folder = gc.listFolder(user_folder['_id'], 'folder', name='edp')
        try:
            data_folder = next(data_folder)
        except StopIteration:
            data_folder = gc.createFolder(user_folder['_id'], 'edp', parentType='folder',
                                          public=public)

    dir  = os.path.abspath(dir)

    # See if the input directory contains directories then assume each of them is
    # a batch to ingest.
    batch_dirs = os.listdir(dir)
    if len(batch_dirs) > 0:
        batch_dirs = [os.path.join(dir, b) for b in batch_dirs]
    else:
        batch_dirs = [dir]

    for batch_dir in batch_dirs:
        _ingest_batch(gc, data_folder, project, cycle, batch_dir, public, summary_func)

@cli.command('ingest_composite', help='Ingest composite data')
@click.option('-p', '--project', default=None, help='the project id', required=True)
@click.option('-d', '--dir', help='base path to data to ingest',
              type=click.Path(exists=True, dir_okay=True, file_okay=False, readable=True), default='.')
@click.option('-m', '--channel-map', default=None, type=click.File('r'),
              help='the mapping of channels to elements', required=True)
@click.option('-u', '--api-url', default='http://localhost:8080/api/v1', help='RESTful API URL '
                   '(e.g https://girder.example.com/api/v1)')
@click.option('-k', '--api-key', envvar='GIRDER_API_KEY', default=None,
              help='[default: GIRDER_API_KEY env. variable]', required=True)
def _ingest_composite(project, dir, channel_map, api_url, api_key):
    if dir[-1] != '/':
        dir += '/'
    gc = GirderClient(apiUrl=api_url)
    gc.authenticate(apiKey=api_key)

    dir  = os.path.abspath(dir)
    composite_name = os.path.basename(dir)
    composite = {
        'name': composite_name
    }
    composite = gc.post('edp/projects/%s/composites' % project, json=composite)
    composite = composite['_id']

    channel_map = json.load(channel_map)
    channel_map = {channel.upper():element.lower() for (channel,element) in channel_map.items()}

    experiments = _ingest_runs(gc, project, composite, dir)

    _ingest_samples(gc, project, composite, dir, experiments, channel_map)


