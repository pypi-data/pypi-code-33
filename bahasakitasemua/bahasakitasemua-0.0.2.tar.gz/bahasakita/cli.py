import click

from bahasakita import data_engineer

epilog = ("Welcome to Bahasakita Recruitment Test Repository")


@click.group(epilog=epilog)
def cli():
    pass


@cli.command(name="data-engineer", short_help=data_engineer.generate_short_help, help=data_engineer.generate_usage)
@click.argument("candidate_email", type=str)
@click.option("--output-dir", default="data", help="Output directory",
              type=click.Path(exists=False, file_okay=False, writable=True))
@click.option("--num-files", default=40, type=int, help="Number of files")
@click.option("--num-workers", default=2, type=int, help="Number of workers")
def generate_dataset(candidate_email, output_dir, num_files, num_workers):
    data_engineer.dataset.generate_data(candidate_email, output_dir, num_files, num_workers)
    click.secho("bahasakita > Output: " + output_dir + "/", fg="green")


def main():
    cli()
