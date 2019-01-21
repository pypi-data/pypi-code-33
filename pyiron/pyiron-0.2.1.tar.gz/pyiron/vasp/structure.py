# coding: utf-8
# Copyright (c) Max-Planck-Institut für Eisenforschung GmbH - Computational Materials Design (CM) Department
# Distributed under the terms of "New BSD License", see the LICENSE file.

from collections import OrderedDict
import numpy as np
from pyiron.atomistics.structure.atoms import Atoms

__author__ = "Sudarsan Surendralal"
__copyright__ = "Copyright 2019, Max-Planck-Institut für Eisenforschung GmbH - " \
                "Computational Materials Design (CM) Department"
__version__ = "1.0"
__maintainer__ = "Sudarsan Surendralal"
__email__ = "surendralal@mpie.de"
__status__ = "production"
__date__ = "Sep 1, 2017"


def read_atoms(filename='CONTCAR', return_velocities=False, species_list=None, species_from_potcar=False):
    """
    Routine to read structural static from a POSCAR type file

    Args:
        filename (str): Input filename
        return_velocities (bool): True if the predictor corrector velocities are read (only from MD output)
        species_list (list/numpy.ndarray): A list of the species (if not present in the POSCAR file or a POTCAR in the
        same directory)
        species_from_potcar (bool): True if the species list should be read from the POTCAR file in the same directory

    Returns:
        pyiron.atomistics.structure.atoms.Atoms: The generated structure object

    """
    directory = "/".join(filename.split("/")[0:-1])
    potcar_file = "/".join([directory, "POTCAR"])
    if (species_list is None) and species_from_potcar:
        species_list = get_species_list_from_potcar(potcar_file)
    file_string = list()
    with open(filename) as f:
        for line in f:
            line = line.strip()
            file_string.append(line)
    return atoms_from_string(file_string, read_velocities=return_velocities, species_list=species_list)


def get_species_list_from_potcar(filename="POTCAR"):
    """
    Generates the species list from a POTCAR type file

    Args:
        filename (str): Input filename

    Returns:
        list: A list of species symbols

    """
    trigger = "VRHFIN ="
    species_list = list()
    with open(filename) as potcar_file:
        lines = potcar_file.readlines()
        for line in lines:
            line = line.strip()
            if trigger in line:
                str_1 = line.split(trigger)
                str_2 = str_1[-1].split(":")
                species_list.append(str_2[0].replace(" ", ""))
    return species_list


def write_poscar(structure, filename="POSCAR", write_species=True, cartesian=True):
    """
    Writes a POSCAR type file from a structure object

    Args:
        structure (pyiron.atomistics.structure.atoms.Atoms): The structure instance to be written to the POSCAR format
        filename (str): Output filename
        write_species (bool): True if the species should be written to the file
        cartesian (bool): True if the positions are written in Cartesian coordinates

    """
    endline = "\n"
    with open(filename, 'w') as f:
        selec_dyn = False
        f.write('Poscar file generated with pyiron' + endline)
        f.write('1.0' + endline)
        for a_i in structure.get_cell():
            x, y, z = a_i
            f.write('{0:f} {1:f} {2:f}'.format(x, y, z) + endline)
        atom_numbers = structure.get_number_species_atoms()
        if write_species:
            f.write(" ".join(atom_numbers.keys()) + endline)
        num_str = [str(val) for val in atom_numbers.values()]
        f.write(" ".join(num_str))
        f.write(endline)
        if 'selective_dynamics' in structure.get_tags():
            selec_dyn = True
            f.write("Selective dynamics" + endline)
        sorted_coords = list()
        selec_dyn_lst = list()
        for species in atom_numbers.keys():
            indices = structure.select_index(species)
            for i in indices:
                if cartesian:
                    sorted_coords.append(structure.positions[i])
                else:
                    sorted_coords.append(structure.scaled_positions[i])
                if selec_dyn:
                    selec_dyn_lst.append(structure.selective_dynamics[i])
        if cartesian:
            f.write("Cartesian" + endline)
        else:
            f.write("Direct" + endline)
        if selec_dyn:
            for i, vec in enumerate(sorted_coords):
                x, y, z = vec
                sd_string = ' '.join(['T' if sd else 'F' for sd in selec_dyn_lst[i]])
                f.write('{0:.15f} {1:.15f} {2:.15f}'.format(x, y, z) + ' ' + sd_string + endline)
        else:
            for i, vec in enumerate(sorted_coords):
                x, y, z = vec
                f.write('{0:.15f} {1:.15f} {2:.15f}'.format(x, y, z) + endline)


