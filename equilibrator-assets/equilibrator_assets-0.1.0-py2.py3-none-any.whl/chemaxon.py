# The MIT License (MIT)
#
# Copyright (c) 2013 The Weizmann Institute of Science.
# Copyright (c) 2018 Institute for Molecular Systems Biology, ETH Zurich.
# Copyright (c) 2018 Novo Nordisk Foundation Center for Biosustainability,
# Technical University of Denmark.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.


"""Enrich compounds with cheminformatic properties."""


import logging
import subprocess
import typing
from collections import defaultdict, namedtuple
from io import StringIO
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd
import pybel


LOG10 = np.log(10.0)

logger = logging.getLogger("populate.chemaxon")
periodic_table = pybel._obconsts.OBElementTable()

MoleculeData = namedtuple(
    "MoleculeData", ["atom_bag", "smiles", "charge", "number_protons"]
)
# A dictionary from InChIKey to MoleculeData objects
# Here we list a few exceptions, i.e. compounds that are not treated
# correctly by cxcalc, and override them with our own data
INCHI_EXCEPTIONS = {
    # H+
    # We add an exception for H+ (and put nH = 0) in order to
    # eliminate its effect of the Legendre transform.
    "InChI=1S/p+1": MoleculeData(
        atom_bag={"H": 1}, smiles=None, charge=0, number_protons=0
    ),
    # sulfur
    # ChemAxon gets confused with the structure of sulfur
    #  (returns a protonated form, [SH-], at pH 7).
    "InChI=1S/S": MoleculeData(
        atom_bag={"S": 1, "e-": 16}, smiles="S", charge=0, number_protons=0
    ),
    # CO
    # ChemAxon gets confused with the structure of carbon
    # monoxide (returns a protonated form, [CH]#[O+], at pH 7).
    "InChI=1S/CO/c1-2": MoleculeData(
        atom_bag={"C": 1, "O": 1, "e-": 14},
        smiles="[C-]#[O+]",
        charge=0,
        number_protons=0,
    ),
    # H2
    "InChI=1S/H2/h1H": MoleculeData(
        atom_bag={"H": 2, "e-": 2}, smiles=None, charge=0, number_protons=2
    ),
    # Metal Cations get multiple pKa values from ChemAxon, which is
    # obviously a bug. We override the important ones here:
    # Ca2+
    "InChI=1S/Ca/q+2": MoleculeData(
        atom_bag={"Ca": 1, "e-": 18},
        smiles="[Ca++]",
        charge=2,
        number_protons=0,
    ),
    # K+
    "InChI=1S/K/q+1": MoleculeData(
        atom_bag={"K": 1, "e-": 18}, smiles="[K+]", charge=1, number_protons=0
    ),
    # Mg2+
    "InChI=1S/Mg/q+2": MoleculeData(
        atom_bag={"Mg": 1, "e-": 10},
        smiles="[Mg++]",
        charge=2,
        number_protons=0,
    ),
    # Fe2+
    "InChI=1S/Fe/q+2": MoleculeData(
        atom_bag={"Fe": 1, "e-": 24},
        smiles="[Fe++]",
        charge=2,
        number_protons=0,
    ),
    # Fe3+
    "InChI=1S/Fe/q+3": MoleculeData(
        atom_bag={"Fe": 1, "e-": 23},
        smiles="[Fe+++]",
        charge=3,
        number_protons=0,
    ),
    # catchers for empty InChIs
    None: MoleculeData({}, None, None, None),
    np.nan: MoleculeData({}, None, None, None),
    "": MoleculeData({}, None, None, None),
}

# A dictionary from MetaNetX ID to MoleculeData objects
# These compounds don't have a real structure, but we still want to use them
# for training the component-contribution data
METANETX_EXCEPTIONS = {
    # ferredoxin(red)
    "MNXM169": MoleculeData(
        atom_bag={"Fe": 1, "e-": 26}, smiles=None, charge=0, number_protons=0
    ),
    # ferredoxin(ox)
    "MNXM178": MoleculeData(
        atom_bag={"Fe": 1, "e-": 25}, smiles=None, charge=1, number_protons=0
    ),
}


