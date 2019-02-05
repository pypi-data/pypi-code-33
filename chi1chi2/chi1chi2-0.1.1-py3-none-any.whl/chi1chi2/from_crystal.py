#!/usr/bin/env python
import os
from optparse import OptionParser

from chi1chi2.crystal_support.crystal_reader import read_coords_charges
from chi1chi2.input.input_preparator import Input
from chi1chi2.utils.constants import resolve_path, XYZ_EXTENSION, INP_FILENAME_PATTERN
from chi1chi2.utils.molecule_reader_writer import write_mol_to_file
from chi1chi2.utils.molecule_reorderer import get_molecules_by_groups

usage = """
%prog [options]
this script facilitates reading of geometry and charges after crystal09/14/.. structure optimization

required input:
- previously prepared input file
- crystal09/14/.. optimization output file
- crystal09/14/.. optimization SCFLOG file

default output:
- final input file
- xyz output for visualization with molden or similar program for verification
- xyz files for separated molecules for property calculations (when no further geometry optimization considered)
"""
parser = OptionParser(usage=usage)

parser.add_option("-i", "--input-file", dest="input_file", help="pre-prepared input file (R)", action="store",
                  type="string", default=None)
parser.add_option("-t", "--optimization-file", dest="opt_file", help="optimization output file (R)", action="store",
                  type="string", default=None)
parser.add_option("-s", "--scflog-file", dest="scf_file", help="SCFLOG output file (R)", action="store", type="string",
                  default=None)
parser.add_option("-o", "--outputfile", dest="output_file", help="output file", action="store", type="string",
                  default=None)
parser.add_option("-X", "--skip-xyz", dest="skip_produce_xyz", help="skip preparation of xyz files for property \
                        calculations, default=False", action="store_true",
                  default=False)

(options, args) = parser.parse_args()


def run():
    if any(required_file is None for required_file in (options.input_file, options.opt_file, options.scf_file)):
        parser.error("No input file given, check for the list of required (R) input files")

    inp = Input.from_file(options.input_file)

    fra_supermolecule = read_coords_charges(options.opt_file, options.scf_file)
    xyz_supermolecule = fra_supermolecule.to_xyz_molecule()

    xyz_molecules = get_molecules_by_groups(xyz_supermolecule)

    # prepare and write the final input file
    final_inp = Input(inp.params, inp.flags, inp.symmops, [xyz_mol.to_fra_molecule() for xyz_mol in xyz_molecules],
                      inp.asym_groups)
    if options.output_file is None:
        options.output_file = options.input_file + '_tmp'
    with open(options.output_file, 'w') as f:
        f.write(str(final_inp))
        print(f"{options.output_file} written to use in the program\n"
              f"***Correct the the symmetry operations if started from bare fra file to proceed further!")

    # writing the xyz file
    output_xyz_file = resolve_path(options.input_file, INP_FILENAME_PATTERN, XYZ_EXTENSION)
    with open(output_xyz_file, 'w') as f:
        f.write(xyz_supermolecule.to_str())

    # writing the xyz_files for property calculations
    if not options.skip_produce_xyz:
        if not os.path.isdir("prop"):
            os.mkdir("prop")
        for i, molecule in enumerate(xyz_molecules):
            write_mol_to_file(molecule, "prop/mol" + str(i + 1) + XYZ_EXTENSION)
            print(f"charge of molecule {i + 1}: {molecule.get_charge():.2f}")


if __name__ == '__main__':
    run()
