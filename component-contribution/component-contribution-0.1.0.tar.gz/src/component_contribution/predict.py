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

import gzip
import json
import logging
from collections import namedtuple
from os.path import join
from typing import Dict, List, Tuple

import numpy as np
import quilt

from . import Compound, Reaction, ccache, default_T
from .group_decompose import GroupDecomposer, GroupDecompositionError
from .molecule import Molecule, OpenBabelError


logger = logging.getLogger(__name__)

CCModelParameters = namedtuple("CCModelParameters",
                               "train_b train_S train_w train_G "
                               "dG0_rc dG0_gc dG0_cc cov_dG0 "
                               "V_rc V_gc V_inf MSE "
                               "P_R_rc P_R_gc P_N_rc P_N_gc "
                               "inv_S inv_GS inv_SWS inv_GSWGS "
                               "G1 G2 G3 "
                               "preprocess_v_r preprocess_v_g "
                               "preprocess_G1 preprocess_G2 preprocess_G3 "
                               "preprocess_S preprocess_S_count "
                               "preprocess_C1 preprocess_C2 preprocess_C3")

class GibbsEnergyPredictor(object):

    QUILT_PKG = "equilibrator/component_contribution"

    def __init__(self, parameters: CCModelParameters = None) -> object:
        """

        :rtype: object
        """
        if parameters is None:
            try:
                pkg = quilt.load(GibbsEnergyPredictor.QUILT_PKG)
            except quilt.tools.command.CommandException:
                raise Exception("Quilt package is not installed, please run "
                                "'quilt install " +
                                GibbsEnergyPredictor.QUILT_PKG + "'")

            param_dict = {k: v() for k, v in pkg.parameters._children.items()}
            self.params = CCModelParameters(**param_dict)
        else:
            self.params = parameters

        self.decomposer = GroupDecomposer()

        # store the number of "real" groups, i.e. not including the "fake"
        # ones that are placeholders for undecomposable compounds
        self.Ng = len(self.decomposer.groups_data.GetGroupNames())

        # the total number of groups ("real" and "fake")
        self.Nc, self.Ng_full = self.params.train_G.shape

        self._compound_ids = self.params.train_G.index.tolist()

        self.MSE_inf = self.params.MSE.at['inf', 'MSE']

    def get_compound_index(self, compound: Compound) -> int:
        if compound.id in self._compound_ids:
            return self._compound_ids.index(compound.id)
        else:
            return None

    def get_compound(self, i: int) -> Compound:
        return ccache.get_compound_by_internal_id(self._compound_ids[i])

    def quilt_push(self):
        quilt.install(GibbsEnergyPredictor.QUILT_PKG)

        for k, v in self.params._asdict().items():
            quilt.build(join(GibbsEnergyPredictor.QUILT_PKG, "parameters", k),
                        v)

        quilt.push(GibbsEnergyPredictor.QUILT_PKG, is_public=True)

    def get_major_ms_dG0_f(self, compound: Compound) -> float:
        """
            Calculate the chemical formation energy of the major MS at pH 7.
            If the compound is part of the training set, returns the value
            that was calculated during training. Otherwise, we use pure
            group contribution (if possible) on the groups of the major MS.

            :param compound_id: the compound ID
            :return: the standard formation energy of the major microspecies
        """
        if self.params is None:
            self.train()

        i = self.get_compound_index(compound)
        if i is not None:
            return self.params.dG0_cc[i, 0]
        else:
            # Decompose the compound and calculate the 'formation energy'
            # using the group contributions.
            # Note that the length of the group contribution vector we get
            # from CC is longer than the number of groups in "groups_data"
            # since we artificially added fictive groups to represent all the
            # non-decomposable compounds. Therefore, we truncate the
            # dG0_gc vector since here we only use GC for compounds which
            # are not in CIDs anyway.
            try:
                mol = Molecule.FromCompound(compound)
                group_vec = self.Decompose(mol)
                g = group_vec.AsVector().as_array()
                return g @ self.params.dG0_gc[0:self.Ng]
            except OpenBabelError:
                return np.nan
            except GroupDecompositionError:
                return np.nan

    def _decompose_reaction(self, reaction: Reaction, raise_exception: bool = True
                            ) -> Tuple[np.array, np.array]:
        """Calculate the reaction stoichiometric vector and the group
        incidence vector (x and g)

        :param reaction: the input Reaction object
        :param raise_exception: flag for non-decomposable compounds
        :return: a tuple of the stoichiometric and group vectors
        """
        x = np.zeros(self.Nc)
        total_gv = np.zeros(self.Ng)

        for compound, coeff in reaction.items():
            i = self.get_compound_index(compound)
            if i is not None:
                x[i] = coeff
            else:
                # Decompose the compound and calculate the 'formation energy'
                # using the group contributions.
                # Note that the length of the group contribution vector we get
                # from CC is longer than the number of groups in "groups_data"
                # since we artifically added fictive groups to represent all
                # the non-decomposable compounds. Therefore, we truncate the
                # dG0_gc vector since here we only use GC for compounds which
                # are not in CIDs anyway.
                try:
                    mol = Molecule.FromCompound(compound)
                except OpenBabelError as exception:
                    if raise_exception:
                        logger.warning('Compound %s has a SMILES string that '
                                       'cannot be parsed properly and '
                                       'is also not in the training set'
                                       % str(compound))
                        raise exception
                    else:
                        return np.zeros(self.Nc), np.zeros(self.Ng)

                try:
                    gv = self.decomposer.Decompose(mol)
                except GroupDecompositionError as exception:
                    if raise_exception:
                        logger.warning('Compound %s cannot be decomposed and '
                                       'is also not in the training set'
                                       % str(compound))
                        raise exception
                    else:
                        return np.zeros(self.Nc), np.zeros(self.Ng)

                total_gv += gv.AsVector().as_array()

        return x, total_gv

    def get_dG0_r(self, reaction: Reaction, raise_exception: bool = False
                  ) -> Tuple[float, float]:
        """Calculate the chemical reaction energy, using the major microspecies
        of each of the reactants.

        :param reaction: the input Reaction object
        :param raise_exception: flag for non-decomposable compounds
        :return: a tuple with the CC estimation of the major microspecies'
        standard formation energy, and the uncertainty
        """
        try:
            dG0_cc, U = self.get_dG0_r_multi([reaction], raise_exception=True)
            dG0_cc = dG0_cc[0]
            sigma_cc = np.sqrt(U[0, 0])
        except GroupDecompositionError as exception:
            if raise_exception:
                raise exception
            else:
                return 0, np.sqrt(self.MSE_inf)

        return dG0_cc, sigma_cc

    def get_dG0_r_analysis(self, reaction: Reaction,
                           raise_exception: bool = False) -> List[Dict[str,
                                                                       object]]:
        """Analyse the contribution of each training observation to this
        reaction's dG0 estimate.

        :param reaction: the input Reaction object
        :param raise_exception: flag for non-decomposable compounds
        :return: a list of reactions that contributed to the value of the dG0
        estimation, with their weights and extra information
        """
        G1 = self.params.preprocess_G1
        G2 = self.params.preprocess_G2
        G3 = self.params.preprocess_G3
        S = self.params.preprocess_S
        S_count = self.params.preprocess_S_count

        try:
            x, g = self._decompose_reaction(reaction)
        except GroupDecompositionError as exception:
            if raise_exception:
                raise exception
            else:
                return None

        # dG0_cc = (x*G1 + x*G2 + g*G3)*b
        weights_rc = (x @ G1).round(5)
        weights_gc = (x @ G2 + g @ G3[0:self.Ng, :]).round(5)
        weights = weights_rc + weights_gc

        orders = sorted(range(weights.shape[0]),
                        key=lambda j: abs(weights[j]), reverse=True)

        analysis = []
        for j in orders:
            if abs(weights[j]) < 1e-5:
                continue
            r = Reaction(
                {self.get_compound(i): S[i, j]
                 for i in range(S.shape[0])
                 if S[i, j] != 0}
            )
            analysis.append({'index': j,
                             'w_rc': weights_rc[j],
                             'w_gc': weights_gc[j],
                             'reaction': r,
                             'count': int(S_count[j])})

        return analysis

    def is_using_group_contribution(self, reaction: Reaction,
                                    raise_exception: bool = False) -> bool:
        """Check if group contributions are required to estimate the Gibbs
        energy of this reaction

        :param reaction: the input Reaction object
        :param raise_exception: flag for non-decomposable compounds
        :return: boolean answer
        """
        try:
            x, g = self._decompose_reaction(reaction)
        except GroupDecompositionError as exception:
            if raise_exception:
                raise exception
            else:
                return None

        G2 = self.params.preprocess_G2
        G3 = self.params.preprocess_G3
        weights_gc = x.T * G2 + g.T * G3
        sum_w_gc = sum(abs(weights_gc).flat)
        logging.info('sum(w_gc) = %.2g' % sum_w_gc)
        return sum_w_gc > 1e-5

    def get_dG0_r_multi(self, reactions: List[Reaction],
                        raise_exception: bool = False) -> Tuple[np.array,
                                                                np.array]:
        """Calculate the chemical reaction energies for a list of reactions,
        using the major microspecies of each of the reactants.

        :param reactions: a list of Reaction objects
        :param raise_exception: flag for non-decomposable compounds
        :return: a tuple of two arrays. the first is a 1D NumPy array
        containing the CC estimates for the reactions' untransformed dG0
        (i.e. using the major MS at pH 7 for each of the reactants).
        the second is a 2D numpy array containing the covariance matrix
        of the standard errors of the estimates. one can use the eigenvectors
        of the matrix to define a confidence high-dimensional space, or use
        U as the covariance of a Gaussian used for sampling
        (where dG0_cc is the mean of that Gaussian).
        """
        Nr = len(reactions)
        X = np.zeros((self.Nc, Nr))
        G = np.zeros((self.Ng_full, Nr))
        for i, reaction in enumerate(reactions):
            x, g = self._decompose_reaction(reaction,
                                            raise_exception=raise_exception)
            X[:, i] = x
            G[:self.Ng, i] = g

        v_r = self.params.preprocess_v_r
        v_g = self.params.preprocess_v_g
        C1 = self.params.preprocess_C1
        C2 = self.params.preprocess_C2
        C3 = self.params.preprocess_C3

        dG0 = X.T @ v_r + G.T @ v_g
        U = X.T @ C1 @ X + X.T @ C2 @ G + G.T @ C2.T @ X + G.T @ C3 @ G
        return dG0, U

    def get_dG0_r_prime(self, reaction: Reaction, pH: float,
                        ionic_strength: float, T: float,
                        raise_exception=False) -> Tuple[float, float]:
        """Calculate the transformed reaction energies of a reaction.

        :param reaction: the input Reaction object
        :param pH:
        :param ionic_strength: in M
        :param T: temperature in Kalvin
        :param raise_exception: flag for non-decomposable compounds
        :return: a tuple of the dG0_prime in kJ/mol and standard error. to
        calculate the confidence interval, use the range -1.96 to 1.96 times
        this value
        """
        dG0_cc, sigma_cc = self.get_dG0_r(reaction, raise_exception)
        dG0_prime = dG0_cc + reaction.get_transform_ddG0(pH, ionic_strength, T)
        return dG0_prime, sigma_cc

    def get_dG0_r_prime_multi(self, reactions: List[Reaction],
                              pH: float, ionic_strength: float, T: float,
                              raise_exception: bool = False) -> Tuple[np.array, np.array]:
        """Calculate the transformed reaction energies of a list of reactions.

        :param reactions: a list of Reaction objects
        :param pH:
        :param ionic_strength: in M
        :param T: temperature in Kalvin
        :param raise_exception: flag for non-decomposable compounds
        :return: a tuple of two arrays. the first is a 1D NumPy array
        containing the CC estimates for the reactions' transformed dG0
        the second is a 2D numpy array containing the covariance matrix
        of the standard errors of the estimates. one can use the eigenvectors
        of the matrix to define a confidence high-dimensional space, or use
        U as the covariance of a Gaussian used for sampling
        (where dG0_cc is the mean of that Gaussian).
        """
        dG0, U = self.get_dG0_r_multi(reactions, raise_exception)
        ddG0 = np.array([r.get_transform_ddG0(pH, ionic_strength, T)
                         for r in reactions])
        dG0_prime = dG0 + ddG0
        return dG0_prime, U

    def to_dict(self, compound: Compound) -> Dict[str, object]:
        """adds the component-contribution estimation to the JSON

        :param compound_id:
        :return: A dictionary for adding to the JSON file
        """
        if compound is None:
            raise ValueError('given compound ID is None')
        if self.params is None:
            self.train()

        d = {'compound_id': compound.id,
             'inchi_key': compound.inchi_key}
        gv = None

        i = self.get_compound_index(compound)
        if i is not None:
            gv = self.params.train_G[i, :]
            major_ms_dG0_f = self.params.dG0_cc[i]
            d['compound_index'] = i
        elif compound.smiles is not None:
            # decompose the compounds in the training_data and add to G
            try:
                mol = Molecule.FromCompound(compound)
                group_def = self.decomposer.Decompose(mol)
                gv = group_def.AsVector().as_array()
                # we need to truncate the dG0_gc matrix from all the group
                # dimensions that correspond to non-decomposable compounds
                # from the training set
                dG0_gc = self.params.dG0_gc[0:self.Ng]
                major_ms_dG0_f = float(gv @ dG0_gc)
            except OpenBabelError:
                d['error'] = ('We cannot estimate the formation energy of '
                              'this compound because its structure cannot be'
                              'read by OpenBabel')
                major_ms_dG0_f = np.nan
            except GroupDecompositionError:
                d['error'] = ('We cannot estimate the formation energy of '
                              'this compound because its structure is too '
                              'small or too complex to decompose to groups')
                major_ms_dG0_f = np.nan
        else:
            d['error'] = ('We cannot estimate the formation energy of this '
                          'compound because it has no defined structure')
            major_ms_dG0_f = np.nan

        if gv is not None:
            sparse_gv = [(i, int(g)) for (i, g) in enumerate(gv.flat)
                         if g != 0]
            d['group_vector'] = sparse_gv

        if not np.isnan(major_ms_dG0_f):
            _species = list(compound.get_species(major_ms_dG0_f, default_T))
            d['pmap'] = {'source': 'Component Contribution (2013)',
                         'species': _species}

        d['num_electrons'] = compound.atom_bag.get('e-', 0)

        if compound.inchi is not None:
            d['InChI'] = compound.inchi
            try:
                mol = Molecule.FromInChI(compound.inchi)
                d['mass'] = mol.GetExactMass()
                d['formula'] = mol.GetFormula()
            except OpenBabelError:
                # an exception for hydrogen, due to a bug in KEGG
                if compound == ccache.get_compound('KEGG:C00282'):
                    d['mass'] = 2.0157
                    d['formula'] = 'H2'
                else:
                    d['mass'] = 0
                    d['formula'] = ''

        return d

    def to_json(self, json_file_name: str) -> None:
        """write the JSON file containing the 'additiona' data on all the
        compounds in eQuilibrator (i.e. formula, mass, pKa values, etc.)

        :param json_file_name: path to the parameter .json.gz file
        :return:
        """
        compound_json = []
        for i, compound_id in enumerate(ccache.get_all_kegg_compounds()):
            logger.debug("exporting " + compound_id)

            # skip compounds that cause a segmentation fault in openbabel
            if compound_id in ['KEGG:C09078', 'KEGG:C09093', 'KEGG:C09145',
                               'KEGG:C09246', 'KEGG:C10282', 'KEGG:C10286',
                               'KEGG:C10356', 'KEGG:C10359', 'KEGG:C10396',
                               'KEGG:C16818', 'KEGG:C16839', 'KEGG:C16857']:
                continue
            d = self.to_dict(compound_id)
            # override H2O as liquid phase only
            if compound_id in ['KEGG:C00001']:
                d['pmap']['species'][0]['phase'] = 'liquid'
            # override Sulfur as solid phase only
            if compound_id in ['KEGG:C00087']:
                d['pmap']['species'][0]['phase'] = 'solid'
            # add gas phase for O2 and N2
            if compound_id in ['KEGG:C00007', 'KEGG:C00697']:
                d['pmap']['species'].append({'phase': 'gas', 'dG0_f': 0})
            # add gas phase for H2
            if compound_id in ['KEGG:C00282']:
                d['pmap']['species'].append({'phase': 'gas',
                                             'dG0_f': 0,
                                             'nH': 2})
            # add gas phase for CO2
            if compound_id in ['KEGG:C00011']:
                d['pmap']['species'].append({'phase': 'gas',
                                             'dG0_f': -394.36})
            # add gas phase for CO
            if compound_id in ['KEGG:C00237']:
                d['pmap']['species'].append({'phase': 'gas',
                                             'dG0_f': -137.17})

            compound_json.append(d)

        json_bytes = json.dumps(compound_json, sort_keys=True, indent=4)
        with gzip.open(json_file_name, 'w') as new_json:
            new_json.write(json_bytes.encode('utf-8'))
