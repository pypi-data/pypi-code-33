import click


@click.command()
@click.argument('find_string')
@click.option('--file_pattern', '-f', default="*",
              help='Define a file pattern')
@click.option('--only_filepath', '-p', is_flag=True,
              help='print only filepaths')
def find(find_string, file_pattern, only_filepath):
    """
    Find a regular expression in all repos
    """
    from octohot.cli.config import repositories
    from octohot.cli.regex.file import File
    for repo in repositories:
        files = repo.files(file_pattern)
        for file in files:
            f = File(file)
            matches = f.find(find_string)
            if matches:
                for match in matches:
                    click.echo(
                        "%s (%s:%s)" % (
                            file,
                            f.line(match.start()),
                            f.line(match.end())
                        )
                    )
                    if not only_filepath:
                        click.echo(match.group())
