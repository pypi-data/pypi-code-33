from abc import ABCMeta, abstractmethod

import numpy as np

from chi1chi2.utils.constants import ChiException, simeq

POLAR = "alpha"
HYPER = "beta"
CHI1 = "chi1"
CHI2 = "chi2"

FLOAT_FORMAT = "{: .5f}"


class TensorialProperty(metaclass=ABCMeta):
    @abstractmethod
    def transform(self, rotation):
        pass


class FirstOrdPolTens(TensorialProperty):
    def __init__(self, vector):
        if not type(vector) is np.ndarray and vector.shape != (3,):
            raise ChiException("first order polar tensor should be a one-dimensional numpy array of size 3")
        self.vector = vector

    @classmethod
    def zero(cls):
        return cls(np.zeros(3))

    def transform(self, rotation):
        transformed = np.zeros(3)
        for i in range(3):
            for j in range(3):
                transformed[i] += self.vector[j] * rotation[j, i]
        return Vector(transformed)

    def __eq__(self, other: object) -> bool:
        if other is None or not isinstance(other, FirstOrdPolTens):
            return False
        if other is self:
            return True
        return all(simeq(self.vector[i], other.vector[i]) for i in range(3))

    @classmethod
    def from_line(cls, line: str):
        try:
            return cls(np.array([float(u) for u in line.split()[:3]]))
        except ValueError:
            print(f"reading input for an ion - dipole moment ignored")
            return cls(np.zeros(3))

    def __repr__(self):
        return ' '.join(str(FLOAT_FORMAT.format(u)) for u in self.vector) + '\n'


class Vector(FirstOrdPolTens):
    pass


class PermanentPolarization(FirstOrdPolTens):
    def __repr__(self):
        # not implemented, used as a stub for title of bulk properties
        return "bulk properties\n"


class SecOrdPolTen(TensorialProperty):
    def __init__(self, tensor, name):
        if not type(tensor) is np.ndarray and tensor.shape != (3, 3):
            raise ChiException("second-order tensor should be two-dimensional numpy array of size (3, 3)")
        self.tensor = tensor
        self.name = name

    def transform(self, rotation):
        transformed = np.zeros((3, 3))
        for i in range(3):
            for j in range(3):
                for k in range(3):
                    for l in range(3):
                        transformed[i, j] += self.tensor[k, l] * rotation[k, i] * rotation[l, j]
        return SecOrdPolTen(transformed, self.name)

    def __eq__(self, other: object) -> bool:
        if other is None or not isinstance(other, SecOrdPolTen):
            return False
        if other is self:
            return True
        return all(simeq(self.tensor.reshape(9)[i], other.tensor.reshape(9)[i]) for i in range(9))

    @classmethod
    def from_lines(cls, lines: list):
        if len(lines) != 3:
            raise ChiException("wrong number of lines for reading second-order tensor")
        raw_polar = []
        for i in range(3):
            raw_polar.extend(float(u) for u in lines[i].split()[:3])
        return cls(np.array(raw_polar).reshape((3, 3)))

    def __repr__(self):
        lines = ""
        for i in range(3):
            lines += ' '.join(str((FLOAT_FORMAT.format(u))) for u in self.tensor[i, :]) + '\n'
        return lines

    @classmethod
    def zero(cls, name):
        return cls(np.zeros(9).reshape((3, 3)), name)


class Polar(SecOrdPolTen):
    def __init__(self, tensor):
        super().__init__(tensor, POLAR)

    def to_distributed(self, N: int):
        partial_polar = Polar(self.tensor / N)
        return DistributedPolar([partial_polar for i in range(N)])

    def transform(self, rotation):
        return Polar(super().transform(rotation).tensor)


class Chi(SecOrdPolTen):
    def __init__(self, tensor):
        super().__init__(tensor, CHI1)

    def transform(self, rotation):
        return Chi(super().transform(rotation).tensor)


class DistributedPolar(TensorialProperty):
    def __init__(self, polar_list):
        self.polar_list = polar_list

    @classmethod
    def from_file(cls, file):
        with open(file) as f:
            lines = f.readlines()
        polar_list = []
        for line in lines:
            tokens = line.split()
            raw_polar = np.zeros((3, 3))
            for i in range(3):
                raw_polar[i, i] = float(tokens[i + 3])
            raw_polar[0, 1] = np.average([float(tokens[u]) for u in (6, 7)])
            raw_polar[1, 0] = raw_polar[0, 1]
            raw_polar[0, 2] = np.average([float(tokens[u]) for u in (8, 9)])
            raw_polar[2, 0] = raw_polar[0, 2]
            raw_polar[1, 2] = np.average([float(tokens[u]) for u in (10, 11)])
            raw_polar[2, 1] = raw_polar[1, 2]
            polar_list.append(Polar(raw_polar))
        return cls(polar_list)

    def to_molecular_polar(self):
        return Polar(sum(u.tensor for u in self.polar_list))

    def transform(self, rotation):
        return DistributedPolar([polar.transform(rotation) for polar in self.polar_list])


