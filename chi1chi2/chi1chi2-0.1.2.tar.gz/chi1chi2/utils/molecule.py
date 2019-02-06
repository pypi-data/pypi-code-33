import numpy as np
from openbabel import OBElementTable
from scipy.linalg import inv, det

from chi1chi2.utils.constants import Unit, simeq, Symmop, Params

ptable = OBElementTable()
NUMBER_FORMAT = "{: .10f}"


class Atom:
    """
    a simple class representing an atom
    """

    def __init__(self, symbol, x, y, z, charge=0., unit=Unit.Angstr):
        try:
            self.symbol = ptable.GetSymbol(int(symbol))
        except ValueError:
            self.symbol = symbol
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)
        self.charge = float(charge)  # ignored for equals
        self.unit = unit

    def has_charge(self):
        return not simeq(self.charge, 0.)

    @classmethod
    def from_line(cls, line):
        tokens = line.split()
        return cls(*tokens)

    def get_coords(self):
        return (self.x * self.unit.to_angstrom(),
                self.y * self.unit.to_angstrom(),
                self.z * self.unit.to_angstrom())

    def get_atomic_num(self):
        return ptable.GetAtomicNum(self.symbol)

    def to_str(self, atomic_symbol=True, include_chg=False) -> str:
        if atomic_symbol:
            line = self.symbol
        else:
            line = str(ptable.GetAtomicNum(self.symbol))
        line += ' ' + ' '.join(map(NUMBER_FORMAT.format, self.get_coords()))
        if include_chg:
            line += ' ' + NUMBER_FORMAT.format(self.charge)
        return line

    def __str__(self) -> str:
        return self.to_str()

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, Atom):
            return False
        elif self is o:
            return True
        else:
            return self.symbol == o.symbol \
                   and simeq(self.x, o.x) \
                   and simeq(self.y, o.y) \
                   and simeq(self.z, o.z)


class Molecule:
    """
    a molecule model structure
    """

    def __init__(self, atoms: list, params: Params):
        """
        reading from xyz file
        :param atoms: list of atoms
        """
        self.num_atoms = len(atoms)
        self.atoms = atoms
        self.params = params

    def to_str(self, atomic_symbol=True, include_chg=False, include_num_atoms=True, include_params=True) -> str:
        result = ""
        if include_num_atoms:
            result = str(self.num_atoms) + '\n'
        if include_params:
            result += str(self.params) + '\n'
        for i in range(self.num_atoms):
            result += self.atoms[i].to_str(atomic_symbol, include_chg) + '\n'
        return result

    def __repr__(self):
        return self.to_str()

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, Molecule):
            return False
        elif self is o:
            return True
        else:
            return self.num_atoms == o.num_atoms \
                   and self.atoms == o.atoms

    def get_charge(self):
        total_chg = 0.
        for at in self.atoms:
            total_chg += at.charge
        return total_chg

    def cq(self):
        cq = np.zeros((3, 1))
        nuc_chg = 0.
        for atom in self.atoms:
            nuc_chg += atom.get_atomic_num()
            cq += atom.get_atomic_num() * np.array(atom.get_coords()).reshape((3, 1))
        return cq / nuc_chg

    def has_charges_defined(self):
        return any(atom.has_charge() for atom in self.atoms)

    def has_no_charges_defined(self):
        return not self.has_charges_defined()

    def as_fra_molecule(self):
        return FraMolecule(self.atoms, self.params)

    def as_xyz_molecule(self):
        return XyzMolecule(self.atoms, self.params)

    @staticmethod
    def transform(molecule, symmop: Symmop):
        """
        transforms this molecule into a new one
        :param molecule: molecule to be transformed
        :param rotation_matrix: 3D transformation matrix
        :param translation: translation vector
        :return: new molecule object after transformation
        """
        atoms_rotated = []
        for at in molecule.atoms:
            atoms_rotated.append(
                Atom(at.symbol,
                     *(np.dot(symmop.rotation, np.array(at.get_coords()).reshape((3, 1))) + symmop.translation),
                     at.charge))
        return Molecule(atoms_rotated, molecule.params)


class XyzMolecule(Molecule):
    def to_fra_molecule(self):
        return FraMolecule.transform(self, Symmop.no_translation(xyz_to_frac_transf_matrix(self.params))) \
            .as_fra_molecule()


class FraMolecule(Molecule):
    def to_xyz_molecule(self):
        return XyzMolecule.transform(self, Symmop.no_translation(inv(xyz_to_frac_transf_matrix(self.params)))) \
            .as_xyz_molecule()


def xyz_to_frac_transf_matrix(params):
    a, b, c, al, be, ga = params
    G = np.zeros((3, 3))
    G[0, 0] = a ** 2.
    G[1, 1] = b ** 2.
    G[2, 2] = c ** 2.
    G[0, 1] = a * b * np.cos(ga)
    G[0, 2] = a * c * np.cos(be)
    G[1, 2] = b * c * np.cos(al)
    G[1, 0] = G[0, 1]
    G[2, 0] = G[0, 2]
    G[2, 1] = G[1, 2]
    V = np.sqrt(float(det(G)))
    G_pr = inv(G)
    M_xyz_to_frac = np.zeros((3, 3))
    M_xyz_to_frac[0, 0] = 1. / a / np.sin(ga)
    M_xyz_to_frac[1, 0] = -1. / b / np.tan(ga)
    M_xyz_to_frac[1, 1] = 1. / b
    M_xyz_to_frac[:, 2] = V / a / b / np.sin(ga) * G_pr[:, 2]
    return M_xyz_to_frac
