import re

from chi1chi2.utils.constants import Params, PI, ChiException
from chi1chi2.utils.molecule import FraMolecule, Atom
from chi1chi2.utils.molecule_reorderer import get_molecule_with_generated_charges

CRYSTAL_HEADER_PATT = re.compile(r"^crystal\s*$")
OPTIMIZED_STATEMENT = "FINAL OPTIMIZED GEOMETRY"
CONVENTIONAL_CELL_TAG = "COORDINATES IN THE CRYSTALLOGRAPHIC CELL"
ASYMMETRIC_UNIT_TAG = "ATOMS IN THE ASYMMETRIC UNIT"
OPT_STRUCT_LINE_PATT = re.compile(r"\s*\d+\s+([TF])\s+(\d+)\s+\w+\s+(.*)")
ATOMIC_CHG_STATEMENT = "TOTAL ATOMIC CHARGES:"
ATOMIC_CHG_PATTERN = re.compile(r"^(\s+\d+\.\d+)+\s*$")


def round_half(x):
    return round(x * 2) / 2


def read_fra_molecule(opt_file, generate_charges=False):
    with open(opt_file) as f:
        opt_lines = f.readlines()
    current_line_number = 0
    while CRYSTAL_HEADER_PATT.match(opt_lines[current_line_number]) is None:
        current_line_number += 1
    current_line_number += 3
    params = Params.from_line(opt_lines[current_line_number])
    current_line_number += 1
    n_ats = int(opt_lines[current_line_number].split()[0])
    current_line_number += 1
    ats = []
    for i in range(n_ats):
        ats.append(Atom.from_line(opt_lines[current_line_number]))
        current_line_number += 1
    fra_molecule = FraMolecule(ats, params)
    if generate_charges:
        xyz_molecule = fra_molecule.to_xyz_molecule()
        xyz_molecule = get_molecule_with_generated_charges(xyz_molecule)
        fra_molecule = xyz_molecule.to_fra_molecule()
        fra_molecule = FraMolecule(fra_molecule.atoms, fra_molecule.params)
    return fra_molecule


def read_opt_molecule(opt_file, charges=[]):
    with open(opt_file) as f:
        opt_lines = f.readlines()
    len_chg = len(charges)
    current_line_number = 0
    try:
        while opt_lines[current_line_number].find(OPTIMIZED_STATEMENT) < 0:
            current_line_number += 1
    except IndexError:
        print("geomtry not optimized")
        raise ChiException("restart optimization and get it done first!")
    I_store = current_line_number
    search_asymm = False
    try:
        while opt_lines[current_line_number].find(CONVENTIONAL_CELL_TAG) < 0:
            current_line_number += 1
    except IndexError:
        search_asymm = True
        current_line_number = I_store
    if search_asymm:  # todo add test file for this situation!
        try:
            while opt_lines[current_line_number].find(ASYMMETRIC_UNIT_TAG) < 0:
                current_line_number += 1
        except IndexError:
            print("asymmetric unit not found!")
            raise ChiException("check the optimization log!")
    params_raw = opt_lines[current_line_number - 2].split()
    params = Params(*(float(u) for u in params_raw[:3]), *(float(u) * PI / 180. for u in params_raw[3:6]))
    atoms = []
    current_line_number += 3
    c = 0
    try:
        while OPT_STRUCT_LINE_PATT.match(opt_lines[current_line_number]):
            match = OPT_STRUCT_LINE_PATT.match(opt_lines[current_line_number])
            if match.group(1) == 'T':
                atomic_num = float(match.group(2))
                atoms.append(Atom(match.group(2), *(float(u) for u in match.group(3).split()),
                                  atomic_num - charges[c] if len_chg > 0 else 0))
            current_line_number += 1
            c += 1
    except IndexError:
        print("unexpected end of optimization output in line: " + current_line_number)
        raise ChiException("provide a complete optimization file")
    return FraMolecule(atoms, params)


def read_optimized_coords(opt_file, charges=[]):
    # reading of input reference geometry
    reference = read_fra_molecule(opt_file)
    optimized = read_opt_molecule(opt_file, charges)
    atoms_adjusted = []
    if reference.num_atoms != optimized.num_atoms:
        raise ChiException("number of atoms in reference and optimized structure differs!")
    for i in range(reference.num_atoms):
        x_adj = optimized.atoms[i].x - round_half(optimized.atoms[i].x - reference.atoms[i].x)
        y_adj = optimized.atoms[i].y - round_half(optimized.atoms[i].y - reference.atoms[i].y)
        z_adj = optimized.atoms[i].z - round_half(optimized.atoms[i].z - reference.atoms[i].z)
        atoms_adjusted.append(Atom(optimized.atoms[i].symbol, x_adj, y_adj, z_adj, optimized.atoms[i].charge))
    return FraMolecule(atoms_adjusted, optimized.params)


def get_charges(scf_file):
    with open(scf_file) as f:
        scf_lines = f.readlines()
    current_line_number = len(scf_lines) - 1
    try:
        while scf_lines[current_line_number].find(ATOMIC_CHG_STATEMENT) < 0:
            current_line_number -= 1
    except IndexError:
        print("charges not found, check SCFLOG file")
        raise ChiException("provide a correct SCFLOG file")
    current_line_number += 1
    charges = []
    while ATOMIC_CHG_PATTERN.match(scf_lines[current_line_number]) is not None:
        charges.extend((float(u) for u in scf_lines[current_line_number].split()))
        current_line_number += 1
    return charges


def read_coords_charges(opt_file, scf_file):
    charges = get_charges(scf_file)
    return read_optimized_coords(opt_file, charges)
