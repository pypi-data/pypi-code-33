# The MIT License (MIT)
#
# Copyright (c) 2013 Weizmann Institute of Science.
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


import atexit
import logging
from contextlib import ExitStack
from os.path import dirname, join
from typing import List

import quilt
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound

from equilibrator_cache.models import Compound, CompoundIdentifier, Registry


logger = logging.getLogger(__name__)
Session = sessionmaker()
file_manager = ExitStack()
atexit.register(file_manager.close)

DEFAULT_DATABASE_LOCATION = join(dirname(__file__), "cache", "compounds.sqlite")

DEFAULT_DATABASE_URL = f"sqlite:///{DEFAULT_DATABASE_LOCATION}"
DEFAULT_QUILT_PKG = "equilibrator/cache"


def sqlite_deserializer(connection):
    """
    populate an SQLite DB with DataFrames from a Quilt pacakge

    :param engine: A SQLite engine
    """

    def _sqlite_deserializer(node, paths):
        if type(node) == quilt.nodes.DataNode:
            raise ValueError("Can only use SQLite deserializer on GroupNodes")

        for table_name, child in node._children.items():
            df = child()
            logger.debug(
                f"Inserting {df.shape[0]} entries to sqlite DB table "
                f"{table_name}"
            )
            df.to_sql(
                table_name,
                con=connection,
                index=False,
                index_label="id",
                if_exists="replace",
            )

    return _sqlite_deserializer


class Singleton(type):
    """
    Define a singleton metaclass.

    Overrides a child's `__call__` classmethod thus ensuring that per process
    there can only ever be one instance of the child class.

    """

    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(
                *args, **kwargs
            )
        return cls._instances[cls]


class CompoundCache(metaclass=Singleton):
    """
    Implement a compound cache for look ups.

    CompoundCache is a singleton that handles caching of Compound objects for
    the component-contribution package.  The Compounds are retrieved by their
    ID (e.g., KEGG COMPOUND ID, ChEBI Id or HMDB in most cases) or InChI Key.
    The first time a Compound is requested, it is obtained from the relevant
    database and a Compound object is created (this takes a while because it
    usually involves internet communication and then invoking the ChemAxon
    plugin for calculating the pKa values for that structure). Any further
    request for the same Compound ID will draw the object from the cache. When
    the method dump() is called, all cached data is written to a file that will
    be loaded in future python sessions.

    """

    TABLE_NAMES = [
        "structures",
        "microspecies",
        "atom_bags",
        "cross_references",
    ]

    def __init__(self, location: str = DEFAULT_DATABASE_URL):
        # an RAM-only cache for Compound objects that have already
        # been looked up in this session
        self.compound_dict = dict()

        engine = create_engine(location)
        if engine.table_names() == []:
            # Download the data from Quilt
            quilt.install(DEFAULT_QUILT_PKG, force=True)
            pkg = quilt.load(DEFAULT_QUILT_PKG)

            logger.debug("Populating SQLite Database from the Quilt package")
            connection = engine.connect()
            try:
                trans = connection.begin()
                pkg.compounds._data(asa=sqlite_deserializer(connection))

                connection.execute(
                    "CREATE INDEX ix_compound_id ON compounds (id)"
                )
                connection.execute(
                    "CREATE INDEX ix_compounds_inchi ON compounds (inchi)"
                )
                connection.execute(
                    "CREATE INDEX ix_compounds_inchi_key ON compounds (inchi_key)"
                )
                connection.execute(
                    "CREATE INDEX ix_compounds_mnx_id ON compounds (mnx_id)"
                )
                connection.execute(
                    "CREATE INDEX ix_compounds_smiles ON compounds (smiles)"
                )
                connection.execute(
                    "CREATE INDEX ix_compound_identifiers_accession ON compound_identifiers (accession)"
                )
                connection.execute(
                    "CREATE UNIQUE INDEX ix_registries_namespace ON registries (namespace)"
                )
                trans.commit()
            except:
                trans.rollback()

        self.session = Session(bind=engine)

    def commit(self):
        self.session.commit()

    def all_compound_accessions(self) -> List[str]:

        return sorted(
            self.session.query(CompoundIdentifier.accession).distinct()
        )

    def accession_exists(self, accession: str) -> bool:
        try:
            self.session.query(CompoundIdentifier).filter_by(
                accession=accession
            ).one()
            return True
        except NoResultFound:
            return False

    def get_compound_by_internal_id(self, compound_id: int) -> Compound:
        """Find a compound in the cache based on the internal ID (integer)

        :param compound_id:
        :return:
        """
        return (
            self.session.query(Compound).filter_by(id=compound_id).one_or_none()
        )

    def get_compound(self, compound_id: str) -> Compound:
        if compound_id.find(":") != -1:
            namespace, accession = compound_id.split(":", 1)
            namespace = namespace.lower()
        else:
            namespace, accession = None, compound_id

        return self.get_compound_from_registry(namespace, accession)

    def get_compound_from_registry(
        self, namespace: str, accession: str
    ) -> Compound:

        if (namespace, accession) in self.compound_dict:
            logging.debug(f"Cache hit for {accession} in {namespace} in RAM")
            return self.compound_dict[(namespace, accession)]

        query = self.session.query(Compound)
        if namespace == "mnx":
            # if the namespace is MetaNetX, simply use that column in the
            # Compound table
            logging.debug(f"Looking for {accession} in MetaNetX")
            query = query.filter_by(mnx_id=accession)
        elif namespace == "inchi_key":
            # try to find this compound by assuming the input is an InChIKey
            logging.debug(f"Looking for {accession} as InChIKey")
            query = query.filter_by(inchi_key=accession)
        else:
            query = query.join(CompoundIdentifier).filter(
                CompoundIdentifier.accession == accession
            )
            if namespace is None:
                # if the namespace is not given, use the accession alone to
                # find the compound
                logging.debug(f"Looking for {accession} in all namespaces")
            else:
                # otherwise, use the specific namespace and accession to
                # locate the compound.
                logging.debug(f"Looking for {accession} in {namespace}")
                query = query.join(Registry).filter(
                    Registry.namespace == namespace
                )

        compound = query.one_or_none()

        if compound is None:
            logging.debug(f"Cache miss")
            return None
        else:
            logging.debug(f"Cache hit")
            self.compound_dict[(namespace, accession)] = compound
            return compound

    def cache_registry_in_ram(self, namespace: str) -> None:
        if namespace == "mnx":
            query = self.session.query(Compound, Compound.mnx_id).filter(
                Compound.mnx_id.isnot(None)
            )
        elif namespace == "inchi_key":
            query = self.session.query(Compound, Compound.inchi_key).filter(
                Compound.inchi_key.isnot(None)
            )
        elif namespace is None:
            raise ValueError("namespace cannot be None")
        else:
            registry = (
                self.session.query(Registry)
                .filter(Registry.namespace == namespace)
                .one_or_none()
            )
            if registry is None:
                raise ValueError(f"namespace '{namespace}' was not found")

            query = (
                self.session.query(Compound, CompoundIdentifier.accession)
                .join(CompoundIdentifier)
                .filter(CompoundIdentifier.compound_id == Compound.id)
                .filter(CompoundIdentifier.registry_id == registry.id)
            )
            if namespace == "kegg":
                query = query.filter(CompoundIdentifier.accession.like("C%"))
            query = query.group_by(Compound.id)

        for compound, accession in query:
            if (namespace, accession) not in self.compound_dict:
                self.compound_dict[(namespace, accession)] = compound
