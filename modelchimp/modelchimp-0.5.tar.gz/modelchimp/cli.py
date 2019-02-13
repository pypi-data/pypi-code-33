import click
import os
import ntpath
#Temp, delete this
import sys
import tempfile
from shutil import make_archive, rmtree, unpack_archive, copy
sys.path.insert(0, '.')

from modelchimp.connection_thread import RestConnection
from modelchimp.utils import generate_uid
from modelchimp.log import get_logger

logger = get_logger(__name__)

@click.group()
def cli():
    pass

@cli.command()
@click.option('--host', '-h', default='localhost:8000')
@click.option('--project-key', '-k')
@click.argument('path')
def sync(host, project_key, path):
    if not project_key:
        raise click.BadParameter("--project-key is required", param=project_key)

    # Current working directory
    cwd = os.getcwd()
    full_path = os.path.join(cwd, path)
    data, file_locations = create_temp_file(full_path)

    # Connection addresses
    rest_address = "%s/" %(host,)
    version_id = generate_uid()
    rest = RestConnection(rest_address, project_key, version_id)
    rest.create_data_version(version_id, data, file_locations)


@cli.command()
@click.option('--host', '-h', default='localhost:8000')
@click.option('--project-key', '-k')
@click.argument('id')
def pull_data(host, project_key, id):
    if not project_key:
        raise click.BadParameter("--project-key is required", param=project_key)

    # Connection addresses
    rest_address = "%s/" %(host,)
    rest = RestConnection(rest_address, project_key, id)

    url = 'api/retrieve-data-version/%s/?data-version=%s' % (rest.project_id, id)

    logger.info("Downloading data with the id: %s" % id)
    request = rest.get(url)

    if request.status_code == 400:
        logger.info("Unable to download data. Is it a valid id?")

    data_object = request.content

    with open('data.zip', 'wb') as f:
        f.write(data_object)

    unpack_archive('data.zip', 'data')
    os.remove('data.zip')

def create_temp_file(path):
    file = None
    file_locations = []

    if os.path.isfile(path):
        file = _compress_file(path)
        file_locations.append(path)
    elif os.path.isdir(path):
        for path, subdirs, files in os.walk(path):
            for name in files:
                file_locations.append(os.path.join(path, name))
        file = _compress_folder(path)
    else:
        print("Oops, path is neither a file nor a folder")
        return

    return file, file_locations

def _compress_file(path):
    tmpdir = tempfile.mkdtemp()
    try:
        tmpdata = os.path.join(tmpdir, 'data')
        os.mkdir(tmpdata)
        copy(path, tmpdata)

        tmparchive = os.path.join(tmpdir, 'arhive')
        data = open(make_archive(tmparchive, 'zip', tmpdata), 'rb').read()
    finally:
        rmtree(tmpdir)

    return data

def _compress_folder(path):
    tmpdir = tempfile.mkdtemp()
    try:
        tmparchive = os.path.join(tmpdir, 'data')
        data = open(make_archive(tmparchive, 'zip', path), 'rb').read()
    finally:
        rmtree(tmpdir)

    return data

if __name__ == "__main__":
    cli()
