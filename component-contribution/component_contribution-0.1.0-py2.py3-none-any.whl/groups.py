import json
import logging

import numpy as np
import pandas as pd
import quilt.data.equilibrator.component_contribution

from .molecule import Molecule


class GroupVector(list):
    """A vector of groups."""

    def __init__(self, groups_data, iterable=None):
        """Construct a vector.

        Args:
            groups_data: data about all the groups.
            iterable: data to load into the vector.
        """
        self.groups_data = groups_data

        if iterable is not None:
            self.extend(iterable)
        else:
            for _ in range(len(self.groups_data.all_group_names)):
                self.append(0)

    def __str__(self):
        """Return a sparse string representation of this group vector."""
        group_strs = []
        gv_flat = self.flat
        for i, name in enumerate(self.groups_data.GetGroupNames()):
            if gv_flat[i]:
                group_strs.append('%s x %d' % (name, gv_flat[i]))
        return " | ".join(group_strs)

    def __iadd__(self, other):
        for i in range(len(self.groups_data.all_group_names)):
            self[i] += other[i]
        return self

    def __isub__(self, other):
        for i in range(len(self.groups_data.all_group_names)):
            self[i] -= other[i]
        return self

    def __add__(self, other):
        result = GroupVector(self.groups_data)
        for i in range(len(self.groups_data.all_group_names)):
            result[i] = self[i] + other[i]
        return result

    def __sub__(self, other):
        result = GroupVector(self.groups_data)
        for i in range(len(self.groups_data.all_group_names)):
            result[i] = self[i] - other[i]
        return result

    def __eq__(self, other):
        for i in range(len(self.groups_data.all_group_names)):
            if self[i] != other[i]:
                return False
        return True

    def __nonzero__(self):
        for i in range(len(self.groups_data.all_group_names)):
            if self[i] != 0:
                return True
        return False

    def __mul__(self, other):
        try:
            c = float(other)
            return GroupVector(self.groups_data, [x*c for x in self])
        except ValueError:
            raise ValueError("A GroupVector can only be multiplied by a scalar"
                             ", given " + str(other))

    def NetCharge(self):
        """Returns the net charge."""
        return int(np.dot(self, self.groups_data.all_group_charges))

    def Hydrogens(self):
        """Returns the number of protons."""
        return int(np.dot(self, self.groups_data.all_group_hydrogens))

    def Magnesiums(self):
        """Returns the number of Mg2+ ions."""
        return int(np.dot(self, self.groups_data.all_group_mgs))

    def RemoveEpsilonValues(self, epsilon=1e-10):
        for i in range(len(self)):
            if abs(self[i]) < epsilon:
                self[i] = 0

    def ToJSONString(self):
        return json.dumps(dict([(i, x) for (i, x) in enumerate(self) if x != 0]))

    @staticmethod
    def FromJSONString(groups_data, s):
        v = [0] * groups_data.Count()
        for i, x in json.loads(s).items():
            v[int(i)] = x
        return GroupVector(groups_data, v)

    @property
    def flat(self):
        if not self.groups_data.transformed:
            return tuple(self)

        # map all pseudoisomeric group indices to Biochemical group indices (which are fewer)
        # use the names of each group and ignore the nH, z and nMg.
        biochemical_group_names = self.groups_data.GetGroupNames()
        biochemical_vector = [0] * len(biochemical_group_names)
        for i, x in enumerate(self):
            group_name = self.groups_data.all_groups[i].name
            new_index = biochemical_group_names.index(group_name)
            biochemical_vector[new_index] += x
        return tuple(biochemical_vector)

    def as_array(self):
        return np.array(self.flat)

class GroupsDataError(Exception):
    pass

class MalformedGroupDefinitionError(GroupsDataError):
    pass

class _AllAtomsSet(object):
    """A set containing all the atoms: used for focal atoms sets."""

    def __contains__(self, elt):
        return True

class FocalSet(object):

    def __init__(self, focal_atoms_str):
        if not focal_atoms_str:
            raise ValueError(
                'You must supply a non-empty focal atom string.'
                ' You may use "None" or "All" in the obvious fashion.')

        self.str = focal_atoms_str
        self.focal_atoms_set = None
        prepped_str = self.str.strip().lower()

        if prepped_str == 'all':
            self.focal_atoms_set = _AllAtomsSet()
        elif prepped_str == 'none':
            self.focal_atoms_set = set()
        else:
            self.focal_atoms_set = set([int(c) for c in self.str.split('|')])

    def __str__(self):
        return self.str

    def __contains__(self, elt):
        return self.focal_atoms_set.__contains__(elt)

