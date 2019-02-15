# The MIT License (MIT)
#
# Copyright (c) 2018 Institute for Molecular Systems Biology, ETH Zurich
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

import numpy as np
from sqlalchemy import Column, Float, Integer, PickleType, String
from sqlalchemy.orm import relationship

from . import Base
from ..exceptions import MissingDissociationConstantsException
from ..thermodynamic_constants import ureg
from .mixins import TimeStampMixin


class Compound(TimeStampMixin, Base):
    """
    Model a chemical compound in the context of component contribution.

    Attributes
    ----------
    id : int
        The primary key in the table.
    mnx_id :
        The MetaNetX serial number of this metabolite.
    inchi_key : str
        InChIKey is a hash of the full InChI with a constant length.
    inchi : str
        InChI descriptor of the molecule.
    smiles : str
        SMILES descriptor of the molecule, taken from MetaNetX but not used.
    mass : float
        Molecualr mass of the molecule.
    atom_bag : dict
        The chemical formula, where keys are the atoms and values are the 
        stoichiometric coefficient.
    dissociation_constants : list
        A list of float, which are the pKa values of this molecule.
    group_vector : list
        A list of groups and their counts
    microspecies : list
        The compound's microspecies in a one-to-many relationship
    identifiers : list
        The compound's identifiers in a one-to-many relationship.

    """

    __tablename__ = "compounds"

    # SQLAlchemy column descriptors.
    id: int = Column(Integer, primary_key=True, autoincrement=True)
    mnx_id: str = Column(String(), default=None, nullable=True, index=True)
    inchi_key: str = Column(String(), default=None, nullable=True, index=True)
    inchi: str = Column(String(), default=None, nullable=True, index=True)
    smiles: str = Column(String(), default=None, nullable=True, index=True)
    mass: float = Column(Float, default=None, nullable=True)
    atom_bag: dict = Column(PickleType, nullable=True)
    dissociation_constants: list = Column(PickleType, nullable=True)
    group_vector: list = Column(PickleType, nullable=True)
    microspecies: list = relationship("CompoundMicrospecies", lazy="selectin")
    identifiers: list = relationship("CompoundIdentifier", lazy="selectin")

    @ureg.check(None, None, "[concentration]", "[temperature]")
    def transform(
        self, p_h: float, ionic_strength: float, temperature: float
    ) -> object:
        """Use the Legendre transform to convert the ddG_over_RT to the
        difference in the transformed energies of the biochemical compound
        and the chemical compound (the major microspecies)

        :param p_h:
        :param ionic_strength:
        :param temperature:
        :return: the transformed relative deltaG (in units of RT)

        """
        if len(self.microspecies) == 0:
            raise MissingDissociationConstantsException(
                "%r has not yet been analyzed by ChemAxon" % str(self)
            )
        if None in self.microspecies:
            raise MissingDissociationConstantsException(
                "%r has not yet been analyzed by ChemAxon" % str(self)
            )

        ddg_over_rt = sorted(
            map(
                lambda ms: -1.0
                * ms.transform(p_h, ionic_strength, temperature),
                self.microspecies,
            )
        )

        total_ddg_over_rt = ddg_over_rt[0]
        for x in ddg_over_rt[1:]:
            total_ddg_over_rt = np.logaddexp(total_ddg_over_rt, x)
        return -total_ddg_over_rt

    def __repr__(self):
        return f"{type(self).__name__}(mnx_id={self.mnx_id})"

    def __lt__(self, other: object) -> bool:
        return self.id < other.id

    def __str__(self) -> str:
        if self.mnx_id:
            return self.mnx_id
        elif self.identifiers:
            return self.identifiers[0].accession
        else:
            return "compound #%d" % self.id

    @property
    def formula(self) -> str:
        if self.atom_bag is None:
            return ""
        tokens = [
            element if count == 1 else f"{element}{count}"
            for element, count in sorted(self.atom_bag.items())
            if count > 0 or element != "e-"
        ]
        return "".join(tokens)
