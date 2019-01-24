
import click

from os.path import abspath

from ..project_schema import ProjectSchema
from .bio import (
    add_named_fastx_to_schema,
    add_unnamed_fastx_to_schema,
)


@click.group('bio')
def bio_cli():
    pass


def get_file_logger(file):
    """Return a logger that writes to a file."""
    def logger(val):
        file.write(val + '\n')
    return logger


def get_schema_builder(source):
    """Return a function that returns file schema."""
    def build_schema(path, md5, line_count, sample_name=None):
        out = {
            'path': path,
            source: {},
            'md5': md5,
            'unzipped_line_count': line_count,
        }
        if sample_name:
            out['sample_name'] = sample_name
            return out
        return out
    return build_schema


@bio_cli.command()
@click.option('-s/-u', '--sample-names/--unnamed', default=False)
@click.argument('source')
@click.argument('schema')
@click.argument('err_file', type=click.File('a'))
@click.argument('filenames', nargs=-1)
def add_fastx(sample_names, source, schema, err_file, filenames):
    """Add fastx files to a schema with a health check and checksums."""
    project_schema = ProjectSchema.from_file(schema)
    existing_filepaths = {file_schema['path'] for file_schema in project_schema.files}
    filepaths = [
        abspath(filename) for filename in filenames
        if abspath(filename) not in existing_filepaths
    ]
    logger, build_schema = get_file_logger(err_file), get_schema_builder(source)
    if sample_names:
        schema = add_named_fastx_to_schema(schema, filepaths, logger, build_schema)
    else:
        schema = add_unnamed_fastx_to_schema(schema, filepaths, logger, build_schema)


if __name__ == '__main__':
    bio_cli()
