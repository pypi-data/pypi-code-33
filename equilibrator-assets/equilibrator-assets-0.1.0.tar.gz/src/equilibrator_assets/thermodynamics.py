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


"""Enrich compounds with thermodynamic information."""


import logging
import typing
from os.path import dirname, join, pardir

import pandas as pd
from equilibrator_cache import (
    Compound,
    CompoundIdentifier,
    CompoundMicrospecies,
    Registry,
)
from sqlalchemy import and_, or_
from sqlalchemy.orm import sessionmaker
from tqdm import tqdm

from . import chemaxon


logger = logging.getLogger("populate.thermodynamics")
Session = sessionmaker()


def create_microspecies(
    molecules: pd.DataFrame,
    error_log: str,
    num_acidic: int,
    num_basic: int,
    min_ph: float,
    mid_ph: float,
    max_ph: float,
) -> typing.Tuple[typing.List[dict], typing.List[dict]]:
    """
    Coordinate the calculation of a single batch of compounds.

    Parameters
    ----------
    molecules : pandas.DataFrame
        The input data frame representing compounds through InChIs.
    error_log : str
        The base file path for error output.
    num_acidic : int
        The maximal number of acidic pKas to calculate.
    num_basic : int
        The maximal number of basic pKas to calculate.
    min_ph : float
        The minimal pH to consider.
    mid_ph : float
        The pH for which the major pseudoisomer is calculated.
    max_ph : float
        The maximal pH to consider.

    Returns
    -------
    tuple
        list
            A list of mappings for updating a compounds with atom bag and
            dissociation constants.
        list
            A list of microspecies mappings for those compounds.

    """

    def MoleculeDataToMappings(
        compound_id: int,
        mol_data: chemaxon.MoleculeData,
        compounds: typing.List[typing.Dict],
        microspecies: typing.List[typing.Dict],
    ) -> None:
        compounds.append(
            {
                "id": compound_id,
                "atom_bag": mol_data.atom_bag,
                "smiles": mol_data.smiles,
                "dissociation_constants": [],
            }
        )

        if mol_data.charge is not None and mol_data.number_protons is not None:
            microspecies.append(
                {
                    "compound_id": compound_id,
                    "charge": mol_data.charge,
                    "number_protons": mol_data.number_protons,
                    "ddg_over_rt": 0,
                    "is_major": True,
                }
            )

    compounds = []
    microspecies = []

    override_mask = molecules.mnx_id.isin(chemaxon.METANETX_EXCEPTIONS)
    for row in molecules.loc[override_mask, :].itertuples(index=False):
        mol_data = chemaxon.METANETX_EXCEPTIONS[row.mnx_id]
        MoleculeDataToMappings(row.id, mol_data, compounds, microspecies)

    molecules = molecules.loc[~override_mask, :]

    override_mask = molecules.inchi.isin(chemaxon.INCHI_EXCEPTIONS)
    for row in molecules.loc[override_mask, :].itertuples(index=False):
        mol_data = chemaxon.INCHI_EXCEPTIONS[row.inchi]
        MoleculeDataToMappings(row.id, mol_data, compounds, microspecies)

    molecules = molecules.loc[~override_mask, :]

    if molecules.shape[0] > 0:
        try:
            constants, pka_columns = chemaxon.get_dissociation_constants(
                molecules, error_log, num_acidic, num_basic, mid_ph
            )
            for row in constants.itertuples(index=False):
                cmpd_obj, ms_objs = chemaxon.get_microspecies_data(
                    row, min_ph, mid_ph, max_ph, pka_columns
                )
                compounds.append(cmpd_obj)
                microspecies.extend(ms_objs)

                # TODO: Caching of objects needs to happen here. Will require
                #  some restructuring of code.

        except ValueError as e:
            logger.warning(str(e))
            pass

    return compounds, microspecies


