from typing import List

import numpy as np
from numpy.linalg import inv

from chi1chi2.core.property import Lorentz, Chi2, Chi, PermanentPolarization, DistributedPolar, Polar
from chi1chi2.core.property_reader import STATIC_LIMIT, PropsBulk, PropsWBulk, PropsMol
from chi1chi2.input.input_preparator import Input
from chi1chi2.utils.constants import PI, Unit, simeq

# beta 1 au = 3.2063615e-53 C^3m^3J^-2 = 3.62129376e-42 m^4/V = 24.4377019 Bh^3pm/V <- value containing eps_0
BET_MULT = 24.4377019


class BulkProperties:
    def __init__(self, inp: Input, lorentz: Lorentz, wave_lengths, list_properties: List[PropsMol],
                 dist_stat_pols=None):
        self.inp = inp
        self.volume = inp.params.volume() * Unit.Angstr.to_bohr() ** 3.
        self.lorentz = lorentz
        self.wave_lengths = wave_lengths
        self.list_properties = list_properties
        self.dist_stat_pols = dist_stat_pols

    def calc_chis(self, qlft=False):
        props = PropsBulk(PermanentPolarization.zero(), [])
        if qlft and self.dist_stat_pols is None:
            return None
        for wave_length in self.wave_lengths:
            alphas_w = self._get_alphas(wave_length) if not qlft else self._get_alphas_qlft(wave_length)
            alphas_2w = self._get_alphas(wave_length, for_2w=True) if not qlft else self._get_alphas_qlft(wave_length,
                                                                                                          for_2w=True)
            betas = self._get_betas(wave_length)
            d_w = _calc_d(self.volume, self.lorentz.lorentz_tensor, alphas_w)
            if wave_length == STATIC_LIMIT:
                d_2w = d_w
            else:
                d_2w = _calc_d(self.volume, self.lorentz.lorentz_tensor, alphas_2w)
            chi_w, chi_2w = self._calc_chis(alphas_w, alphas_2w, d_w, d_2w)
            chi2_w = self._calc_chi2(betas, d_w, d_2w)
            props.props_dict[wave_length] = PropsWBulk(wave_length, chi_w, chi_2w, chi2_w)
        return props

    def _calc_chi2(self, betas, d_w, d_2w):
        chi2_w = np.zeros((3, 3, 3))
        for i in range(3):
            for j in range(3):
                for k in range(3):
                    for n in range(3):
                        for m in range(3):
                            for o in range(3):
                                for x in range(int(d_w.shape[0] / 3)):
                                    chi2_w[i, j, k] += 0.5 / self.volume * BET_MULT * betas[x].tensor[n, m, o] * d_2w[
                                        3 * x + n, i] * d_w[3 * x + m, j] * d_w[3 * x + o, k]
        return Chi2(chi2_w)

    def _calc_chis(self, alphas_w, alphas_2w, d_w, d_2w):
        chi_w = 4. * PI / self.volume * np.dot(np.hstack(a_w.tensor for a_w in alphas_w), d_w)
        chi_2w = 4. * PI / self.volume * np.dot(np.hstack(a_w.tensor for a_w in alphas_2w), d_2w)
        return Chi(chi_w), Chi(chi_2w)

    def _get_alphas(self, wave_length, for_2w=False):
        return _get_alphas(wave_length, self.list_properties, self.inp.flags, self.inp.symmops, self.inp.asym_groups,
                           for_2w)

    def _get_betas(self, wave_length):
        return _get_betas(wave_length, self.list_properties, self.inp.flags, self.inp.symmops, self.inp.asym_groups)

    def _get_alphas_qlft(self, wave_length, for_2w=False):
        return _get_alphas_qlft(wave_length, self.list_properties, self.inp.flags, self.inp.symmops,
                                self.inp.asym_groups, self.dist_stat_pols, for_2w)


def _get_alphas(wave_length, properties, flags, symmops, asym_groups, for_2w=False):
    alphas = []
    for submol_idx in range(len(properties)):
        prop_sub = properties[submol_idx].get_or_static(wave_length)
        for symmop_idx in range(len(flags[submol_idx])):
            if flags[submol_idx][symmop_idx]:
                if not for_2w:
                    alphas.extend(prop_sub.polar_w.transform(symmops[symmop_idx].rotation).to_distributed(
                        len(asym_groups[submol_idx])).polar_list)
                else:
                    alphas.extend(prop_sub.polar_2w.transform(symmops[symmop_idx].rotation).to_distributed(
                        len(asym_groups[submol_idx])).polar_list)
    return alphas


def _get_alphas_qlft(wave_length, properties, flags, symmops, asym_groups, dist_pols, for_2w=False):
    alphas = []
    for submol_idx in range(len(properties)):
        prop_stat = properties[submol_idx].get_or_static(STATIC_LIMIT)
        prop_sub = properties[submol_idx].get_or_static(wave_length)
        if not for_2w:
            scale = _get_scale(prop_stat.polar_w, prop_sub.polar_w)
        else:
            scale = _get_scale(prop_stat.polar_w, prop_sub.polar_2w)
        for symmop_idx in range(len(flags[submol_idx])):
            if flags[submol_idx][symmop_idx]:
                # rotation =  * scale
                alphas.extend(
                    DistributedPolar([Polar(tens) for tens in
                                      _get_grouped_polars(asym_groups[submol_idx], dist_pols[submol_idx],
                                                          scale)]).transform(symmops[symmop_idx].rotation).polar_list)
    return alphas


def _get_grouped_polars(asym_groups, dist_pols: DistributedPolar, scale):
    polars = []
    current_start = 0
    for i in range(len(asym_groups)):
        current_end = current_start + asym_groups[i]
        polars.append(sum(dist_pols.polar_list[i].tensor for i in range(current_start, current_end)) * scale)
        current_start = current_end
    return polars


def _get_scale(alpha_stat: Polar, alpha_dyn: Polar):
    transformation = np.identity(3)
    for i, j in ((0, 0), (1, 1), (2, 2), (0, 1), (0, 2), (1, 2)):
        if not simeq(alpha_stat.tensor[i, j], 0):
            transformation[i, j] = alpha_dyn.tensor[i, j] / alpha_stat.tensor[i, j]
    for i, j in ((0, 1), (0, 2), (1, 2)):
        transformation[j, i] = transformation[i, j]
    return transformation


def _get_betas(wave_length, properties, flags, symmops, asym_groups):
    betas = []
    for submol_idx in range(len(properties)):
        prop_sub = properties[submol_idx].get_or_static(wave_length)
        for symmop_idx in range(len(flags[submol_idx])):
            if flags[submol_idx][symmop_idx]:
                betas.extend(prop_sub.hyper_w.transform(symmops[symmop_idx].rotation).to_distributed(
                    len(asym_groups[submol_idx])).hyper_list)
    return betas


def _calc_d(volume, raw_lorentz, alphas):
    dim = len(alphas)
    alpha_super = np.zeros((3 * dim, 3 * dim))
    for i in range(dim):
        alpha_super[3 * i:3 * (i + 1), 3 * i:3 * (i + 1)] = alphas[i].tensor[:, :]
    D_inv = np.identity(3 * dim) - 4. * PI / volume * np.dot(raw_lorentz, alpha_super)
    D = inv(D_inv)
    U = np.vstack([np.identity(3) for i in range(dim)])
    return np.dot(D, U)
