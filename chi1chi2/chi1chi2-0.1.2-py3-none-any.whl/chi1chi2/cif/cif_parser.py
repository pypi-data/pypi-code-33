import re

from CifFile import ReadCif

from chi1chi2.input.input_preparator import Input
from chi1chi2.utils.constants import Params, Symmop, PI, ChiException
from chi1chi2.utils.molecule import Atom, FraMolecule
from chi1chi2.utils.molecule_reorderer import get_molecules_by_groups, get_groups

NUMBER_STD_PATT = re.compile(r"(-?\d+\.?\d+)(?:\(\d+\))?")
ATOM_LABEL_PATT = re.compile(r"(\D+)(?:.*)")


def escape_stdev(value):
    res = NUMBER_STD_PATT.search(value)
    if res is None:
        print("warning: no standard dev found")
        return value
    return res.group(1)


def escape_atomic_symbol(value):
    res = ATOM_LABEL_PATT.search(value)
    if res is None:
        raise ChiException("wrong format of input when escaping atomic label")
    return res.group(1)


class Cif:
    def __init__(self, cif, keys):
        self.cif = cif
        self.keys = keys

    @classmethod
    def from_file(cls, file_name):
        cif = ReadCif(file_name)
        first_key = cif.keys()[0]  # only first structure in the cif
        cif = cif[first_key]
        keys = cif.keys()
        return cls(cif, keys)

    def _get_prop_by_key(self, key):
        return self.cif[key]

    def _get_prop_by_key_ending(self, key_ending):
        return self.cif[self._get_key_ending_with(key_ending)]

    def _get_loop_by_key(self, key):
        return self.cif.GetLoop(key)

    def get_symmops(self):
        keys = ["operation_xyz", "pos_as_xyz"]
        symmop_key = None
        ind = 0
        while symmop_key is None:
            symmop_key = self._get_key_ending_with(keys[ind])
            ind += 1
        if symmop_key is None:
            raise ChiException("symmop key not found, consider adding a new one")
        symmop_list = list(self._get_loop_by_key(symmop_key))
        if len(symmop_list[0]) > 1:
            ind = len(symmop_list[0]) - 1
            symmop_list = [symmop[ind] for symmop in symmop_list]
        else:
            symmop_list = [symmop[0] for symmop in symmop_list]
        symmop_list = [Symmop.from_line(line) for line in symmop_list]
        return symmop_list

    def get_params(self):
        len_keys = ["length_a", "length_b", "length_c"]
        ang_keys = ["angle_alpha", "angle_beta", "angle_gamma"]
        params = []
        for key in len_keys:
            params.append(float(escape_stdev(self._get_prop_by_key_ending(key))))
        for key in ang_keys:
            params.append(float(escape_stdev(self._get_prop_by_key_ending(key))) * PI / 180)
        return Params(*params)

    def _get_key_ending_with(self, ending):
        return next((key for key in self.keys if key.endswith(ending)), None)

    def get_atoms(self):
        atom_symbols = [escape_atomic_symbol(u).strip("()") for u in self._get_prop_by_key_ending("site_label")]
        x_coords = [escape_stdev(u) for u in self._get_prop_by_key_ending("fract_x")]
        y_coords = [escape_stdev(u) for u in self._get_prop_by_key_ending("fract_y")]
        z_coords = [escape_stdev(u) for u in self._get_prop_by_key_ending("fract_z")]
        atoms = []
        for i in range(len(atom_symbols)):
            atoms.append(Atom(atom_symbols[i], x_coords[i], y_coords[i], z_coords[i]))
        return atoms

    def get_fra_mol(self) -> FraMolecule:
        return FraMolecule(self.get_atoms(), self.get_params())

    def get_input(self) -> Input:
        symmops = self.get_symmops()
        xyz_pre_molecule = self.get_fra_mol().to_xyz_molecule()
        xyz_pre_molecules = get_molecules_by_groups(xyz_pre_molecule)
        fra_molecules = [xyz_mol.to_fra_molecule() for xyz_mol in xyz_pre_molecules]
        groups = get_groups(xyz_pre_molecule)

        flags = [[True for i in range(len(symmops))] for j in range(len(fra_molecules))]

        return Input(self.get_params(), flags, symmops, fra_molecules, groups)
