
import click

from .project_schema import ProjectSchema
from .exceptions import InvalidLLPSException
from .utils import md5_sum
from .constants import CURRENT_SPEC_VERSION
from .bio.cli import bio_cli


@click.group()
def main():
    pass


main.add_command(bio_cli)


@main.command('validate')
@click.argument('filepath')
def cli_validate_schema(filepath):
    """Validate a schema as a valid project schema."""
    try:
        ProjectSchema.from_file(filepath)
    except InvalidLLPSException as exc:
        click.echo(exc, err=True)


@main.command('add-files')
@click.option('-c/-n', '--use-checksums/--no-checksums', default=True)
@click.argument('source')
@click.argument('schema')
@click.argument('filepaths', nargs=-1)
def cli_add_files_to_schema(use_checksums, source, schema, filepaths):
    """Add files to the specified project. Write the result to stdout."""
    project_schema = ProjectSchema.from_file(schema)
    with click.progressbar(filepaths) as bar:
        for filepath in bar:
            file_schema = {
                'path': filepath,
                source: {},
                'md5': 'none',
            }
            if use_checksums:
                file_schema['md5'] = md5_sum(filepath)
            project_schema.add_file(file_schema)
    click.echo(project_schema.dump())


@main.command('new')
@click.argument('project_name')
def cli_new_schema(project_name):
    """Dump a new project schema to stdout."""
    kwargs = {
        'project_name': project_name,
        'project_description': '',
        'version': 'v0.1.0',
        'spec_version': CURRENT_SPEC_VERSION,
        'sources': {},
        'files': []
    }
    project_schema = ProjectSchema(**kwargs)
    click.echo(project_schema.dump())


@main.command('remove-files')
@click.argument('schema')
@click.argument('filepaths', nargs=-1)
def cli_remove_files_from_schema(schema, filepaths):
    """Add files to the specified project. Write the result to stdout."""
    project_schema = ProjectSchema.from_file(schema)
    indexed_files = {
        file_schema['path']: file_schema for file_schema in project_schema.files
    }
    with click.progressbar(filepaths) as bar:
        for filepath in bar:
            if filepath in indexed_files:
                del indexed_files[filepath]
    project_schema.files = list(indexed_files.values())
    click.echo(project_schema.dump())


if __name__ == '__main__':
    main()