class ThirdOrdPolarTensor(TensorialProperty):
    def __init__(self, tensor, name):
        if not type(tensor) is np.ndarray and tensor.shape != (3, 3, 3):
            raise ChiException("third order tensor should be three-dimensional numpy array of size (3, 3, 3)")
        self.tensor = tensor
        self.name = name

    def transform(self, rotation):
        transformed = np.zeros((3, 3, 3))
        for i in range(3):
            for j in range(3):
                for k in range(3):
                    for l in range(3):
                        for m in range(3):
                            for n in range(3):
                                transformed[i, j, k] += self.tensor[l, m, n] * rotation[l, i] * rotation[
                                    m, j] * rotation[n, k]
        return ThirdOrdPolarTensor(transformed, self.name)

    def __eq__(self, other: object) -> bool:
        if other is None or not isinstance(other, ThirdOrdPolarTensor):
            return False
        if other is self:
            return True
        return all(simeq(self.tensor.reshape(27)[i], other.tensor.reshape(27)[i]) for i in
                   range(27))

    @classmethod
    def from_lines(cls, lines: list):
        if len(lines) != 9:
            raise ChiException("wrong number of lines for reading of third-order polar tensor")
        raw_hyper = []
        for i in range(9):
            raw_hyper.extend(float(u) for u in lines[i].split()[:3])
        return cls(np.array(raw_hyper).reshape((3, 3, 3)))

    def __repr__(self):
        lines = ""
        for i in range(3):
            for j in range(3):
                lines += ' '.join(str((FLOAT_FORMAT.format(u))) for u in self.tensor[i, j, :]) + '\n'
        return lines

    @classmethod
    def zero(cls, name):
        return cls(np.zeros(27).reshape((3, 3, 3)), name)


class Hyper(ThirdOrdPolarTensor):
    def __init__(self, tensor):
        super().__init__(tensor, CHI2)

    def transform(self, rotation):
        return Hyper(super().transform(rotation).tensor)

    def to_distributed(self, N: int):
        partial_hyper = Hyper(self.tensor / N)
        return DistributedHyper([partial_hyper for i in range(N)])


class Chi2(ThirdOrdPolarTensor):
    def __init__(self, tensor):
        super().__init__(tensor, CHI2)

    def transform(self, rotation):
        return Chi2(super().transform(rotation).tensor)


class DistributedHyper(TensorialProperty):
    def __init__(self, hyper_list):
        self.hyper_list = hyper_list

    def to_molecular_hyper(self):
        return Hyper(sum(u.tensor for u in self.hyper_list))

    def transform(self, rotation):
        return DistributedHyper([hyper.transform(rotation) for hyper in self.hyper_list])


class Lorentz:
    def __init__(self, lorentz_tensor: np.array):
        if lorentz_tensor.shape[0] != lorentz_tensor.shape[1]:
            raise ChiException(f"Lorentz tensor should be a square matrix! Actual shape {lorentz_tensor.shape[0]} x "
                               f"{lorentz_tensor.shape[1]}")
        self.lorentz_tensor = lorentz_tensor
        self.dimension = lorentz_tensor.shape[0]

    @classmethod
    def from_file(cls, file):
        with open(file) as f:
            lines = f.readlines()
        if lines[1].find("results not fully converged") > -1:
            raise ChiException("Lorentz tensor not converged, most problem with input, if OK increase r_cut")
        current_line = 2
        l_tmp = []
        while current_line < len(lines):
            l_tmp.append(_get_tensor_from_line(lines[current_line]))
            current_line += 1
        number_of_submolecules = _get_number_of_submolecules(len(l_tmp))
        L = np.zeros((number_of_submolecules * 3, number_of_submolecules * 3))
        current_lorentz_ind = 0
        for i in range(number_of_submolecules):
            for j in range(i, number_of_submolecules):
                L[3 * i:3 * (i + 1), 3 * j:3 * (j + 1)] = l_tmp[current_lorentz_ind][:, :]
                if i != j:
                    L[3 * j:3 * (j + 1), 3 * i:3 * (i + 1)] = l_tmp[current_lorentz_ind][:, :]
                current_lorentz_ind += 1
        return cls(L)

    def __eq__(self, other):
        if other is None or not isinstance(other, Lorentz):
            return False
        if other is self:
            return True
        dimsq = self.dimension ** 2
        return all([simeq(self.lorentz_tensor.reshape(dimsq)[i], other.lorentz_tensor.reshape(dimsq)[i]) for i in
                    range(dimsq)])


def _get_tensor_from_line(line):
    L = np.zeros((3, 3))
    indices = ((0, 0), (1, 1), (2, 2), (0, 1), (0, 2), (1, 2))
    tokens = line.split()[:6]
    for i, tk in enumerate(indices):
        L[indices[i]] = float(tokens[i])
    for ind in ((0, 1), (0, 2), (1, 2)):
        L[ind[1], ind[0]] = L[ind[0], ind[1]]
    return L


def _get_number_of_submolecules(number_of_lines: int) -> int:
    return int((np.sqrt(1 + 8 * number_of_lines) - 1) / 2)
