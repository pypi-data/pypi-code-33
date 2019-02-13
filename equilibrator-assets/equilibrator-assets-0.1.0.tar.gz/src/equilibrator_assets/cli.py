# The MIT License (MIT)
#
# Copyright (c) 2018 Institute for Molecular Systems Biology, ETH Zurich.
# Copyright (c) 2018 Novo Nordisk Foundation Center for Biosustainability,
# Technical University of Denmark
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.


"""Define the command line interface (CLI) for generating assets."""


import logging
import os
from os.path import dirname, join, pardir
from shutil import rmtree
from tempfile import mkdtemp

import click
import click_log
import pandas as pd
import quilt
import whoosh.index as search_index
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from tqdm import tqdm


try:
    from equilibrator_cache import (
        Base,
        CompoundIdentifier,
        CompoundSearchSchema,
        Registry,
    )
    from equilibrator_cache.compound_cache import (
        DEFAULT_DATABASE_URL,
        DEFAULT_QUILT_PKG,
    )
    from support import compounds, metanetx, registry, thermodynamics
except Exception:
    pass


logger = logging.getLogger()
click_log.basic_config(logger)
Session = sessionmaker()


DEFAULT_INDEX_LOCATION = join(
    dirname(__file__), pardir, "src", "equilibrator_cache", "cache", "index"
)
try:
    NUM_PROCESSES = len(os.sched_getaffinity(0))
except OSError:
    logger.warning(
        "Could not determine the number of cores available - assuming 1."
    )
    NUM_PROCESSES = 1
ERROR_LOG = join(mkdtemp(prefix="equilibrator_cache_"), "error")


@click.group()
@click.help_option("--help", "-h")
@click_log.simple_verbosity_option(
    logger,
    default="INFO",
    show_default=True,
    type=click.Choice(["CRITICAL", "ERROR", "WARN", "INFO", "DEBUG"]),
)
def cli():
    """Command line interface to populate and update the equilibrator cache."""
    pass


@cli.command()
@click.help_option("--help", "-h")
@click.option(
    "--location",
    metavar="URL",
    default=DEFAULT_DATABASE_URL,
    show_default=True,
    help="A string interpreted as an rfc1738 compatible database URL.",
)
@click.option(
    "--update/--no-update",
    default=True,
    show_default=True,
    help="Check the MetaNetX FTP server for updated tables.",
)
@click.option(
    "--batch-size",
    type=int,
    default=1000,
    show_default=True,
    help="The size of batches of compounds to transform at a time.",
)
@click.option(
    "--error-log",
    type=click.Path(dir_okay=False, writable=True),
    default=ERROR_LOG,
    show_default=True,
    help="The base file path for error output.",
)
def init(location: str, update: bool, batch_size: int, error_log: str):
    """Drop any existing tables and populate the database using MetaNetX."""
    engine = create_engine(location)
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    session = Session(bind=engine)
    if update:
        logger.info("Updating MetaNetX content.")
        metanetx.update_tables()
    logger.info("Parsing compound cross-references.")
    chem_xref = metanetx.load_compound_cross_references()
    logger.info("Populating registries.")
    registry.populate_registries(session, chem_xref)
    logger.info("Loading compound properties.")
    chem_prop = metanetx.load_compound_properties()
    logger.info("Populating compounds.")
    compounds.populate_compounds(session, chem_prop, chem_xref, batch_size)
    logger.info("Populating additional compounds.")
    compounds.populate_additional_compounds(session)
    logger.info("Filling in missing InChIs from KEGG.")
    compounds.fetch_kegg_missing_inchis(session)


@cli.command()
@click.help_option("--help", "-h")
@click.option(
    "--location",
    metavar="URL",
    default=DEFAULT_DATABASE_URL,
    show_default=True,
    help="A string interpreted as an rfc1738 compatible database URL.",
)
@click.option(
    "--kegg/--no-kegg",
    default=True,
    show_default=True,
    help="By default, calculate thermodynamic information for compounds "
    "contained in KEGG only.",
)
@click.option(
    "--batch-size",
    type=int,
    default=1000,
    show_default=True,
    help="The size of batches of compounds to transform at a time.",
)
@click.option(
    "--error-log",
    type=click.Path(dir_okay=False, writable=True),
    default=ERROR_LOG,
    show_default=True,
    help="The base file path for error output.",
)
def fill(location: str, kegg: bool, batch_size: int, error_log: str):
    """
    Calculate atom bags and molecular masses for compounds missing those.

    Use openbabel to calculate the atom bags and molecular masses of all
    the compounds that are missing these values.

    """
    engine = create_engine(location)
    session = Session(bind=engine)

    logger.info("Filling in missing masses and atom bags.")
    compounds.fill_missing_values(
        session, only_kegg=kegg, batch_size=batch_size, error_log=error_log
    )