CXCALC_BIN = "cxcalc"


class ChemAxonNotAvailableError(OSError):
    """Raise when ``cxcalc`` is not available."""

    pass


def verify_cxcalc():
    """Verify the existence of the ``cxcalc`` command line program."""
    try:
        subprocess.run([CXCALC_BIN, "--help"])
        return True
    except OSError:
        return False


def run_cxcalc(molstring: str, args: typing.List[str]):
    """
    Run cxcalc as a subprocess.

    Parameters
    ----------
    molstring : str
        A text description of the molecule(s) (SMILES or InChI).
    args : list
        A list of arguments for cxcalc.

    Returns
    -------
    tuple
        str
            The cxcalc standard output.
        str
            The cxcalc standard error.

    Raises
    ------
    subprocess.CalledProcessError
        If the command fails.
    ChemAxonNotAvailableError
        If the cxcalc program is not working as expected.

    """
    command = [CXCALC_BIN] + args
    try:
        logger.debug("Parameters: %s | %s", molstring, " ".join(command))
        result = subprocess.run(
            command,
            input=molstring,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            check=True,
        )
    except OSError as error:
        raise ChemAxonNotAvailableError(
            f"{error.strerror} (Please ensure that Marvin cxcalc is "
            f"properly installed as described at https://chemaxon.com/.)"
        )
    return result.stdout, result.stderr


def get_molecular_masses(
    molecules: pd.DataFrame, error_log: str
) -> pd.DataFrame:
    """
    Compute the dissociation constants and major microspecies at a defined pH.

    Parameters
    ----------
    molecules: pandas.DataFrame
        A list containing descriptions of the molecules (SMILES or InChI).
    error_log : str
        The base file path for error output.

    Returns
    -------
    view : pandas.DataFrame
        the input molecules data frame joined with the results calculated
        by ``cxcalc``.

    """
    if len(molecules) == 0:
        raise ValueError("Empty list of molecules, cannot calculate pKas.")

    args = [
        "--ignore-error",  # Continue with the next molecule on error.
        "mass",  # calculate molecular mass.
    ]

    output, error = run_cxcalc("\n".join(molecules["inchi"].tolist()), args)
    with open(f"{str(error_log)}.log", "w") as handle:
        # We skip the unhelpful Java stack traces that occur every second line.
        handle.write("\n".join(error.split("\n")[::2]))

    try:
        output_df = pd.read_table(StringIO(output), header=0, index_col="id")
    except pd.errors.EmptyDataError:
        raise ValueError("ChemAxon failed on all molecules")

    output_df.rename(columns={"Molecular weight": "mass"}, inplace=True)
    # We adjust the input index to start at 1 in order to be aligned with the
    # cxcalc standard and error output.
    molecules.index = range(1, 1 + molecules.shape[0])
    # Left join the results on index.
    return molecules.join(output_df)