class Group(object):
    """Representation of a single group."""

    def __init__(self, group_id, name, hydrogens, charge, nMg,
                 smarts=None, focal_atoms=None):
        self.id = group_id
        self.name = name
        self.hydrogens = hydrogens
        self.charge = charge
        self.nMg = nMg
        self.smarts = smarts
        self.focal_atoms = focal_atoms

    def _IsHydrocarbonGroup(self):
        return self.name.startswith('*Hc')

    def _IsSugarGroup(self):
        return self.name.startswith('*Su')

    def _IsAromaticRingGroup(self):
        return self.name.startswith('*Ar')

    def _IsHeteroaromaticRingGroup(self):
        return self.name.startswith('*Har')

    def IsPhosphate(self):
        return self.name.startswith('*P')

    def IgnoreCharges(self):
        # (I)gnore charges
        return self.name[2] == 'I'

    def ChargeSensitive(self):
        # (C)harge sensitive
        return self.name[2] == 'C'

    def IsCodedCorrection(self):
        """Returns True if this is a correction for which hand-written code.
           must be executed.
        """
        return (self._IsHydrocarbonGroup() or
                self._IsAromaticRingGroup() or
                self._IsHeteroaromaticRingGroup())

    @staticmethod
    def _IsHydrocarbon(mol):
        """Tests if a molecule is a simple hydrocarbon."""
        if mol.FindSmarts('[!C;!c]'):
            # If we find anything other than a carbon (w/ hydrogens)
            # then it's not a hydrocarbon.
            return 0
        return 1

    @staticmethod
    def _CountAromaticRings(mol):
        expressions = ['c1cccc1', 'c1ccccc1']
        count = 0
        for smarts_str in expressions:
            count += len(mol.FindSmarts(smarts_str))
        return count

    @staticmethod
    def _CountHeteroaromaticRings(mol):
        expressions = ['a1aaaa1', 'a1aaaaa1']
        count = 0
        all_atoms = mol.GetAtoms()
        for smarts_str in expressions:
            for match in mol.FindSmarts(smarts_str):
                atoms = set([all_atoms[i].atomicnum for i in match])
                atoms.discard(6)  # Ditch carbons
                if atoms:
                    count += 1
        return count

    def GetCorrection(self, mol):
        """Get the value of the correction for this molecule."""
        if self._IsHydrocarbonGroup():
            return self._IsHydrocarbon(mol)
        elif self._IsAromaticRingGroup():
            return self._CountAromaticRings(mol)
        elif self._IsHeteroaromaticRingGroup():
            return self._CountHeteroaromaticRings(mol)

        raise TypeError('This group is not a correction.')

    def FocalSet(self, nodes):
        """Get the set of focal atoms from the match.

        Args:
            nodes: the nodes matching this group.

        Returns:
            A set of focal atoms.
        """
        focal_set = set()
        for i, node in enumerate(nodes):
            if i in self.focal_atoms:
                focal_set.add(node)
        return focal_set

    def __str__(self):
        if self.hydrogens is not None and self.charge is not None and self.nMg is not None:
            return '%s [H%d Z%d Mg%d]' % \
                (self.name, self.hydrogens or 0, self.charge or 0, self.nMg or 0)
        else:
            return '%s' % self.name

    def __eq__(self, other):
        """Enable == checking.

        Only checks name, protons, charge, and nMg.
        """
        return (str(self.name) == str(other.name) and
                self.hydrogens == other.hydrogens and
                self.charge == other.charge and
                self.nMg == other.nMg)

    def __hash__(self):
        """We are HASHABLE!

        Note that the hash depends on the same attributes that are checked for equality.
        """
        return hash((self.name, self.hydrogens, self.charge, self.nMg))


