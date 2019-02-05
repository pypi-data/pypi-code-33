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
from collections import namedtuple
from os.path import join
from typing import Dict, List, Tuple

import numpy as np
import quilt

from equilibrator_cache import Q_, R, ureg

from . import Compound, Reaction, ccache
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
            self.params = GibbsEnergyPredictor.quilt_fetch()
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

    def quilt_install(self) -> None:
        quilt.install(GibbsEnergyPredictor.QUILT_PKG, force=True)

    def quilt_build(self) -> None:
        for k, v in self.params._asdict().items():
            quilt.build(join(GibbsEnergyPredictor.QUILT_PKG, "parameters", k),
                        v)

    def quilt_push(self) -> None:
        quilt.push(GibbsEnergyPredictor.QUILT_PKG, is_public=True)

    @staticmethod
    def quilt_fetch() -> CCModelParameters:
        try:
            pkg = quilt.load(GibbsEnergyPredictor.QUILT_PKG)
        except quilt.tools.command.CommandException:
            raise Exception("Quilt package is not installed, please run "
                            "'quilt install " +
                            GibbsEnergyPredictor.QUILT_PKG + "'")

        param_dict = {k: v() for k, v in pkg.parameters._children.items()}
        return CCModelParameters(**param_dict)

    def get_major_ms_standard_dg_formation(self, compound: Compound) -> float:
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

                total_gv += coeff * gv.AsVector().as_array()

        return x, total_gv

    def dg_analysis(
        self,
        reaction: Reaction,
        raise_exception: bool = False
    ) -> List[Dict[str, object]]:
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

    def is_using_group_contribution(
        self,
        reaction: Reaction,
        raise_exception: bool = False
    ) -> bool:
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
        weights_gc = x @ G2 + g @ G3[0:self.Ng, :]
        sum_w_gc = sum(abs(weights_gc).flat)
        logging.info('sum(w_gc) = %.2g' % sum_w_gc)
        return sum_w_gc > 1e-5

    def standard_dg_multi(
        self,
        reactions: List[Reaction],
        raise_exception: bool = False
    ) -> Tuple[np.array, np.array]:
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

        dG0 = Q_(dG0, "kJ/mol")
        U = Q_(U, "(kJ/mol)**2")
        return dG0, U

    @ureg.check(None, None, None, '[concentration]', '[temperature]', None)
    def standard_dg_prime_multi(
        self,
        reactions: List[Reaction],
        p_h: float,
        ionic_strength: float,
        temperature: float,
        raise_exception: bool = False
    ) -> Tuple[np.array, np.array]:
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
        standard_dg, U = self.standard_dg_multi(reactions, raise_exception)

        for i, r in enumerate(reactions):
            standard_dg[i] += R * temperature * \
                              r.transform(p_h, ionic_strength, temperature)

        return standard_dg, U

    def standard_dg(
        self,
        reaction: Reaction,
        raise_exception: bool = False
    ) -> Tuple[float, float]:
        """Calculate the chemical reaction energy, using the major microspecies
        of each of the reactants.

        :param reaction: the input Reaction object
        :param raise_exception: flag for non-decomposable compounds
        :return: a tuple with the CC estimation of the major microspecies'
        standard formation energy, and the uncertainty
        """
        try:
            dG0_cc, U = self.standard_dg_multi([reaction], raise_exception=True)
            dG0_cc = dG0_cc[0]
            sigma_cc = np.sqrt(U[0, 0])
        except GroupDecompositionError as exception:
            if raise_exception:
                raise exception
            else:
                return 0, np.sqrt(self.MSE_inf)

        return dG0_cc, sigma_cc

    @ureg.check(None, None, None, 'molar', 'kelvin', None)
    def standard_dg_prime(
        self,
        reaction: Reaction,
        p_h: float,
        ionic_strength: float,
        temperature: float,
        raise_exception=False
    ) -> Tuple[float, float]:
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
        try:
            dG0_cc, U = self.standard_dg_prime_multi(
                [reaction], p_h=p_h, ionic_strength=ionic_strength,
                temperature=temperature, raise_exception=True
            )
            dG0_cc = dG0_cc[0]
            sigma_cc = np.sqrt(U[0, 0])
        except GroupDecompositionError as exception:
            if raise_exception:
                raise exception
            else:
                return 0, np.sqrt(self.MSE_inf)

        return dG0_cc, sigma_cc
