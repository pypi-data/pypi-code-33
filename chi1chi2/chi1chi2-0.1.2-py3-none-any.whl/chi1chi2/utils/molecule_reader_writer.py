import openbabel as ob

from chi1chi2.utils.constants import PI, Params, ChiException
from chi1chi2.utils.molecule import XyzMolecule, Atom, FraMolecule, Molecule

ptable = ob.OBElementTable()


def from_file(file):
    if file.endswith('.xyz'):
        return __from_xyz_file(file)
    elif file.endswith('.fra'):
        return __from_frac_file(file)
    else:
        raise ChiException("unknown file format encountered...")


def __from_xyz_file(file):
    """
    reading from frac file with similar to xyz convention
    :param file: .frac file
    """
    atoms, params = __read_atoms_params_from_file(file)
    return XyzMolecule(atoms, params)


def __read_atoms_params_from_file(file):
    with open(file) as f:
        lines = f.readlines()
    return read_atoms_params_from_lines_list(lines)


def read_atoms_params_from_lines_list(lines):
    num_atoms = int(lines[0].split()[0])
    atoms = []
    try:
        param_line = lines[1].split()
        abc = [float(u) for u in param_line[:3]]
        albega = [float(u) * PI / 180. for u in param_line[3:6]]
        params = Params(*abc, *albega)
    except (IndexError, TypeError):
        params = Params.default()
    for i in range(num_atoms):
        atoms.append(Atom.from_line(lines[2 + i]))
    return atoms, params


def __from_frac_file(file):
    """
    reading from .frac file
    :param file: fractional coordinates of molecules in the unit cell
    """
    atoms, params = __read_atoms_params_from_file(file)
    return FraMolecule(atoms, params)


def write_mol_to_file(molecule: Molecule, file_name: str) -> None:
    with open(file_name, 'w+') as f:
        f.write(str(molecule))


def write_prop_file(molecule: Molecule, file_name: str, charges_file: str = None) -> None:
    pass