@cli.command()
@click.help_option("--help", "-h")
@click.option(
    "--location",
    metavar="URL",
    default=DEFAULT_DATABASE_URL,
    show_default=True,
    help="A string interpreted as an rfc1738 compatible database URL.",
)
@click.option(
    "--kegg/--no-kegg",
    default=True,
    show_default=True,
    help="By default, calculate thermodynamic information for compounds "
    "contained in KEGG only.",
)
@click.option(
    "--batch-size",
    type=int,
    default=100,
    show_default=True,
    help="The size of batches of compounds considered at a time.",
)
@click.option(
    "--error-log",
    type=click.Path(dir_okay=False, writable=True),
    default=ERROR_LOG,
    show_default=True,
    help="The base file path for error output.",
)
def thermo(location: str, kegg: bool, batch_size: int, error_log: str) -> None:
    """Calculate and store thermodynamic information for compounds."""
    engine = create_engine(location)
    session = Session(bind=engine)
    thermodynamics.populate_microspecies(
        session, only_kegg=kegg, batch_size=batch_size, error_log=error_log
    )


@cli.command()
@click.help_option("--help", "-h")
@click.option(
    "--db-url",
    metavar="URL",
    default=DEFAULT_DATABASE_URL,
    show_default=True,
    help="A string interpreted as an rfc1738 compatible database URL.",
)
@click.option(
    "--index-location",
    metavar="PATH",
    default=DEFAULT_INDEX_LOCATION,
    show_default=True,
    help="A directory where the search index should be stored.",
)
@click.option(
    "--processes",
    "-p",
    type=int,
    default=NUM_PROCESSES,
    show_default=True,
    help="The number of cores to use for parallel processing.",
)
@click.option(
    "--memory-limit",
    type=int,
    default=1024,
    show_default=True,
    help="Roughly the maximum memory used per process for indexing in MB.",
)
def index(db_url: str, index_location: str, processes: int, memory_limit: int):
    """Remove an existing Whoosh search index and generate a new one."""
    engine = create_engine(db_url)
    session = Session(bind=engine)
    try:
        logger.info("Removing any index at location %r.", index_location)
        rmtree(index_location)
    except FileNotFoundError:
        logger.debug("No previous index found.")
    logger.info("Indexing compound names.")
    os.mkdir(index_location)
    idx = search_index.create_in(index_location, CompoundSearchSchema)
    writer = idx.writer(procs=processes, limitmb=memory_limit)
    query = (
        session.query(
            CompoundIdentifier.id,
            CompoundIdentifier.compound_id,
            CompoundIdentifier.accession,
        )
        .join(Registry)
        .filter(Registry.namespace == "synonyms")
    )
    total = query.count()
    for row in tqdm(query.yield_per(10000), total=total, desc="Names"):
        writer.add_document(
            identifier_id=row.id,
            compound_id=row.compound_id,
            name=row.accession,
        )
    logger.info("Finalizing index.")
    writer.commit()


@cli.command()
@click.help_option("--help", "-h")
@click.option(
    "--db-url",
    metavar="URL",
    default=DEFAULT_DATABASE_URL,
    show_default=True,
    help="A string interpreted as an rfc1738 compatible database URL.",
)
@click.option(
    "--quilt_pkg",
    metavar="PATH",
    default=DEFAULT_QUILT_PKG,
    show_default=True,
    help="Quilt package name for the compound cache.",
)
def quilt_push(db_url: str, quilt_pkg: str):
    """Remove an existing Whoosh search index and generate a new one."""
    engine = create_engine(db_url)
    quilt.install(quilt_pkg)

    # upload the tables one by one to quilt
    for table_name in engine.table_names():
        df = pd.read_sql_table(table_name, engine)
        quilt.build(join(quilt_pkg, "compounds", table_name), df)

    quilt.push(quilt_pkg, is_public=True)