class GroupsData(object):
    """Contains data about all groups."""

    ORIGIN = Group('Origin', 'Origin', hydrogens=0, charge=0, nMg=0)

    # Phosphate groups need special treatment, so they are defined in code...
    # TODO(flamholz): Define them in the groups file.

    # each tuple contains: (name, description, nH, charge, nMg, is_default)

    phosphate_groups = [('initial H0', '-OPO3-', 0, -1, 0, True),
                        ('initial H1', '-OPO3-', 1, 0, 0, False),
                        ('middle H0', '-OPO2-', 0, -1, 0, True),
                        ('middle H1', '-OPO2-', 1, 0, 0, False),
                        ('final H0', '-OPO3', 0, -2, 0, True),
                        ('final H1', '-OPO3', 1, -1, 0, False),
                        ('final H2', '-OPO3', 2, 0, 0, False),
                        ('initial chain H0', '-OPO3-OPO2-', 0, -2, 0, True),
                        ('initial chain H1', '-OPO3-OPO2-', 1, -1, 0, False),
                        ('initial chain H2', '-OPO3-OPO2-', 2, 0, 0, False),
                        ('initial chain Mg1', '-OPO3-OPO2-', 0, 0, 1, False),
                        ('middle chain H0', '-OPO2-OPO2-', 0, -2, 0, True),
                        ('middle chain H1', '-OPO2-OPO2-', 1, -1, 0, False),
                        ('middle chain H2', '-OPO2-OPO2-', 2, 0, 0, False),
                        ('middle chain Mg1', '-OPO2-OPO2-', 0, 0, 1, False),
                        ('ring initial H0', 'ring -OPO3-', 0, -1, 0, True),
                        ('ring initial H1', 'ring -OPO3-', 1, 0, 0, False),
                        ('ring initial chain H0', 'ring -OPO3-OPO2-', 0, -2, 0, True),
                        ('ring initial chain H1', 'ring -OPO3-OPO2-', 1, -1, 0, False),
                        ('ring initial chain H2', 'ring -OPO3-OPO2-', 2, 0, 0, False),
                        ('ring middle chain H0', 'ring -OPO2-OPO2-', 0, -2, 0, True),
                        ('ring middle chain H1', 'ring -OPO2-OPO2-', 1, -1, 0, False),
                        ('ring middle chain H2', 'ring -OPO2-OPO2-', 2, 0, 0, False),
                        ('ring initial chain Mg1', 'ring -OPO2-OPO2-', 0, 0, 1, False)]

    PHOSPHATE_GROUPS = []
    PHOSPHATE_DICT = {}
    DEFAULTS = {}
    for name, desc, nH, z, nMg, is_default in phosphate_groups:
        group = Group(name, desc, nH, z, nMg)
        PHOSPHATE_GROUPS.append(group)
        PHOSPHATE_DICT[name] = group
        if is_default:
            DEFAULTS[desc] = group

    RING_PHOSPHATES_TO_MGS = ((PHOSPHATE_DICT['ring initial chain H0'], PHOSPHATE_DICT['ring initial chain Mg1']),)
    MIDDLE_PHOSPHATES_TO_MGS = ((PHOSPHATE_DICT['initial chain H0'], PHOSPHATE_DICT['initial chain Mg1']),)
    FINAL_PHOSPHATES_TO_MGS = ((PHOSPHATE_DICT['middle chain H0'], PHOSPHATE_DICT['middle chain Mg1']),)

    def __init__(self, groups, transformed=False):
        """Construct GroupsData.

        Args:
            groups: a list of Group objects.
        """
        self.transformed = transformed
        self.groups = groups
        self.all_groups = self._GetAllGroups(self.groups)
        self.all_group_names = [str(g) for g in self.all_groups]
        self.all_group_hydrogens = np.array([g.hydrogens or 0 for g in self.all_groups])
        self.all_group_charges = np.array([g.charge or 0 for g in self.all_groups])
        self.all_group_mgs = np.array([g.nMg or 0 for g in self.all_groups])

        if self.transformed:
            # find the unique group names (ignoring nH, z, nMg)
            # note that Group.name is does not contain these values,
            # unlike Group.__str__() which concatenates the name and the nH, z, nMg
            self.biochemical_group_names = []
            for group in self.all_groups:
                if group.name not in self.biochemical_group_names:
                    self.biochemical_group_names.append(group.name)

    def Count(self):
        return len(self.all_groups)

    count = property(Count)

    @staticmethod
    def _GetAllGroups(groups):
        all_groups = []

        for group in groups:
            # Expand phosphate groups.
            if group.IsPhosphate():
                all_groups.extend(GroupsData.PHOSPHATE_GROUPS)
            else:
                all_groups.append(group)

        # Add the origin.
        all_groups.append(GroupsData.ORIGIN)
        return all_groups

    @staticmethod
    def _ConvertFocalAtoms(focal_atoms_str):
        if not focal_atoms_str:
            return _AllAtomsSet()
        if focal_atoms_str.lower().strip() == 'none':
            return set()

        return set([int(c) for c in focal_atoms_str.split('|')])

    @staticmethod
    def FromDataFrame(gr_def_df: pd.DataFrame,
                      transformed: bool = False) -> object:
        """Factory that initializes a GroupData from a DataFrame."""
        list_of_groups = []
        for row in gr_def_df.itertuples(index=True):
            logging.debug('Reading group definition for ' + row.NAME)
            smarts = row.SMARTS
            focal_atoms = FocalSet(row.FOCAL_ATOMS)
            # remark = row['REMARK']

            # Check that the smarts are good.
            if not Molecule.VerifySmarts(smarts):
                raise GroupsDataError('Cannot parse SMARTS expression: %s' %
                                      row.SMARTS)

            group = Group(row.Index, row.NAME, row.PROTONS, row.CHARGE,
                          row.MAGNESIUMS, row.SMARTS,
                          focal_atoms)
            list_of_groups.append(group)

        logging.debug('Done reading groups data.')

        return GroupsData(list_of_groups, transformed)

    @staticmethod
    def FromGroupsFile(file, transformed: bool = False) -> object:
        """Factory that initializes a GroupData from a CSV file."""
        assert file
        gr_def_df = pd.read_csv(file, index_col=None, header=0)
        return GroupsData.FromDataFrame(gr_def_df, transformed)

    def Index(self, gr):
        try:
            return self.all_groups.index(gr)
        except ValueError:
            raise ValueError('group %s is not defined' % str(gr))

    def GetGroupNames(self):
        if self.transformed:
            return self.biochemical_group_names
        else:
            return self.all_group_names



DEFAULT_GROUPS_DATA = GroupsData.FromDataFrame(
    quilt.data.equilibrator.component_contribution.train.group_definitions(),
    transformed=False)
