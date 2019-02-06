import os
from collections import deque
from functools import reduce
from tempfile import mkstemp

import numpy as np
import openbabel as ob

from chi1chi2.utils.constants import HYDROGEN_TOLERANCE, ChiException
from chi1chi2.utils.molecule import Molecule, XyzMolecule, Atom
from chi1chi2.utils.molecule_reader_writer import from_file

ptable = ob.OBElementTable()
conv = ob.OBConversion()
conv.SetInAndOutFormats("xyz", "xyz")


def _is_hydrogen_bound(heavy_atom, hydrogen_atom):
    return np.linalg.norm(np.array(heavy_atom.get_coords()) - np.array(hydrogen_atom.get_coords())) < HYDROGEN_TOLERANCE


def is_ordered(molecule: Molecule) -> bool:
    hvy_ind = 0
    heavy_atom = molecule.atoms[hvy_ind]
    if heavy_atom.symbol == "H":
        return False
    cur_ind = 1
    while cur_ind < molecule.num_atoms:
        atom = molecule.atoms[cur_ind]
        if atom.symbol != "H":
            hvy_ind = cur_ind
            heavy_atom = molecule.atoms[hvy_ind]
            cur_ind += 1
        else:
            hydrogen_atom = atom
            if not _is_hydrogen_bound(heavy_atom, hydrogen_atom):
                print("heavy atom: " + str(heavy_atom) + " and hydrogen atom: " + str(
                    hydrogen_atom) + " is further than " + str(HYDROGEN_TOLERANCE) + " A")
                return False
            cur_ind += 1
    return True


def _group_heavies_by_molecule(heavies, connectivity_matrix):
    remaining_heavies = set(heavies.copy())

    # first (and maybe the only) molecule group for sure
    remaining_heavies = remaining_heavies.difference([heavies[0]])
    groups = [[heavies[0]]]

    while len(remaining_heavies) > 0:
        to_check = [groups[-1][0]]
        while len(to_check) > 0:
            current = to_check.pop(0)
            for heavy in remaining_heavies:
                if connectivity_matrix[current, heavy] > 0:
                    to_check.append(heavy)
                    groups[-1].append(heavy)
                    remaining_heavies = remaining_heavies.difference({heavy})
        if len(remaining_heavies) > 0:
            groups.append([remaining_heavies.pop()])
    # adding step to post-sort groups after using sets
    groups = [sorted(gr) for gr in groups]
    groups = sorted(groups, key=lambda gr: gr[0])
    return groups


def get_groups(molecule: XyzMolecule) -> list:
    if not is_ordered(molecule):
        raise ChiException("Molecule should first be reordered! Failure from method >>get_groups<<")
    obmol = _get_obmol(molecule)
    heavies, hydrogens, connectivity_matrix = __partition_atoms(obmol)
    heavies = _group_heavies_by_molecule(heavies, connectivity_matrix)
    groups = []
    for group_idx in range(len(heavies)):
        groups.append([])
        for heavy_idx in range(1, len(heavies[group_idx])):
            groups[-1].append(heavies[group_idx][heavy_idx] - heavies[group_idx][heavy_idx - 1])
        if group_idx < len(heavies) - 1:
            groups[-1].append(heavies[group_idx + 1][0] - heavies[group_idx][len(heavies[group_idx]) - 1])
    groups[-1].append(molecule.num_atoms - heavies[-1][-1])
    return groups


def get_molecules_by_groups(molecule: XyzMolecule) -> tuple:
    groups = get_groups(molecule)
    molecules = []
    act_first = 0
    for i in range(len(groups)):
        act_last = act_first + reduce(lambda a, b: a + b, groups[i])
        molecules.append(XyzMolecule(molecule.atoms[act_first:act_last], molecule.params))
        act_first = act_last
    return tuple(molecules)


def reorder_and_group_by_charge(molecule: Molecule) -> (list, list):
    molecule, groups = reorder(molecule)
    return group_by_charge(molecule, groups)


def group_by_charge(molecule: Molecule, groups: list) -> (tuple, tuple):
    if not is_ordered(molecule):
        raise ChiException("molecule is not ordered, failed to get group by charge")
    grouped_coordinates = []
    contracted_group_list = []
    current_atom_index = 0
    for i in range(len(groups)):
        submolecules = groups[i]
        contracted_group_list.append(len(submolecules))
        # iteration over one molecule group
        for j in range(len(submolecules)):
            coords, weight = np.zeros((3, 1)), 0.
            for k in range(submolecules[j]):
                atom = molecule.atoms[current_atom_index]
                weight += atom.get_atomic_num()
                coords += atom.get_atomic_num() * np.array(atom.get_coords()).reshape((3, 1))
                current_atom_index += 1
            grouped_coordinates.append((coords / weight)[:, 0].tolist())
    return grouped_coordinates, contracted_group_list


