from abc import abstractmethod, ABCMeta
from itertools import chain
from typing import List

from chi1chi2.core.property import Vector, Polar, Hyper, FirstOrdPolTens, SecOrdPolTen, ThirdOrdPolarTensor, Chi, Chi2, \
    PermanentPolarization, POLAR, HYPER
from chi1chi2.utils.constants import ChiException

STATIC_LIMIT = "static"
ETIQ_FORMAT = "{:.1f}"


class PropsWGen:
    def __init__(self, wave_length, polar_w: SecOrdPolTen, polar_2w: SecOrdPolTen, hyper_w: ThirdOrdPolarTensor):
        self.wave_length = wave_length
        self.polar_w = polar_w
        self.polar_2w = polar_2w
        self.hyper_w = hyper_w

    @classmethod
    def in_static_limit(cls, polar: SecOrdPolTen, hyper: ThirdOrdPolarTensor):
        return cls(STATIC_LIMIT, polar, polar, hyper)

    @classmethod
    def zero(cls, wave_length, lin_name, nlin_name):
        return cls(wave_length, SecOrdPolTen.zero(lin_name), SecOrdPolTen.zero(lin_name),
                   ThirdOrdPolarTensor.zero(nlin_name))

    def __repr__(self):
        lines = self.wave_length + '\n'
        lines += str(self.polar_w) + '\n'
        if self.wave_length != STATIC_LIMIT:
            lines += str(self.polar_2w) + '\n'
        lines += str(self.hyper_w) + '\n'
        return lines


class PropsWMol(PropsWGen):
    def __init__(self, wave_length, polar_w: Polar, polar_2w: Polar, hyper_w: Hyper):
        super().__init__(wave_length, polar_w, polar_2w, hyper_w)


class PropsWBulk(PropsWGen):
    def __init__(self, wave_length, polar_w: Chi, polar_2w: Chi, hyper_w: Chi2):
        super().__init__(wave_length, polar_w, polar_2w, hyper_w)


class PropsGen(metaclass=ABCMeta):
    def __init__(self, dipole_moment: FirstOrdPolTens, props_list: List[PropsWGen]):
        self.dipole_moment = dipole_moment
        self.props_dict = {prop.wave_length: prop for prop in props_list}
        self.wave_lengths = list(u.wave_length for u in props_list)

    def is_defined_for_wavelength(self, wave_length):
        return wave_length in self.props_dict

    def get_or_static(self, wave_length):
        if not self.is_defined_for_wavelength(wave_length):
            print(f"falling back to the static limit for wavelength {wave_length}")
            return self.props_dict.get("static")
        else:
            return self.props_dict.get(wave_length)

    @classmethod
    @abstractmethod
    def from_file(cls, file):
        pass  # TODO: figure out how to use polymorphism for this method...

    def __repr__(self):
        lines = str(self.dipole_moment)
        for prop in self.props_dict.values():
            lines += str(prop)

        return lines


class PropsMol(PropsGen):
    def __init__(self, dipole_moment: Vector, props_list: List[PropsWMol]):
        super().__init__(dipole_moment, props_list)

    @classmethod
    def from_file(cls, file):
        with open(file) as f:
            lines = f.readlines()
        dipole = Vector.from_line(lines[0])
        current_line = 1
        properties = []
        try:
            while current_line < len(lines):
                et = lines[current_line].split()[1]
                current_line += 1
                if et == STATIC_LIMIT:
                    polar = Polar.from_lines(lines[current_line: current_line + 3])
                    current_line += 4
                    _get_etiq_verify(et, lines[current_line])
                    current_line += 1
                    hyper = Hyper.from_lines(lines[current_line: current_line + 9])
                    properties.append(PropsWMol.in_static_limit(polar, hyper))
                    current_line += 9
                else:
                    polar_w = Polar.from_lines(lines[current_line: current_line + 3])
                    current_line += 4
                    _get_etiq_verify(halve_etiq(et), lines[current_line])
                    current_line += 1
                    polar_2w = Polar.from_lines(lines[current_line: current_line + 3])
                    current_line += 4
                    _get_etiq_verify(et, lines[current_line])
                    current_line += 1
                    hyper_w = Hyper.from_lines(lines[current_line: current_line + 9])
                    current_line += 9
                    properties.append(PropsWMol(et, polar_w, polar_2w, hyper_w))
                current_line += 1
        except Exception as e:
            print(f"malformed or cut property file: {e}, line number: {current_line}")
        return cls(dipole, properties)


def halve_etiq(et):
    if et == STATIC_LIMIT:
        return et
    return ETIQ_FORMAT.format(float(et) / 2)


def _get_etiq_verify(et, line):
    et2 = line.split()[1]
    if et != et2:
        raise ChiException(f"etiquette mismatch: found {et2}, expected {et}")


class PropsBulk(PropsGen):
    def __init__(self, dipole_moment: PermanentPolarization, props_list: List[PropsWBulk]):
        super().__init__(dipole_moment, props_list)

    @classmethod
    def from_file(cls, file):
        with open(file) as f:
            lines = f.readlines()
        dipole = PermanentPolarization.from_line(lines[0])
        current_line = 1
        properties = []
        try:
            while current_line < len(lines):
                et = lines[current_line].strip()
                current_line += 1
                if et == STATIC_LIMIT:
                    polar = Chi.from_lines(lines[current_line: current_line + 3])
                    current_line += 4
                    hyper = Chi2.from_lines(lines[current_line: current_line + 9])
                    properties.append(PropsWMol.in_static_limit(polar, hyper))
                    current_line += 9
                else:
                    polar_w = Chi.from_lines(lines[current_line: current_line + 3])
                    current_line += 4
                    polar_2w = Chi.from_lines(lines[current_line: current_line + 3])
                    current_line += 4
                    hyper_w = Chi2.from_lines(lines[current_line: current_line + 9])
                    current_line += 9
                    properties.append(PropsWMol(et, polar_w, polar_2w, hyper_w))
                current_line += 1
        except Exception as e:
            print(f"malformed or cut property file: {e}, line number: {current_line}")
        return cls(dipole, properties)


def equalize_properties(list_properties, use_static=False):
    """
    checks properties for each wavelength and adds "sero" fo rthe missing ones
    :param list_properties:
    :return: equalized_properties
    """
    equalized_properties = []
    all_wave_lengths = list(set(chain.from_iterable(p.wave_lengths for p in list_properties)))
    all_wave_lengths.remove("static")
    final_wave_lengths = ["static"]
    final_wave_lengths.extend(sorted(all_wave_lengths, key=lambda x: float(x), reverse=True))
    for i in range(len(list_properties)):
        tmp_props = []
        for wave_length in final_wave_lengths:
            if not use_static:
                if list_properties[i].is_defined_for_wavelength(wave_length):
                    tmp_props.append(list_properties[i].get_or_static(wave_length))
                else:
                    tmp_props.append(PropsWMol.zero(wave_length, POLAR, HYPER))
            else:
                tmp_props.append(list_properties[i].get_or_static(wave_length))
        equalized_properties.append(PropsMol(list_properties[i].dipole_moment, tmp_props))
    return final_wave_lengths, equalized_properties
