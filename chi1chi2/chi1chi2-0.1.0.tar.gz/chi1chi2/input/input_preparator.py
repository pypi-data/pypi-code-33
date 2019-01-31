import copy

import numpy as np

from chi1chi2.utils.constants import Symmop, Params, ChiException
from chi1chi2.utils.molecule import Molecule, FraMolecule, XyzMolecule, Atom, NUMBER_FORMAT
from chi1chi2.utils.molecule_reader_writer import read_atoms_params_from_lines_list
from chi1chi2.utils.molecule_reorderer import get_molecule_with_generated_charges, get_groups, group_by_charge, \
    reorder_and_group_by_charge

R_MAX = 200.
LOR_TOL = 1e-5


class Input:
    def __init__(self, params, flags, symmops, fra_molecules, asym_groups):
        self.params = params
        self.flags = flags
        self.num_molecules = len(flags)
        self.symmops = symmops
        # add charges when not found and display warning
        if all(fra_molecule.has_no_charges_defined() for fra_molecule in fra_molecules):
            print("WARNING: charges not found in the input - generating")
            fra_molecules = [get_molecule_with_generated_charges(fra_molecule.to_xyz_molecule()).to_fra_molecule() for
                             fra_molecule in fra_molecules]
        self.fra_molecules = fra_molecules
        self.asym_groups = asym_groups

    @classmethod
    def from_file(cls, file):
        with open(file) as f:
            lines = f.readlines()
        params = Params.from_line(lines[0].strip())
        molecules_number, symmop_number = (int(u) for u in lines[1].split()[:2])
        current_line = 2
        transform_flags = []
        for i in range(molecules_number):
            flag_line = lines[current_line]
            transform_flags.append(
                [True if int(u) == 1 else False for u in flag_line.split()[:symmop_number]])
            current_line += 1
        symmops = []
        for i in range(symmop_number):
            symmops.append(Symmop.from_line(lines[current_line]))
            if i == 0:
                if symmops[0] != Symmop.identity():
                    raise ChiException("first transformation should be identity: " + Symmop.identity().to_line())
            current_line += 1
        fra_molecules = []
        tot_atoms = []
        for i in range(molecules_number):
            atoms_number = int(lines[current_line].split()[0])
            current_fra_molecule = FraMolecule(*read_atoms_params_from_lines_list(
                [lines[current_line], str(params), *lines[current_line + 1: current_line + 1 + atoms_number]]))
            fra_molecules.append(current_fra_molecule)
            current_line += atoms_number + 1
            tot_atoms.extend(fra_molecules[-1].atoms)
        groups = get_groups(FraMolecule(tot_atoms, params).to_xyz_molecule())
        return cls(params, transform_flags, symmops, fra_molecules, groups)

    def get_fra_supermolecule(self, flags) -> FraMolecule:
        fra_supermolecule_atoms = []
        for cur_molecule in range(self.num_molecules):
            for cur_symmop in range(len(self.symmops)):
                if flags[cur_molecule][cur_symmop]:
                    transformed = Molecule.transform(self.fra_molecules[cur_molecule], self.symmops[cur_symmop])
                    translation = np.array([-round(transformed.cq()[i, 0]) for i in range(3)]).reshape((3, 1))
                    transformed = Molecule.transform(transformed, Symmop.only_translation(translation))
                    fra_supermolecule_atoms.extend(transformed.atoms)
        fra_supermolecule = FraMolecule(fra_supermolecule_atoms, self.params)
        return fra_supermolecule

    def for_lorentz(self):
        lines = [str(self.params)]
        xyz_supermolecule = self.get_fra_supermolecule(self.flags).to_xyz_molecule()
        try:
            groups = group_by_charge(xyz_supermolecule, get_groups(xyz_supermolecule))
        except AssertionError as e:
            print("malformed input, falling back to reordering...", e)
            groups = reorder_and_group_by_charge(xyz_supermolecule)
        lines.append(str(len(groups[1])) + " ")
        lines[-1] += (str(groups[1]).strip("[]").replace(',', ''))
        _tmp_xyz_mol = XyzMolecule([Atom('He', *coords) for coords in groups[0]], self.params)
        _tmp_fra_mol = _tmp_xyz_mol.to_fra_molecule()
        lines.extend(' '.join(NUMBER_FORMAT.format(coord) for coord in at.get_coords()) for at in _tmp_fra_mol.atoms)
        lines.append(str(R_MAX) + " " + str(LOR_TOL))
        return '\n'.join(lines)

    def __repr__(self) -> str:
        lines = str(self.params) + "\n"
        lines += str(self.num_molecules) + ' ' + str(len(self.symmops)) + '\n'
        for molecule_flags in self.flags:
            lines += str([1 if u else 0 for u in molecule_flags]).strip('[]').replace(',', '') + '\n'
        for symmop in self.symmops:
            lines += str(symmop.to_line()) + '\n'
        for fra_molecule in self.fra_molecules:
            lines += fra_molecule.to_str(include_chg=True, include_params=False)
        return lines

    def for_charge_generation(self, r_cut=100.):
        lines_list = []
        for i in range(self.num_molecules):
            flags = copy.deepcopy(self.flags)
            flags[i][0] = False
            lines = str(self.params) + '\n'
            lines += str(r_cut) + " 1\n"
            flags = copy.deepcopy(self.flags)
            flags[i][0] = False
            supermolecule_without_ith = self.get_fra_supermolecule(flags)
            lines += str(self.fra_molecules[i].num_atoms + supermolecule_without_ith.num_atoms) + ' '
            lines += str(self.fra_molecules[i].num_atoms) + '\n'
            lines += self.fra_molecules[i].to_str(atomic_symbol=False, include_chg=True, include_num_atoms=False,
                                                  include_params=False)
            lines += supermolecule_without_ith.to_str(atomic_symbol=False, include_chg=True, include_num_atoms=False,
                                                      include_params=False)
            lines += str(Symmop.identity())
            lines_list.append(lines)
        return lines_list
