# The MIT License (MIT)
#
# Copyright (c) 2018 Institute for Molecular Systems Biology, ETH Zurich.
# Copyright (c) 2018 Novo Nordisk Foundation Center for Biosustainability,
# Technical University of Denmark.
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
import re
import sys
from typing import Callable, Dict, Iterable, List, Tuple

import numpy as np
import pandas as pd

from equilibrator_cache.compound_cache import CompoundCache
from equilibrator_cache.exceptions import ParseException
from equilibrator_cache.models import Compound
from equilibrator_cache.thermodynamic_constants import (
    POSSIBLE_REACTION_ARROWS,
    Q_,
    physiological_concentration,
    standard_concentration,
    ureg,
)


class Reaction:

    ccache = CompoundCache()
    PROTON_COMPOUND = ccache.get_compound_from_registry("mnx", "MNXM1")
    WATER_COMPOUND = ccache.get_compound_from_registry("mnx", "MNXM2")

    def __init__(
        self, sparse: Dict[Compound, float], arrow: str = "<=>", rid: str = None
    ) -> object:
        self.sparse = dict([(k, v) for (k, v) in sparse.items() if v != 0])
        self.arrow = arrow
        self.rid = rid

    def keys(self) -> List[Compound]:
        return self.sparse.keys()

    def keys_without_water_and_protons(self):
        return set(self.keys()) - {
            Reaction.WATER_COMPOUND,
            Reaction.PROTON_COMPOUND,
        }

    def items(self) -> Iterable[Tuple[Compound, int]]:
        return self.sparse.items()

    def get_coeff(self, compound: Compound) -> float:
        return self.sparse.get(compound, 0.0)

    def reverse(self) -> object:
        """
            reverse the direction of the reaction by negating all
            stoichiometric coefficients
        """
        sparse = dict((k, -v) for (k, v) in self.sparse.items())
        return Reaction(sparse, self.arrow, self.rid)

    def __eq__(self, other) -> bool:
        cpds = set(self.keys()).union(other.keys())
        for c in cpds:
            if self.get_coeff(c) != other.get_coeff(c):
                return False
        return True

    @staticmethod
    def parse_formula_side(
        s: str, str_to_compound: Callable[[str], Compound]
    ) -> Dict[Compound, float]:
        """
            Parses the side formula, e.g.
            '2 KEGG:C00001 + KEGG:C00002 + 3 KEGG:C00003'
            Ignores stoichiometry.

            Returns:
                The set of CIDs.
        """
        if s.strip() == "null":
            return {}

        compound_bag = {}
        for member in re.split(r"\s+\+\s+", s):
            tokens = member.split(None, 1)
            if len(tokens) == 0:
                continue
            if len(tokens) == 1:
                amount = 1.0
                compound = str_to_compound(member)
            else:
                try:
                    amount = float(tokens[0])
                except ValueError:
                    raise ParseException(f"Non-specific reaction: {s}")
                compound = str_to_compound(tokens[1])

            if compound is None:
                raise ParseException(
                    f"{member} was not found in the " "compound cache"
                )

            compound_bag[compound] = compound_bag.get(compound, 0.0) + amount

        return compound_bag

    @classmethod
    def parse_formula(
        cls,
        formula: str,
        rid: str = None,
        str_to_compound: Callable[[str], Compound] = ccache.get_compound,
    ) -> object:
        """
            Parses a two-sided formula such as: 2 C00001 = C00002 + C00003

            Args:
                formula     - a string representation of the chemical formula
                name_to_cid - (optional) a dictionary mapping names to KEGG IDs

            Return:
                The set of substrates, products and the reaction direction
        """
        tokens = []
        for arrow in POSSIBLE_REACTION_ARROWS:
            if formula.find(arrow) != -1:
                tokens = formula.split(arrow, 2)
                break

        if len(tokens) < 2:
            raise ValueError(
                "Reaction does not contain an allowed arrow sign:"
                " %s" % (arrow, formula)
            )

        left = tokens[0].strip()
        right = tokens[1].strip()

        sparse_reaction = {}
        left_dict = Reaction.parse_formula_side(left, str_to_compound)
        right_dict = Reaction.parse_formula_side(right, str_to_compound)
        for cid, count in left_dict.items():
            sparse_reaction[cid] = sparse_reaction.get(cid, 0) - count

        for cid, count in right_dict.items():
            sparse_reaction[cid] = sparse_reaction.get(cid, 0) + count

        # remove compounds that are balanced out in the reaction,
        # i.e. their coefficient is 0
        sparse_reaction = dict(
            filter(lambda x: x[1] != 0, sparse_reaction.items())
        )
        return cls(sparse_reaction, arrow=arrow, rid=rid)

    @staticmethod
    def write_compound_and_coeff(compound: Compound, coeff: float) -> str:
        if np.abs(coeff - 1) < sys.float_info.epsilon:
            return str(compound)
        else:
            return "%g %s" % (coeff, str(compound))

    def __str__(self) -> str:
        """String representation."""
        left = []
        right = []
        for compound, coeff in sorted(self.sparse.items()):
            if coeff < 0:
                left.append(Reaction.write_compound_and_coeff(compound, -coeff))
            elif coeff > 0:
                right.append(Reaction.write_compound_and_coeff(compound, coeff))
        return "%s %s %s" % (" + ".join(left), self.arrow, " + ".join(right))

    def _get_element_data_frame(self) -> pd.DataFrame:
        """Create a dataframe containing the elemental composition of all
        the reactants in this reaction

        Returns:
            element_df : pd.DataFrame
                A dataframe, where the columns are the compounds and the
                indexes are elements.
        """
        compounds = list(self.keys())

        # gather the "atom bags" of all compounds in a list 'atom_bag_list'
        atom_bags = {}
        for compound in compounds:
            if compound == Reaction.PROTON_COMPOUND:
                atom_bags[compound] = {"H": 1}
            elif compound.atom_bag is not None:
                atom_bags[compound] = compound.atom_bag
            else:
                atom_bags[compound] = {}

        # create the elemental matrix, where each row is a compound and each
        # column is an element (or e-)
        element_df = pd.DataFrame.from_dict(
            atom_bags, orient="columns", dtype=int
        ).fillna(0)
        return element_df

    def _get_reaction_atom_bag(
        self, raise_exception: bool = False
    ) -> Dict[str, int]:
        """
            Use for checking if all elements are conserved.

            Returns:
                An atom_bag of the differences between the sides of the
                reaction. E.g. if there is one extra C on the left-hand
                side, the result will be {'C': -1}.
        """
        element_df = self._get_element_data_frame()

        if np.any((element_df == 0).all(axis=0)):
            warning_str = (
                "cannot generate the reaction atom bag because "
                + "compounds have unspecific formulas: "
                + "%s" % str(self)
            )
            if raise_exception:
                raise ValueError(warning_str)
            else:
                logging.warning(warning_str)
                return None

        stoichiometry = np.array(list(element_df.columns.map(self.get_coeff)))
        unbalanced = element_df @ stoichiometry
        unbalanced = unbalanced[unbalanced != 0]
        atom_bag = unbalanced.to_dict()

        if len(atom_bag) > 0:
            logging.debug("unbalanced reaction: %s" % str(self))
            for elem, imbalance in atom_bag.items():
                logging.debug(
                    "there are %d more %s atoms on the "
                    "right-hand side" % (imbalance, elem)
                )

        return atom_bag

    def is_balanced(
        self,
        fix_protons: bool = True,
        fix_water: bool = False,
        raise_exception: bool = False,
    ) -> bool:
        reaction_atom_bag = self._get_reaction_atom_bag(
            raise_exception=raise_exception
        )

        if reaction_atom_bag is None:
            # this means some compound formulas are missing
            return False

        for fix_flag, atom, cpd in [
            (fix_water, "O", Reaction.WATER_COMPOUND),
            (fix_protons, "H", Reaction.PROTON_COMPOUND),
        ]:
            if fix_flag and (atom in reaction_atom_bag):
                self.sparse[cpd] = (
                    self.sparse.setdefault(cpd, 0) - reaction_atom_bag[atom]
                )
                reaction_atom_bag = self._get_reaction_atom_bag()

        return len(reaction_atom_bag) == 0

    def is_empty(self):
        return len(self.sparse) == 0

    def dense(self, cids):
        s = np.zeros((len(cids), 1))
        for cid, coeff in self.items():
            s[cids.index(cid), 0] = coeff
        return s

    @ureg.check(None, None, "[concentration]", "[temperature]")
    def transform(
        self, p_h: float, ionic_strength: float, temperature: float
    ) -> float:
        """Use the Legendre transform to convert the ddG_over_RT to the
        difference in the transformed energies of this MS and the major MS

        :param p_h:
        :param ionic_strength:
        :param temperature:
        :return: the transformed relative deltaG (in units of RT)
        """
        ddg_over_rt = Q_(0.0)
        for compound, coeff in self.items():
            if compound == Reaction.PROTON_COMPOUND:
                continue  # H+ is ignored in the Legendre transform
            ddg_over_rt += coeff * compound.transform(
                p_h, ionic_strength, temperature
            )
        return ddg_over_rt

    def dg_correction(self, compound_to_conc: Dict[Compound, float]) -> float:
        """
            Calculate the concentration adjustment in the dG' of reaction.
            Arguments:
                compound_to_conc - a dictionary mapping Compound objects
                                   to concentration in M (default is 1M)

            Returns:
                ddg_over_rt - correction for delta G in units of RT
        """
        ddg_over_rt = Q_(0.0)
        for compound in self.keys_without_water_and_protons():
            if compound in compound_to_conc:
                assert compound_to_conc[compound].check("[concentration]")

                ddg_over_rt += self.get_coeff(compound) * np.log(
                    compound_to_conc[compound] / standard_concentration
                )

        return ddg_over_rt

    def _GetSumCoeff(self) -> float:
        """
            Calculate the sum of all coefficients (excluding water).
            This is useful for shifting the dG'0 to another set of standard
            concentrations (e.g. 1 mM)
        """
        sum_coeff = sum(
            map(self.get_coeff, self.keys_without_water_and_protons())
        )
        return sum_coeff

    def _GetAbsSumCoeff(self) -> float:
        """
            Calculate the sum of all coefficients (excluding water) in
            absolute value.
            This is useful for calculating the reversibility index.
        """
        abs_sum_coeff = sum(
            map(
                lambda cid: abs(self.get_coeff(cid)),
                self.keys_without_water_and_protons(),
            )
        )
        return abs_sum_coeff

    def physiological_dg_correction(self) -> float:
        """
            Calculate the concentration adjustment in the dG' of reaction
            assuming all reactants are in the default physiological
            concentrations (i.e. 1 mM)

            Returns:
                ddg_over_rt - correction for delta G in units of RT
        """
        return self._GetSumCoeff() * np.log(
            physiological_concentration / standard_concentration
        )

    def check_half_reaction_balancing(self):
        """
            Returns:
                The number of electrons that are 'missing' in the half-reaction
                or None if the reaction is not atomwise-balanced.
        """
        atom_bag = self._get_reaction_atom_bag()
        if atom_bag is None:
            return None

        atom_bag.pop("H")

        n_e = atom_bag.pop("e-", 0)
        if len(atom_bag) > 0:
            return None
        else:
            return n_e


def create_stoichiometric_matrix_from_reactions(
    reactions: Iterable[Reaction]
) -> pd.DataFrame:
    """
        Builds a stoichiometric matrix.

    Returns:
        the stoichiometric matrix S as a DataFrame, whose indexes are the
        compounds and its columns are the reactions (in the same order as
        the input).
    """
    S = (
        pd.DataFrame.from_records(map(lambda r: r.sparse, reactions))
        .fillna(0)
        .T
    )

    # now get rid of the protons, since we are applying Alberty's
    # framework where their potential is set to 0, and the pH is held
    # as a controlled parameter
    if Reaction.PROTON_COMPOUND in S.index:
        S.drop(Reaction.PROTON_COMPOUND, axis=0, inplace=True)
    if Reaction.WATER_COMPOUND not in S.index:
        S.loc[Reaction.WATER_COMPOUND, :] = 0

    return S
