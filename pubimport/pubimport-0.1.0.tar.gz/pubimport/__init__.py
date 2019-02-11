import pathlib

import bibtexparser
import click
from click import command, Path, argument, File
from dominate.tags import *


@command()
@argument('source_dir', type=click.Path(exists=True))
@argument('destination', type=File('w'))
def cli(source_dir, destination):
    root = pathlib.Path(source_dir)
    container = div()
    for source in root.iterdir():
        with source.open() as f:
            data = bibtexparser.load(f)
        container.add(section())
        # for entry in data.entries:
    destination.write(container)

# for topic in topics
#     section.topic-section
#     h2.h2.topic-title= topic.title
#     ul.paper-list
#     for paper in topic.papers
#         li
#             h3.paper-title= paper.title
#             p= paper.authors
#             p= paper.journal