def atoms_from_string(string, read_velocities=False, species_list=None):
    """
    Routine to convert a string list read from a input/output structure file and convert into Atoms instance

    Args:
        string (list): A list of strings (lines) read from the POSCAR/CONTCAR/CHGCAR/LOCPOT file
        read_velocities (bool): True if the velocities from a CONTCAR file should be read (predictor corrector)
        species_list (list/numpy.ndarray): A list of species of the atoms

    Returns:
        pyiron.atomistics.structure.atoms.Atoms: The required structure object

    """
    string = [s.strip() for s in string]
    atoms_dict = dict()
    atoms_dict["first_line"] = string[0]
    # del string[0]
    atoms_dict["selective_dynamics"] = False
    atoms_dict["relative"] = False
    for val in ['direct', 'Direct', "D", "d"]:
        if val in string:
            atoms_dict["relative"] = True
    atoms_dict["scaling_factor"] = float(string[1])
    unscaled_cell = list()
    for i in [2, 3, 4]:
        vec = list()
        for j in range(3):
            vec.append(float(string[i].split()[j]))
        unscaled_cell.append(vec)
    if atoms_dict["scaling_factor"] > 0.:
        atoms_dict["cell"] = np.array(unscaled_cell) * atoms_dict["scaling_factor"]
    else:
        atoms_dict["cell"] = np.array(unscaled_cell) * ((-atoms_dict["scaling_factor"]) ** (1. / 3.))
    for val in ["Selective Dynamics", "selective dynamics", "Selective dynamics", "selective Dynamics"]:
        if val in string:
            atoms_dict["selective_dynamics"] = True
    no_of_species = len(string[5].split())
    species_dict = OrderedDict()
    position_index = 7
    if atoms_dict["selective_dynamics"]:
        position_index += 1
    for i in range(no_of_species):
        species_dict["species_" + str(i)] = dict()
        try:
            species_dict["species_" + str(i)]["count"] = int(string[5].split()[i])
        except ValueError:
            species_dict["species_" + str(i)]["species"] = string[5].split()[i]
            species_dict["species_" + str(i)]["count"] = int(string[6].split()[i])
    atoms_dict["species_dict"] = species_dict
    if "species" in atoms_dict["species_dict"]["species_0"].keys():
        position_index += 1
    positions = list()
    selective_dynamics = list()
    n_atoms = 0
    for key in atoms_dict["species_dict"].keys():
        n_atoms += atoms_dict["species_dict"][key]["count"]
    for i in range(position_index, position_index + n_atoms):
        vec = list()
        for j in range(3):
            vec.append(float(string[i].split()[j]))
        if atoms_dict["selective_dynamics"]:
            selective_dynamics.append(["T" in string[i].split()[k] for k in range(3, 6)])
        positions.append(vec)
    atoms_dict["positions"] = np.array(positions)
    if not atoms_dict["relative"]:
        if atoms_dict["scaling_factor"] > 0.:
            atoms_dict["positions"] *= atoms_dict["scaling_factor"]
        else:
            atoms_dict["positions"] *= (-atoms_dict["scaling_factor"]) ** (1. / 3.)

    if not (len(atoms_dict["positions"]) == n_atoms):
        raise AssertionError()
    velocities = list()
    if read_velocities:
        velocity_index = position_index + n_atoms + 1
        for i in range(velocity_index, velocity_index + n_atoms):
            vec = list()
            for j in range(3):
                vec.append(float(string[i].split()[j]))
            velocities.append(vec)
        if not (len(velocities) == n_atoms):
            raise AssertionError()
        atoms = _dict_to_atoms(atoms_dict, species_list=species_list)
        if atoms_dict["selective_dynamics"]:
            selective_dynamics = np.array(selective_dynamics)
            atoms.add_tag(selective_dynamics=[True, True, True])
            atoms.selective_dynamics[:] = selective_dynamics
        return atoms, velocities
    else:
        atoms = _dict_to_atoms(atoms_dict, species_list=species_list)
        if atoms_dict["selective_dynamics"]:
            selective_dynamics = np.array(selective_dynamics)
            atoms.add_tag(selective_dynamics=[True, True, True])
            atoms.selective_dynamics = selective_dynamics
        return atoms


