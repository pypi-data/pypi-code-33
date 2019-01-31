import re
from collections import namedtuple
from enum import Enum
from fractions import Fraction
from pathlib import Path

import numpy as np

PI = np.pi
PI2 = PI / 2

TOLERANCE = 1e-5
HYDROGEN_TOLERANCE = 1.15
XYZ_EXTENSION = ".xyz"
INP_EXTENSION = ".inp"
FRA_EXTENSION = ".fra"

INP_FILENAME_PATTERN = re.compile(r"(.*)(\.inp)$")
FRA_FILENAME_PATTERN = re.compile(r"(.*)(\.fra)$")
CIF_FILENAME_PATTERN = re.compile(r"(.*)(\.cif)$")

_Params_tuple = namedtuple('Params', "a, b, c, al, be, ga")

ZERO_TRANSLATION = np.zeros((3, 1)).reshape((3, 1))


class ChiException(Exception):
    pass


class SymmopParsingException(ChiException):
    pass


class Params(_Params_tuple):
    @classmethod
    def from_line(cls, line, is_tetragonal=False):
        param_list = line.split()
        param_list_length = len(param_list)
        if param_list_length == 1:
            a = float(param_list[0])
            return cls.orthogonal(a, a, a)
        elif param_list_length == 2 and not is_tetragonal:
            print("assuming hexagonal system, make sure it is not a tetragonal!")
            a = float(param_list[0])
            c = float(param_list[1])
            return cls(a, a, c, PI2, PI2, PI2 * 4. / 3.)
        elif param_list_length == 2 and is_tetragonal:
            a = float(param_list[0])
            b = float(param_list[1])
            return cls.orthogonal(a, b, b)
        elif param_list_length == 3:
            a = float(param_list[0])
            b = float(param_list[1])
            c = float(param_list[2])
            return cls.orthogonal(a, b, c)
        elif param_list_length == 4:
            a = float(param_list[0])
            b = float(param_list[1])
            c = float(param_list[2])
            be = PI / 180. * float(param_list[3])
            return cls.monoclinic(a, b, c, be)
        elif param_list_length == 6:
            lengths = [float(u) for u in param_list[:3]]
            angles = [PI / 180. * float(u) for u in param_list[3:6]]
            return cls(*lengths, *angles)
        return None

    @classmethod
    def default(cls):
        return cls(1, 1., 1., PI2, PI2, PI2)

    @classmethod
    def orthogonal(cls, a, b, c):
        return cls(a, b, c, PI2, PI2, PI2)

    @classmethod
    def monoclinic(cls, a, b, c, be):
        return cls(a, b, c, PI2, be, PI2)

    def volume(self):
        a, b, c, al, be, ga = self.a, self.b, self.c, self.al, self.be, self.ga
        G = np.zeros((3, 3))
        G[0, 0] = a ** 2.
        G[1, 1] = b ** 2.
        G[2, 2] = c ** 2.
        G[0, 1] = a * b * np.cos(ga)
        G[0, 2] = a * c * np.cos(be)
        G[1, 2] = b * c * np.cos(al)
        G[1, 0] = G[0, 1]
        G[2, 0] = G[0, 2]
        G[2, 1] = G[1, 2]
        return np.sqrt(float(np.linalg.det(G)))

    def __eq__(self, other):
        return simeq(self.a, other.a) and \
               simeq(self.b, other.b) and \
               simeq(self.c, other.c) and \
               simeq(self.al, other.al) and \
               simeq(self.be, other.be) and \
               simeq(self.ga, other.ga)

    def __repr__(self):
        line = " ".join(str(u) for u in (self.a, self.b, self.c)) + " "
        line += " ".join(str(round(180 / PI * float(u), 5)) for u in (self.al, self.be, self.ga))
        return line


