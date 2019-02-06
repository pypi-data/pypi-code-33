#!/usr/bin/env python
import os
from optparse import OptionParser

from chi1chi2.input.input_preparator import Input
from chi1chi2.utils.constants import Symmop, resolve_path, XYZ_EXTENSION, INP_EXTENSION, FRA_FILENAME_PATTERN
from chi1chi2.utils.molecule import FraMolecule
from chi1chi2.utils.molecule_reader_writer import from_file, write_mol_to_file
from chi1chi2.utils.molecule_reorderer import reorder, adjust_hydrogens, get_molecules_by_groups, get_groups

usage = """
%prog [options]
this script facilitates preparation of the input for the main script when some other geometry optimization procedure \
is to be used or none at all (fra input required)

required input:
- name of the input file (fra)
optional input:
- name of the output file

default output:
- stub input file
- fra output file with atomic charges (for crystal09/14/.. optimization)
- xyz output for visualization with molden or similar program for verification
optional output:
- xyz files for separated molecules for property calculations (when no further geometry optimization considered)
"""

parser = OptionParser(usage=usage)

parser.add_option("-i", "--inputfile", dest="input_file", help="input file", action="store", type="string",
                  default=None)
parser.add_option("-o", "--outputfile", dest="output_file", help="output file", action="store", type="string",
                  default=None)
parser.add_option("-f", "--output-fra", dest="output_fra", help="output fra file", action="store", type="string",
                  default=None)
parser.add_option("-x", "--output-xyz", dest="output_xyz_file", help="xyz file name, not produced by default \
(useful to inspect with a molecular viewing tool such as molden", action="store", type="string",
                  default=None)
parser.add_option("-H", "--skip-adjust-hydrogens", dest="skip_adj_hydr",
                  help="flag to skip hydrogen adjusting, default=False", action="store_true", default=False)
parser.add_option("-R", "--skip-reorder", dest="skip_reorder", help="flag to skip molecule reordering, default=False",
                  action="store_true", default=False)
parser.add_option("-X", "--produce-xyz", dest="produce_xyz", help="produce xyz files for property calculations, \
                                                                  default=False", action="store_true", default=False)

(options, args) = parser.parse_args()


def run():
    if options.input_file is None or not options.input_file.endswith("fra"):
        parser.error("No input file given, check usage")

    fra_mol = from_file(options.input_file)
    xyz_mol = fra_mol.to_xyz_molecule()
    if not options.skip_adj_hydr:
        xyz_mol = adjust_hydrogens(xyz_mol)
    if not options.skip_reorder:
        xyz_mol, groups = reorder(xyz_mol)

    xyz_molecules = get_molecules_by_groups(xyz_mol)
    groups = get_groups(xyz_mol)

    # writing input file
    inp = Input(fra_mol.params,
                [[True] for i in range(len(xyz_molecules))],
                [Symmop.identity()],
                [xyz_mol.to_fra_molecule() for xyz_mol in xyz_molecules],
                groups)
    if options.output_file is None:
        options.output_file = resolve_path(options.input_file, FRA_FILENAME_PATTERN, INP_EXTENSION)
    with open(options.output_file, 'w') as f:
        f.write(str(inp))

    # writing the fractional coordinate file
    if options.output_fra is None:
        options.output_fra = resolve_path(options.input_file, FRA_FILENAME_PATTERN, "_preopt.fra")
    with open(options.output_fra, 'w') as f:
        atoms = []
        for mol in inp.fra_molecules:
            atoms.extend(mol.atoms)
        fra_asym = FraMolecule(atoms, inp.params)
        f.write(fra_asym.to_str(atomic_symbol=False, include_chg=False))
        print(options.output_fra + " (fra) file written for geometry optimization")

    # writing the xyz file
    if options.output_xyz_file is None:
        options.output_xyz_file = resolve_path(options.input_file, FRA_FILENAME_PATTERN, XYZ_EXTENSION)
    with open(options.output_xyz_file, 'w') as f:
        f.write(xyz_mol.to_str())

    # writing the xyz_files for property calculations
    if options.produce_xyz:
        if not os.path.isdir("prop"):
            os.mkdir("prop")
        for i, molecule in enumerate(xyz_molecules):
            write_mol_to_file(molecule, "prop/mol" + str(i + 1) + XYZ_EXTENSION)
            print(f"charge of molecule {i + 1}: {molecule.get_charge():.2f}")


if __name__ == '__main__':
    run()