def _dict_to_atoms(atoms_dict, species_list=None, read_from_first_line=False):
    """
    Function to convert a generated dict into an structure object

    Args:
        atoms_dict (dict): Dictionary with the details (from string_to_atom)
        species_list (list/numpy.ndarray): List of species
        read_from_first_line (bool): True if we are to read the species information from the first line in the file

    Returns:
        pyiron.atomistics.structure.atoms.Atoms: The required structure object
    """
    is_absolute = not (atoms_dict["relative"])
    positions = atoms_dict["positions"]
    cell = atoms_dict["cell"]
    symbol = str()
    elements = list()
    el_list = list()
    for i, sp_key in enumerate(atoms_dict["species_dict"].keys()):
        if species_list is not None:
            try:
                el_list = np.array([species_list[i]])
                el_list = np.tile(el_list, atoms_dict["species_dict"][sp_key]["count"])
                if isinstance(species_list[i], str):
                    symbol += species_list[i] + str(atoms_dict["species_dict"][sp_key]["count"])
                else: 
                    symbol += species_list[i].Abbreviation + str(atoms_dict["species_dict"][sp_key]["count"])
            except IndexError:
                raise ValueError("Number of species in the specified species list does not match that in the file")
        elif "species" in atoms_dict["species_dict"][sp_key].keys():
            el_list = np.array([atoms_dict["species_dict"][sp_key]["species"]])
            el_list = np.tile(el_list, atoms_dict["species_dict"][sp_key]["count"])
            symbol += atoms_dict["species_dict"][sp_key]["species"]
            symbol += str(atoms_dict["species_dict"][sp_key]["count"])
        elif read_from_first_line:
            if not (len(atoms_dict["first_line"].split()) == len(atoms_dict["species_dict"].keys())):
                raise AssertionError()
            el_list = np.array(atoms_dict["first_line"].split()[i])
            el_list = np.tile(el_list, atoms_dict["species_dict"][sp_key]["count"])
            symbol += atoms_dict["first_line"].split()[i]
            symbol += str(atoms_dict["species_dict"][sp_key]["count"])
        elif species_list is None:
            raise ValueError("Species list should be provided since pyiron can't detect species information")
        elements.append(el_list)
    elements_new = list()
    for ele in elements:
        for e in ele:
            elements_new.append(e)
    elements = elements_new
    if is_absolute:
        atoms = Atoms(elements, positions=positions, cell=cell)
    else:
        atoms = Atoms(elements, scaled_positions=positions, cell=cell)
    return atoms


def vasp_sorter(structure):
    """
    Routine to sort the indices of a structure as it would be when written to a POSCAR file

    Args:
        structure (pyiron.atomistics.structure.atoms.Atoms): The structure whose indices need to be sorted

    Returns:
        list: A list of indices which is sorted by the corresponding species for writing to POSCAR

    """
    atom_numbers = structure.get_number_species_atoms()
    sorted_indices = list()
    for species in atom_numbers.keys():
        indices = structure.select_index(species)
        for i in indices:
            sorted_indices.append(i)
    return sorted_indices