def adjust_hydrogens(molecule: Molecule) -> Molecule:
    obmol, tmp_file = _get_obmol_and_tmp_file(molecule)
    try:
        for i in range(obmol.NumBonds()):
            bond = obmol.GetBond(i)
            at1 = bond.GetBeginAtom()
            at2 = bond.GetEndAtom()
            if at1.GetAtomicNum() == 1 or at2.GetAtomicNum() == 1:
                bond.SetLength(bond.GetEquibLength())
        conv.WriteFile(obmol, tmp_file)
        molecule_adjusted = from_file(tmp_file)
    finally:
        os.remove(tmp_file)
    return molecule_adjusted


def reorder(molecule: Molecule) -> (Molecule, tuple):
    obmol = _get_obmol(molecule)

    seq, groups = __add_all_atoms(*__partition_atoms(obmol))
    atoms = [molecule.atoms[i] for i in seq]

    return Molecule(atoms, molecule.params), groups


def _get_obmol(molecule):
    obmol, tmp_file = _get_obmol_and_tmp_file(molecule)
    os.remove(tmp_file)
    return obmol


def _get_obmol_and_tmp_file(molecule):
    _, tmp_file = mkstemp(suffix=".xyz")
    with open(tmp_file, 'w') as f:
        f.write(str(molecule))
    obmol = ob.OBMol()
    conv.ReadFile(obmol, tmp_file)
    return obmol, tmp_file


def __partition_atoms(obmol):
    heavies = deque()
    hydrogens = deque()
    N = obmol.NumAtoms()
    connectivity_matrix = np.zeros((N, N))

    for atom_index in range(N):
        at = obmol.GetAtom(atom_index + 1)
        # connectivity_matrix[atom_index, atom_index] = at.GetAtomicNum()
        # print(i + 1, at.GetType(), at.GetHvyValence())
        if ptable.GetSymbol(at.GetAtomicNum()) == "H":
            hydrogens.append(atom_index)
        else:
            heavies.append(atom_index)

    for bond_index in range(obmol.NumBonds()):
        bnd = obmol.GetBond(bond_index)
        a = bnd.GetBeginAtomIdx() - 1
        b = bnd.GetEndAtomIdx() - 1
        connectivity_matrix[a, b] = 1
        connectivity_matrix[b, a] = 1

    return heavies, hydrogens, connectivity_matrix


def __get_indices_for(a_list):
    return set([ind for ind in range(len(a_list)) if a_list[ind] > 0])


def __add_all_hydrogens_to_heavy_atom(seq, current_heavy, hydrogens, conn_matr, groups):
    connected_hydrogens = set(hydrogens).intersection(__get_indices_for(conn_matr[current_heavy]))
    for hydrogen_idx in connected_hydrogens:
        seq.append(hydrogen_idx)
        hydrogens.remove(hydrogen_idx)
        groups[-1][-1] += 1


def __get_connected_heavies(current_heavy, heavies, conn_matr):
    connected_heavies = set(heavies).intersection(__get_indices_for(conn_matr[current_heavy]))
    for heavy_idx in connected_heavies:
        heavies.remove(heavy_idx)
    return connected_heavies


def __add_all_atoms_to_sequence(seq, first_heavy, heavies, hydrogens, conn_matr, groups):
    current_heavies = deque()
    current_heavies.append(first_heavy)
    while current_heavies:
        current_heavy = current_heavies.popleft()
        seq.append(current_heavy)
        groups[-1].append(1)
        current_heavies.extend(__get_connected_heavies(current_heavy, heavies, conn_matr))
        __add_all_hydrogens_to_heavy_atom(seq, current_heavy, hydrogens, conn_matr, groups)


def __add_all_atoms(heavies, hydrogens, conn_matr):
    if not heavies:
        raise ChiException("only hydrogens, it won't work...")
    seq = []
    groups = []
    while heavies:  # there might be more than one molecule, let's iterate over them
        first_heavy = heavies.popleft()
        groups.append([])
        __add_all_atoms_to_sequence(seq, first_heavy, heavies, hydrogens, conn_matr, groups)
    return seq, groups


def get_molecule_with_generated_charges(molecule: XyzMolecule):
    obmol = _get_obmol(molecule)
    atoms = []
    for i in range(molecule.num_atoms):
        at = molecule.atoms[i]
        ob_at = obmol.GetAtom(i + 1)
        atoms.append(Atom(at.symbol, at.x, at.y, at.z, ob_at.GetPartialCharge()))
    return XyzMolecule(atoms, molecule.params)
