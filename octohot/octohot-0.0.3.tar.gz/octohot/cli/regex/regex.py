import click


@click.group()
def regex():
    """RegEx provider for octohot"""


from octohot.cli.regex.find import find
regex.add_command(find)

from octohot.cli.regex.replace import replace
regex.add_command(replace)

if __name__ == '__main__':
    regex()