def populate_microspecies(
    session: Session,
    only_kegg: bool,
    batch_size: int,
    error_log: str,
    num_acidic: int = 20,
    num_basic: int = 20,
    min_ph: float = 0.0,
    mid_ph: float = 7.0,
    max_ph: float = 14.0,
) -> None:
    """
    Calculate dissociation constants and create microspecies.

    Parameters
    ----------
    session : sqlalchemy.orm.session.Session
        An active session in order to communicate with a SQL database.
    only_kegg : bool
        Calculate thermodynamic information for compounds contained in KEGG
        only.
    batch_size : int
        The size of batches of compounds considered at a time.
    error_log : str
        The base file path for error output.
    num_acidic : int
        The maximal number of acidic pKas to calculate.
    num_basic : int
        The maximal number of basic pKas to calculate.
    min_ph : float
        The minimal pH to consider.
    mid_ph : float
        The pH for which the major pseudoisomer is calculated.
    max_ph : float
        The maximal pH to consider.

    """
    if only_kegg:
        # Construct a query only including KEGG compounds.
        query = session.query(Compound.id, Compound.mnx_id, Compound.inchi)
        query = (
            query.join(CompoundIdentifier)
            .join(Registry)
            .filter(
                or_(
                    and_(
                        Registry.namespace == "kegg",
                        CompoundIdentifier.accession.like("C%"),
                    ),
                    Registry.namespace == "coco",
                ),
                Compound.inchi.isnot(None),
                Compound.dissociation_constants.is_(None),
                Compound.mass.isnot(None),
            )
            .group_by(Compound.id)
            .order_by(Compound.mass, CompoundIdentifier.accession)
        )
        # Query for all compounds.
        # Load all the information into memory in order for the query to not be
        # updated during insertion of information. The current size in MetaNetX
        # is 700k compounds which should be < 100 MB.
        input_list = list(query)

        cc_compound_df = pd.read_csv(
            join(
                dirname(__file__),
                pardir,
                pardir,
                "src",
                "equilibrator_cache",
                "data",
                "compounds_required_for_cc.csv",
            )
        )

        for row in cc_compound_df.itertuples(index=False):
            if row.namespace.lower() == "mnx":
                compound = (
                    session.query(Compound)
                    .filter(Compound.mnx_id == row.accession)
                    .one_or_none()
                )
            else:
                query = session.query(Compound)
                query = query.join(CompoundIdentifier).join(Registry)
                query = query.filter(
                    Registry.namespace == row.namespace,
                    CompoundIdentifier.accession == row.accession,
                )
                compound = query.group_by(Compound.id).one_or_none()

            if compound is None:
                logger.debug("not found in DB %r", row)
            elif len(compound.microspecies) > 0:
                logger.debug(
                    "already analyzed %r (%d microspecies)",
                    row,
                    len(compound.microspecies),
                )
            else:
                logger.debug("adding to list %r", row)
                input_list.append(
                    (compound.id, compound.mnx_id, compound.inchi)
                )

    else:
        query = session.query(Compound.id, Compound.mnx_id, Compound.inchi)
        query = query.filter(
            Compound.dissociation_constants.is_(None),
            Compound.inchi.isnot(None),
            Compound.mass.isnot(None),
        ).order_by(Compound.mass, Compound.inchi)

        input_list = list(query)

    input_df = pd.DataFrame(data=input_list, columns=["id", "mnx_id", "inchi"])

    with tqdm(total=len(input_df), desc="Analyzed") as pbar:
        for index in range(0, len(input_df), batch_size):
            view = input_df.iloc[index : index + batch_size, :]
            logger.debug(view)
            compounds, microspecies = create_microspecies(
                view,
                f"{error_log}_batch_{index}",
                num_acidic,
                num_basic,
                min_ph,
                mid_ph,
                max_ph,
            )
            session.bulk_update_mappings(Compound, compounds)
            session.bulk_insert_mappings(CompoundMicrospecies, microspecies)
            session.commit()
            pbar.update(len(view))
