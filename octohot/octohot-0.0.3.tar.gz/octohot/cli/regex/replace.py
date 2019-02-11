import click


@click.command()
@click.argument('find_string')
@click.argument('replace_string')
@click.option('--file_pattern', '-f', default="*",
              help='Define a file pattern')
@click.option('--dry-run', '-d', is_flag=True, default=False,
              help='print only replace')
def replace(find_string, file_pattern, replace_string, dry_run):
    """Find and replace a string in all repos"""
    from octohot.cli.config import repositories
    from octohot.cli.regex.file import File
    for repo in repositories:
        files = repo.files(file_pattern)
        for file in files:
            f = File(file)
            f.replace(find_string, replace_string, dry_run)