def get_dissociation_constants(
    molecules: pd.DataFrame,
    error_log: str,
    num_acidic: int,
    num_basic: int,
    mid_ph: float,
) -> Tuple[pd.DataFrame, List[str]]:
    """
    Compute the dissociation constants and major microspecies at a defined pH.

    Parameters
    ----------
    molecules: pandas.DataFrame
        A list containing descriptions of the molecules (SMILES or InChI).
    error_log : str
        The base file path for error output.
    num_acidic : int
        The maximal number of acidic pKas to calculate.
    num_basic : int
        The maximal number of basic pKas to calculate.
    mid_ph : float
        The pH for which the major pseudoisomer is calculated.

    Returns
    -------
    view, pka_columns : Tuple[pandas.DataFrame, List[str]]
        view - the input molecules data frame joined with the results
               calculated by ``cxcalc``.
        pka_columns - a list of the column names in 'view' containing pKa values

    """
    if len(molecules) == 0:
        raise ValueError("Empty list of molecules, cannot calculate pKas.")

    args = [
        "--ignore-error",  # Continue with the next molecule on error.
        "pka",  # pKa calculation.
        "--na",  # The number of acidic pKa values displayed.
        str(num_acidic),
        "--nb",  # The number of basic pKa values displayed.
        str(num_basic),
        "majorms",  # Major microspecies at given pH.
        "--majortautomer",  # Take the major tautomeric form.
        "true",
        "--pH",  # Get the major microspecies at this pH.
        str(mid_ph),
    ]

    input = "\n".join(molecules["inchi"].tolist())
    output, error = run_cxcalc(input, args)
    with open(f"{str(error_log)}.log", "w") as handle:
        # We skip the unhelpful Java stack traces that occur every second line.
        handle.write("\n".join(error.split("\n")[::2]))

    try:
        output_df = pd.read_table(
            StringIO(output),
            header=0,
            index_col="id",
            delimiter="\t",
            dtype=str,
        )
    except pd.errors.EmptyDataError:
        raise ValueError(f"Empty output from cxcalc for {input}.")

    # We adjust the input index to start at 1 in order to be aligned with the
    # cxcalc standard and error output.
    molecules.index = range(1, 1 + molecules.shape[0])

    # Create a table output of molecules with calculation errors.
    # when only the pka run fails, the return value has "pka:FAILED" in the
    # first column:
    error_mask_pka = (output_df == "pka:FAILED").any(axis=1)

    # when only the majorms run fails, the return value has "majorms:FAILED" in
    # the second column:
    error_mask_majorms = (output_df == "majorms:FAILED").any(axis=1)

    # when both the pKa and major-ms runs fail:
    # The first acidic pKa column is empty if there was an error.
    # The second acidic pKa column contains an error description.
    error_mask_both = output_df["apKa1"].isnull() & output_df["apKa2"].notnull()

    error_mask = error_mask_pka | error_mask_majorms | error_mask_both
    if error_mask.any(axis=0):
        # write the error report to the log file
        error = molecules.copy()
        error["error"] = "PASSED"
        error.loc[output_df[error_mask_pka].index, "error"] = "pka:FAILED"
        error.loc[
            output_df[error_mask_majorms].index, "error"
        ] = "majorms:FAILED"
        error.loc[output_df[error_mask_both].index, "error"] = output_df.loc[
            error_mask_both, "apKa2"
        ]
        error.to_csv(f"{str(error_log)}.tsv", sep="\t")

    # Left join the results on index.
    result = molecules.join(output_df.loc[~error_mask, :], how="left")
    result.rename(columns={"major-ms": "major_ms"}, inplace=True)

    # create a function that retrieves the dissociation constants data from
    # a list. The relevant indices don't start from 0 (since the pKa values are
    # preceded by the columns in the input DataFrame "molecules").
    pka_columns = [f"apKa{i}" for i in range(1, 1 + num_acidic)] + [
        f"bpKa{i}" for i in range(1, 1 + num_basic)
    ]

    return result, pka_columns


def atom_bag_and_charge(molecule: pybel.Molecule) -> Tuple[Dict[str, int], int]:
    """
    Compute the atom bag and the formal charge of a molecule.

    The formal charge is calculated by summing the formal charge of each atom
    in the molecule.

    Parameters
    ----------
    molecule : pybel.Molecule
        A molecule object.

    Returns
    -------
    tuple
        dict
            A dictionary of atom counts.
        int
            The formal charge of the molecule.

    """
    # Make all hydrogens explicit so we can properly count them
    molecule.addh()

    # Count charges and atoms.
    atom_bag = defaultdict(int)
    formal_charge = 0
    for atom in molecule.atoms:
        symbol = periodic_table.GetSymbol(atom.atomicnum)
        atom_bag[symbol] += 1
        formal_charge += atom.formalcharge
    atom_bag = dict(atom_bag)

    num_protons = sum(
        count * periodic_table.GetAtomicNum(elem)
        for elem, count in atom_bag.items()
    )

    atom_bag["e-"] = num_protons - formal_charge
    return atom_bag, formal_charge


