import click
from nmqn import crawl as crl
from nmqn import compare as cmp


DEFAULT_PATH = "~/.nmqn"
# TODO:: ロギング

@click.group()
def cmd():
    pass

@cmd.command()
@click.option('config', '-c', required=True, type=str, help='Config path.')
@click.option('max_tab', '-m', default=10, type=int, help='Chrome Tab.')
@click.option('path', '-p', default=DEFAULT_PATH, type=str, help='OutputPath')
@click.option('--debug', is_flag=True, help='not headless mode')
def crawl(config, max_tab, path, debug):
    crl.execute(config, max_tab, path, not debug)


@cmd.command()
@click.option('config', '-c', required=True, type=str, help='Config path.')
@click.option('x', '-x', default=None, type=str, help='before path.')
@click.option('y', '-y', default=None, type=str, help='after path.')
@click.option('path', '-p', default=DEFAULT_PATH, type=str, help='Crawl path.')
def compare(config, x, y, path):
    cmp.execute(config, x, y, path)


def main():
    cmd()

if __name__ == "__main__":
    main()