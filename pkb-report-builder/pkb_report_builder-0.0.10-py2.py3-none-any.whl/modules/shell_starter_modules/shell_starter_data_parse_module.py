import click

@click.group()
def data_parse_commands_cli():
    pass

#get data from file
@data_parse_commands_cli.command()
@click.option('--file_name', required=True, type=str)
#@click.option('--age', required=False, type=int)
def get_data_from_file(file_name):
    click.echo("Name = " + file_name)