def get_microspecies_data(
    row: typing.NamedTuple,
    min_ph: float,
    mid_ph: float,
    max_ph: float,
    pka_columns: List[str],
) -> Tuple[dict, List[dict]]:
    """
    Calculate the microspecies information for a compound (if possible).

    Parameters
    ----------
    row : tuple
        A single row resulting from extending the molecules data frame with
        the ``cxcalc`` results.
    min_ph : float
        The minimal pH to consider.
    mid_ph : float
        The pH for which the major pseudoisomer is calculated.
    max_ph : float
        The maximal pH to consider.
    pka_getter : itemgetter
        A mapping of column indexes to retrieve pKa information from the `row`.

    Returns
    -------
    tuple
        dict
            A mapping for updating a compound with atom bag and dissociation
            constants.
        list
            A list of microspecies mappings for that compound.

    """

    def get_constants(row, pka_columns, min_ph=0.0, max_ph=14.0):
        """Return pKa values within the given pH range and ignore NaNs."""
        p_kas = [getattr(row, col) for col in pka_columns]
        p_kas = map(float, p_kas)
        p_kas = filter(lambda p_ka: min_ph < p_ka < max_ph, p_kas)
        return sorted(p_kas, reverse=True)

    logger.debug(
        "Calculating microspecies for %r - %r.", row.mnx_id, row.major_ms
    )
    dissociation_constants = get_constants(
        row, pka_columns, min_ph=min_ph, max_ph=max_ph
    )
    logger.debug("list of pKas: %r.", dissociation_constants)

    # Compounds for which the major microspecies calculation failed are skipped.
    if pd.isnull(row.major_ms) or row.major_ms == "":
        logger.warning(
            "Failed to calculate major_ms string for %r.", row.mnx_id
        )
        return (
            {
                "id": row.id,
                "atom_bag": {},
                "smiles": None,
                "dissociation_constants": dissociation_constants,
            },
            [],
        )

    molecule = pybel.readstring("smi", row.major_ms)

    atom_bag, major_ms_charge = atom_bag_and_charge(molecule)
    major_ms_num_protons = atom_bag.get("H", 0)
    num_species = len(dissociation_constants) + 1
    # Find the index of the major microspecies, by counting how many pKas there
    # are in the range between the given pH and the maximum (typically, 7 - 14).
    if not dissociation_constants:
        major_ms_index = 0
        num_protons = [major_ms_num_protons]
        charges = [major_ms_charge]
    else:
        major_ms_index = sum(
            (1 for p_ka in dissociation_constants if p_ka > mid_ph)
        )
        num_protons = [
            i - major_ms_index + major_ms_num_protons
            for i in range(num_species)
        ]
        charges = [
            i - major_ms_index + major_ms_charge for i in range(num_species)
        ]

    microspecies = []
    for i, (z, nH) in enumerate(zip(charges, num_protons)):
        is_major = False

        if i == major_ms_index:
            ddg_over_rt = 0.0
            is_major = True
        elif i < major_ms_index:
            ddg_over_rt = sum(dissociation_constants[i:major_ms_index]) * LOG10
        elif i > major_ms_index:
            ddg_over_rt = -sum(dissociation_constants[major_ms_index:i]) * LOG10
        else:
            raise IndexError("Major microspecies index mismatch.")
        microspecies.append(
            {
                "compound_id": row.id,
                "charge": z,
                "number_protons": nH,
                "ddg_over_rt": ddg_over_rt,
                "is_major": is_major,
            }
        )
    return (
        {
            "id": row.id,
            "atom_bag": atom_bag,
            "smiles": row.major_ms,
            "dissociation_constants": dissociation_constants,
        },
        microspecies,
    )
