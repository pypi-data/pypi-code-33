# The MIT License (MIT)
#
# Copyright (c) 2013 The Weizmann Institute of Science.
# Copyright (c) 2018 Novo Nordisk Foundation Center for Biosustainability,
# Technical University of Denmark.
# Copyright (c) 2018 Institute for Molecular Systems Biology,
# ETH Zurich, Switzerland.
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


import logging
from typing import Iterable, List, Set, Tuple

import numpy as np
import pandas as pd
import quilt.data.equilibrator.component_contribution

from equilibrator_cache.exceptions import MissingDissociationConstantsException

from . import (
    Compound, F, ParseException, R, Reaction, ccache,
    create_stoichiometric_matrix_from_reactions)


logger = logging.getLogger(__name__)


class TrainingData(object):

    def __init__(self) -> object:
        self.S = None  # a DataFrame containing the stoichiometric matrix
        self.reaction_df = None  # a DataFrame containing all the reaction data
        self._non_decomposable_compounds = []

    @property
    def stoichiometric_matrix(self) -> pd.DataFrame:
        return self.S

    @property
    def compounds(self) -> List[Compound]:
        if self.S is None:
            compounds = {Reaction.PROTON_COMPOUND, Reaction.WATER_COMPOUND}
            for rxn in self.reaction_df.reaction:
                compounds.update(rxn.keys())
            return sorted(compounds)
        else:
            return self.S.index.tolist()

    @property
    def non_decomposable_compounds(self) -> List[Compound]:
        return self._non_decomposable_compounds

    @property
    def decomposable_compounds(self) -> List[Compound]:
        decomposable_compounds = set(self.compounds).difference(
            self.non_decomposable_compounds)
        return sorted(decomposable_compounds)

    @property
    def dG0(self) -> pd.Series:
        return self.reaction_df[['dG0']]

    @property
    def weight(self) -> pd.Series:
        return self.reaction_df[['weight']]

    def balance_reactions(self) -> None:
        """
            use the chemical formulas from the InChIs to verify that each and
            every reaction is balanced
        """
        to_remove = set()
        for row in self.reaction_df[self.reaction_df.balance].itertuples(
            index=True):
            try:
                row.reaction.is_balanced(fix_protons=True,
                                         fix_water=True,
                                         raise_exception=False)
            except ValueError:
                logger.warning("This reaction is not balanced %r",
                               str(row.reaction))
                to_remove.add(row.Index)

        logger.info('After removing %d unbalanced reactions, '
                    'we are left with %d reactions for training',
                    len(to_remove), len(self.reaction_df))

        self.reaction_df = self.reaction_df.drop(to_remove, axis=0)

    def create_stoichiometric_matrix_from_reactions(self) -> None:
        # convert the list of reactions in sparse notation into a full
        # stoichiometric matrix, where the rows (compounds) are in the same
        # order as in 'compounds' and the columns match the reaction indices
        self.S = create_stoichiometric_matrix_from_reactions(
            self.reaction_df.reaction
        )
        self.S.columns = self.reaction_df.index

    @property
    def reactions(self) -> Iterable[Reaction]:
        return self.S.apply(Reaction)

    def reverse_transform(self):
        """
            Calculate the reverse transform for all reactions in training_data.
        """
        self.reaction_df['dG0'] = self.reaction_df['dG0_prime']

        for row, rxn in zip(self.reaction_df.itertuples(index=True),
                            self.reactions):
            try:
                ddG0 = rxn.get_transform_ddG0(pH=row.pH,
                                              ionic_strength=row.I, T=row.T)
                self.reaction_df.at[row.Index, 'dG0'] -= ddG0
            except MissingDissociationConstantsException as e:
                logger.warning(f"Cannot reverse transform {rxn}: {e}")


class ToyTrainingData(TrainingData):

    def __init__(self):
        super().__init__()

        self.reaction_df = (
            quilt.data.equilibrator.component_contribution.train
                .toy_training_data().copy()
        )
        self.reaction_df.loc[:, 'reaction'] = (
            self.reaction_df['reaction'].apply(Reaction.parse_formula)
        )
        self.create_stoichiometric_matrix_from_reactions()
        self.reverse_transform()


