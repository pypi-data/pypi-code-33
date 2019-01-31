#!/usr/bin/env python
import os
from optparse import OptionParser

from chi1chi2.cif.cif_parser import Cif
from chi1chi2.input.input_preparator import Input
from chi1chi2.utils.constants import resolve_path, XYZ_EXTENSION, CIF_FILENAME_PATTERN, INP_EXTENSION
from chi1chi2.utils.molecule import FraMolecule
from chi1chi2.utils.molecule_reader_writer import write_mol_to_file
from chi1chi2.utils.molecule_reorderer import adjust_hydrogens, reorder, get_molecules_by_groups, \
    get_molecule_with_generated_charges

usage = """
%prog [options]
this script facilitates rendering of the input file from CIF

required input:
- cif file
optional input:
- name of the output file
- name of the fra file

default output:
- stub input file
- fra output file with atomic charges (for crystal09/14/.. optimization)
- xyz output for visualization with molden or similar program for verification
optional output:
- xyz files for separated molecules for property calculations (when no further geometry optimization considered)
"""
parser = OptionParser(usage=usage)

parser.add_option("-i", "--cif-inputfile", dest="input_file", help="CIF input file", action="store", type="string",
                  default=None)
parser.add_option("-o", "--output-file", dest="output_file", help="output file", action="store", type="string",
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
    if options.input_file is None:
        parser.error("No input file given, check usage")

    xyz_molecules, symmops, groups = _get_molecule_symmops_groups(options.input_file)
    fra_molecules = [xyz_mol.to_fra_molecule() for xyz_mol in xyz_molecules]

    # writing of the stub input file
    inp = Input(xyz_molecules[0].params, [[True for i in range(len(symmops))] for j in range(len(groups))], symmops,
                fra_molecules, groups)
    if options.output_file is None:
        options.output_file = resolve_path(options.input_file, CIF_FILENAME_PATTERN, INP_EXTENSION)
    with open(options.output_file, 'w') as f:
        f.write(str(inp))
        print(options.output_file + " temporary input file written")

    # writing the fractional coordinate file
    if options.output_fra is None:
        options.output_fra = resolve_path(options.input_file, CIF_FILENAME_PATTERN, "_preopt.fra")
    with open(options.output_fra, 'w') as f:
        atoms = []
        for mol in inp.fra_molecules:
            atoms.extend(mol.atoms)
        fra_asym = FraMolecule(atoms, inp.params)
        f.write(fra_asym.to_str(atomic_symbol=False, include_chg=False))
        print(options.output_fra + " (fra) file written for geometry optimization")

    # writing the xyz file for verification
    fra_supermolecule = inp.get_fra_supermolecule(inp.flags)
    xyz_supermolecule = fra_supermolecule.to_xyz_molecule()
    if options.output_xyz_file is None:
        options.output_xyz_file = resolve_path(options.input_file, CIF_FILENAME_PATTERN, XYZ_EXTENSION)
    with open(options.output_xyz_file, 'w') as f:
        f.write(xyz_supermolecule.to_str())
    print(options.output_xyz_file + " xyz file written for verification")

    # writing the xyz_files for property calculations
    if options.produce_xyz:
        if not os.path.isdir("prop"):
            os.mkdir("prop")
        for i, molecule in enumerate(xyz_molecules):
            write_mol_to_file(molecule, "prop/mol" + str(i + 1) + XYZ_EXTENSION)
            print(f"charge of molecule {i + 1}: {molecule.get_charge():.2f}")


def _get_molecule_symmops_groups(input_file):
    cif = Cif.from_file(input_file)
    mol = cif.get_fra_mol().to_xyz_molecule()
    groups = []
    if not options.skip_adj_hydr:
        mol = adjust_hydrogens(mol)
    if not options.skip_reorder:
        mol, groups = reorder(mol)
    mol = get_molecule_with_generated_charges(mol)
    molecules = get_molecules_by_groups(mol)
    return molecules, cif.get_symmops(), groups


if __name__ == '__main__':
    run()