class Symmop:
    def __init__(self, rotation, translation):
        self.rotation = rotation
        self.translation = translation

    @classmethod
    def no_translation(cls, rotation):
        return cls(rotation, ZERO_TRANSLATION)

    @classmethod
    def only_translation(cls, translation):
        return cls(np.identity(3), translation)

    @classmethod
    def identity(cls):
        return cls(np.identity(3), ZERO_TRANSLATION)

    @classmethod
    def from_line(cls, line):
        tokens = [tk.strip().replace(' ', '') for tk in line.strip('\'\"').split(',')]
        if len(tokens) != 3:
            raise SymmopParsingException("symmetry operation notation error!", line)
        rotation = np.zeros((3, 3))
        translation = np.zeros((3, 1))
        for i in range(3):
            token = tokens[i]
            token_pattern1 = re.compile(r'(-?[xyz](?:[-+][xyz])*)([-+/\d]*)')
            token_pattern2 = re.compile(r'([-+/\d]*)([-+][xyz](?:[-+][xyz])*)')
            match1 = token_pattern1.match(token)
            match2 = token_pattern2.match(token)
            if match1 is not None:
                rotation_part = match1.group(1)
                translation_part = match1.group(2)
            elif match2 is not None:
                rotation_part = match2.group(2)
                translation_part = match2.group(1)
            else:
                raise SymmopParsingException("malformed symmetry operation or notation error, check this: " + token)
            for j, tk in enumerate(('x', 'y', 'z')):
                tk_ind = rotation_part.find(tk)
                if tk_ind != rotation_part.rfind(tk):
                    raise SymmopParsingException("found two occurences of token" + tk + " in: " + rotation_part)
                if tk_ind > -1:
                    if tk_ind > 0:
                        rotation[i, j] = -1 if rotation_part[tk_ind - 1] == '-' else 1
                    else:
                        rotation[i, j] = 1
            if len(translation_part) > 0:
                translation[i, 0] = eval(translation_part)
        return cls(rotation, translation)

    def to_line(self):
        XYZ_TOKENS = ('x', 'y', 'z')
        tokens = []
        for i in range(3):
            rot = self.rotation[i, :]
            tr = self.translation[i, 0]
            tk = ""
            for j in range(3):
                sgn = np.sign(rot[j])
                if sgn < 0:
                    tk += '-' + XYZ_TOKENS[j]
                elif sgn > 0 and len(tk) > 0:
                    tk += '+' + XYZ_TOKENS[j]
                elif sgn > 0:
                    tk += XYZ_TOKENS[j]
            if not simeq(tr, 0):
                sgn = np.sign(tr)
                if sgn > 0:
                    tk += '+'
                tk += str(Fraction(tr).limit_denominator())
            tokens.append(tk)
        return ", ".join(tokens)

    def __repr__(self):
        lines = ""
        for i in range(3):
            lines += " ".join(str(self.rotation[i, j]) for j in range(3))
            lines += " " + str(self.translation[i, 0]) + "\n"
        return lines

    def __eq__(self, other) -> bool:
        return all(self.rotation.reshape(9) == other.rotation.reshape(9)) and \
               all(self.translation == other.translation)


class Unit(Enum):
    """
    a simple enum with converter to Angstrom
    """
    Angstr = (1., 1. / 0.529177249)
    Bohr = (0.529177249, 1.)

    def __init__(self, to_angstr, to_bohr):
        self.__to_angstr = to_angstr
        self.__to_bohr = to_bohr

    def to_angstrom(self):
        return self.__to_angstr

    def to_bohr(self):
        return self.__to_bohr


def simeq(par1, par2, tolerance=TOLERANCE):
    return abs(par1 - par2) < tolerance


def resolve_path(other_file_name, pattern, extension):
    """
    produces path to new file based on another file
    :param other_file_name: reference file
    :param pattern: 2-group regex capturing filename and extension
    :param extension: new extension, example: ".fra"
    :return: resolved path for file with new extension
    """
    cwd = Path.cwd()
    cif_file_name = Path(other_file_name).name
    matcher = pattern.match(cif_file_name)
    if matcher is not None:
        return str(cwd / (matcher.group(1) + extension))
    else:
        return str(cwd / (cif_file_name + "extension"))