class FullTrainingData(TrainingData):

    FORMATION_ENERGY_FNAME = '/data/formation_energies_transformed.csv.gz'
    REACTION_ENERGY_FNAME = '/data/TECRDB.csv.gz'
    OXIDATION_POTENTIAL_FNAME = '/data/redox.csv.gz'

    def __init__(self) -> object:
        super().__init__()

        logger.info('Reading the training data files')
        self.reaction_df, compounds_that_do_not_decompose = \
            self.get_all_thermo_params()

        compounds_that_do_not_decompose.update(
            [Reaction.PROTON_COMPOUND, Reaction.WATER_COMPOUND])
        self.compounds_that_do_not_decompose = list(
            compounds_that_do_not_decompose)

        compounds = set(self.compounds).difference(
            self.compounds_that_do_not_decompose)
        compounds = [cpd for cpd in compounds if cpd.atom_bag is None]

        if len(compounds) > 0:
            for compound in sorted(compounds):
                if compound.inchi is not None:
                    logger.error("Compound %d (%r) has no atom bag, but has "
                                 "an InChI: %r", compound.id,
                                 compound.mnx_id, compound.inchi)
                else:
                    logger.error("Compound %d (%r) has no atom bag or InChI",
                                 compound.id, compound.mnx_id)
            #raise Exception("Some decomposable compounds have no InChI")

        logger.info('Balancing reactions with H2O and H+')
        self.balance_reactions()

        logger.info('Creating the training stoichiometric matrix')
        self.create_stoichiometric_matrix_from_reactions()

        logger.info('Applying reverse Legendre transform on dG0_prime values')
        self.reverse_transform()

    @staticmethod
    def read_tecrdb() -> pd.DataFrame:
        """
        Load a data frame with information from the TECRdb (NIST).

        The component-contribution package distributes data tables with
        information on the 'thermodynamics of enzyme-catalyzed
        reactions'[1, 2]_ that are used as training data.

        Returns
        -------
        pandas.DataFrame

        References
        ----------
        .. [1] Goldberg, Robert N., Yadu B. Tewari, and Talapady N. Bhat.
               “Thermodynamics of Enzyme-Catalyzed Reactions—a Database for
               Quantitative Biochemistry.” Bioinformatics 20, no. 16
               (November 1, 2004): 2874–77.
               https://doi.org/10.1093/bioinformatics/bth314.
        .. [2] http://xpdb.nist.gov/enzyme_thermodynamics/

        """
        tecr_df = (
            quilt.data.equilibrator.component_contribution.train.TECRDB().copy()
        )

        # remove rows with missing crucial data
        tecr_df = tecr_df[~pd.isnull(tecr_df[["K'", "T", "pH"]]).any(axis=1)]

        # calculate the dG'0 from the Keq and T
        dG0_prime = -R * tecr_df["T"] * np.log(tecr_df["K'"])
        tecr_df = tecr_df.assign(**{"dG'0": dG0_prime})

        # parse the reaction
        tecr_df.loc[:, 'reaction'] = tecr_df['reaction'].apply(
                Reaction.parse_formula)

        tecr_df = tecr_df[~pd.isnull(tecr_df['reaction'])]

        tecr_df['balance'] = True
        tecr_df.drop(["url", "method", "K", "K'", "eval", "EC", "enzyme_name"],
                     axis=1, inplace=True)

        logger.debug('Successfully added %d reactions from TECRDB' %
                     tecr_df.shape[0])
        return tecr_df

    @staticmethod
    def read_formations() -> Tuple[pd.DataFrame, Set[Compound]]:
        """
        Read the Formation Energy data from literature data [1-6]

        Returns
        -------
        pandas.DataFrame

        References
        ----------
        .. [1] Alberty (2006)
        .. [2] Maden (2000)
        .. [3] Thauer (1977)
        .. [4] Wagman (1982)
        .. [5] Dolfing (1992)
        .. [6] Dolfing (1994)
        """

        formation_df = (
            quilt.data.equilibrator.component_contribution.train
            .formation_energies_transformed().copy()
        )

        compounds = formation_df['cid'].apply(ccache.get_compound)

        if pd.isnull(compounds).any():
            missing_cids = formation_df.loc[pd.isnull(compounds), 'cid']
            raise ParseException("Cannot find some of the compounds in the "
                                 "cache: " + str(missing_cids))

        compounds_that_do_not_decompose = set(
            compounds.loc[formation_df['decompose'] == 0].values)

        for col in ["dG'0", "T", "I", "pH", "pMg"]:
            formation_df[col] = formation_df[col].apply(float)

        formation_df = formation_df[~pd.isnull(formation_df["dG'0"])]

        formation_df['reaction'] = compounds.apply(lambda c: Reaction({c: 1}))
        formation_df['balance'] = False
        formation_df['description'] = formation_df['name'] + ' formation'
        formation_df.rename(columns={'compound_ref': 'reference'},
                            inplace=True)
        formation_df.drop(['name', 'cid', 'remark', 'decompose'],
                          axis=1, inplace=True)

        logger.debug('Successfully added %d formation energies' %
                     formation_df.shape[0])
        return formation_df, compounds_that_do_not_decompose

    @staticmethod
    def read_redox() -> pd.DataFrame:
        """
        Read the Reduction potential from literature data [1-8]

        Returns
        -------
        pandas.DataFrame

        References
        ----------
        .. [1] CRC biochemistry (2010)
        .. [2] Prince (1987)
        .. [3] Thauer (1977)
        .. [4] CRC biochemistry (2010)
        .. [5] Alberty (2006)
        .. [6] Deppenmeier (2008)
        .. [7] Saeki (1985)
        .. [8] Unden (1997)
        """
        redox_df = (
            quilt.data.equilibrator.component_contribution.train.redox().copy()
        )

        compounds_ox = redox_df['CID_ox'].apply(ccache.get_compound)
        compounds_red = redox_df['CID_red'].apply(ccache.get_compound)
        reaction = [Reaction({c_ox: -1, c_red: 1})
                    for c_ox, c_red in zip(compounds_ox, compounds_red)]

        delta_nH = redox_df['nH_red'] - redox_df['nH_ox']
        delta_charge = redox_df['charge_red'] - redox_df['charge_ox']
        delta_e = delta_nH - delta_charge
        dG0_prime = -F * redox_df["E'0"] * delta_e

        redox_df = redox_df.assign(
            **{"reaction": reaction,
               "description": redox_df['name'] + ' redox',
               "dG'0": dG0_prime,
               "balance": False}
        )
        redox_df.rename(columns={'ref': 'reference'}, inplace=True)
        redox_df.drop(['name', 'CID_ox', 'CID_red', 'charge_ox', 'charge_red',
                       'nH_ox', 'nH_red', "E'0"], axis=1, inplace=True)

        logger.debug('Successfully added %d redox potentials' %
                     redox_df.shape[0])
        return redox_df

    @staticmethod
    def get_all_thermo_params() -> Tuple[pd.DataFrame, Set[Compound]]:
        tecr_df = FullTrainingData.read_tecrdb()
        tecr_df['weight'] = 1.0

        formation_df, compounds_that_do_not_decompose = \
            FullTrainingData.read_formations()
        formation_df['weight'] = 1.0

        redox_df = FullTrainingData.read_redox()
        redox_df['weight'] = 1.0

        reaction_df = pd.concat([tecr_df, formation_df, redox_df], sort=False)
        reaction_df.reset_index(drop=True, inplace=True)

        # default ionic strength is 0.25M
        reaction_df['I'].fillna(0.25, inplace=True)
        # default pMg is 14
        reaction_df['pMg'].fillna(14, inplace=True)

        reaction_df.rename(columns={"dG'0": 'dG0_prime'}, inplace=True)

        return reaction_df, compounds_that_do_not_decompose
