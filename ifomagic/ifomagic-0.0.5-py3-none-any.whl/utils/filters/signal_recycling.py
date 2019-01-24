'''
Shot noise due to signal recycling.

References:
--- [1] Buonanno and Chen 2001 Phys.Rev. D 64 042006
   https://journals.aps.org/prd/abstract/10.1103/PhysRevD.64.042006
--- [2] Kimble et al. 2001 Phys.Rev. D 65 022002
   https://journals.aps.org/prd/pdf/10.1103/PhysRevD.65.022002
--- [3] Buonanno and Chen 2004 Phys.Rev. D 69 102004
   https://journals.aps.org/prd/abstract/10.1103/PhysRevD.69.102004

MAGIC
@author: Isobel
'''
from magic.utils.transfer_functions import transfer_matrix
from magic.utils.transfer_functions import transfer_matrix_product

from magic import constants
import numpy as np


def calculate(params):

    # Assign parameters
    # Frequency
    f = params['frequency']
    # Laser beam wavelength
    lam = params['wavelength']
    # Arm length
    L = params['length']
    # Signal recycling cavity length
    L_src = params['src_length']
    # Transmittance of Itransfer_matrix
    T_itm = params['itm_transmittance']
    # Mass of the test mass
    m = params['mirror_mass'][0]
    # Loss at beamsplitter
    bs_loss = params['bs_loss']
    # Optical coupling
    o_c = params['optical_coupling']
    # Additional loss in signal recycling cavity due to thermal lensing
    src_loss = params['tcs_src_loss']
    # Power at the beamsplitter
    bs_power = params['bs_power']
    # Laser carrier frequency
    w_0 = params['laser_carrier_frequency']
    # Signal recycling cavity detuning
    dphase = params['src_phase_tuning']
    # Signal carrier frequency
    w = params['signal_omega']

    # Assign constants
    # Reduced Planck constant
    hbar = constants.hbar
    # Speed of light
    c = constants.c
    # Mismatch
    mismatch = 1 - o_c + src_loss
    # Signal recycling cavity loss
    sr_cav_loss = mismatch + bs_loss
    # Amplitude of signal recycling mirror transmittance
    tau = np.sqrt(params['srm_transmittance'])
    # Amplitude of signal recycling mirror reflectivity
    rho = np.sqrt(1 - pow(tau, 2) - sr_cav_loss)

    # [1] between eqns. 2.14 - 2.15
    # Set phi for best bandwidth range - resonant sideband extraction
    phi = (np.pi - dphase) / 2
    Phi = w * L_src / c

    # Round trip loss in arm
    # [1] eqn. 5.2+
    o_l = 2 * params['optical_loss']

    # Arm cavity half bandwidth
    # [2]
    half_bw = T_itm * c / 4 / L

    # Phase shift of GW SB in arm
    # [1] eqn. 2.11+
    beta = np.arctan(w / half_bw) + Phi

    # Loss coefficient for arm cavity
    # [1] eqn. 5.2+
    epsilon = o_l * c / 2 / half_bw / L

    # Power to reach free mass SQL
    # [1] eqn. 2.14
    free_mass_power = m * pow(L, 2) * pow(half_bw, 4)
    free_mass_power = free_mass_power / 4
    free_mass_power = free_mass_power / w_0
    power_ratio = bs_power / free_mass_power
    A = power_ratio * pow(half_bw, 4)
    B = pow(w, 2) * (pow(half_bw, 2) + pow(w, 2))

    # Effective radiation pressure
    # [1] eqn. 2.13
    Kappa = 2 * A / B

    # SQL strain
    # [1] eqn. 2.12
    h_SQL = np.sqrt(8 * hbar / (m * pow(w * L, 2)))
    # Calculate matrix elements
    # [1] eqns. 5.8 - 5.12
    # Shorthand for trig functions and exponential
    ejB = np.exp(1j * beta)
    e2jB = np.exp(2j * beta)
    c2P = np.cos(2 * phi)
    cP = np.cos(phi)
    c2B = np.cos(2 * beta)
    cB = np.cos(beta)
    s2P = np.sin(2 * phi)
    sP = np.sin(phi)
    s2B = np.sin(2 * beta)
    sB = np.sin(beta)

    # Set up matrix element c11
    c11_a = ((1 + pow(rho, 2)) * (c2P + Kappa / 2 * s2P)) - 2 * rho * c2B
    c11_b = 1 / 4 * epsilon
    c11_c = -2 * pow((1 + e2jB), 2) * rho
    c11_d = 4 * (1 + pow(rho, 2)) * pow(cB, 2) * c2P
    c11_e = (3 + e2jB) * Kappa * (1 + pow(rho, 2)) * s2P
    c11_f = sr_cav_loss
    c11_g = e2jB * rho - 1 / 2 * (1 + pow(rho, 2)) * (c2P + Kappa / 2 * s2P)

    # Calculate matrix element c11
    c11 = c11_a - c11_b * (c11_c + c11_d + c11_e) + c11_f * c11_g

    # Calculate matrix element c22
    c22 = c11

    # Set up matrix element c12
    c12_a = pow(tau, 2)
    c12_b = -(s2P + Kappa * pow(sP, 2))
    c12_c = 1 / 2 * epsilon * sP
    c12_d = (3 + e2jB) * Kappa * sP
    c12_e = 4 * pow(cB, 2) * cP
    c12_d = 1 / 2 * sr_cav_loss * (s2P + Kappa * pow(sP, 2))

    # Calculate matrix element c12
    c12 = c12_a * (c12_b + c12_c * (((3 + e2jB) * Kappa * sP) + c12_e) + c12_d)

    # Set up matrix element c21
    c21_a = pow(tau, 2)
    c21_b = (s2P - Kappa * pow(cP, 2))
    c21_c = 1 / 2 * epsilon * cP
    c21_e = 4 * pow(cB, 2) * sP
    c21_d = 1 / 2 * sr_cav_loss * (-s2P + Kappa * pow(cP, 2))

    # Calculate matrix element c21
    c21 = c21_a * (c21_b + c21_c * ((3 + e2jB) * Kappa * sP - c21_e) + c21_d)

    # Set up matrix element d1
    d1_a = -(1 + rho * e2jB) * sP
    d1_b = 1 / 4 * epsilon
    d1_c = 3 + rho + 2 * rho * np.exp(4 * 1j * beta)
    d1_d = e2jB * (1 + 5 * rho)
    d1_e = sP
    d1_f = 1 / 2 * sr_cav_loss * e2jB * rho * sP

    # Calculate matrix element d1
    d1 = (d1_a) + d1_b * (d1_c + d1_d) * d1_e + d1_f

    # Set up matrix element d2
    d2_a = -(-1 + rho * e2jB) * cP
    d2_b = 1 / 4 * epsilon
    d2_c = -3 + rho + 2 * rho * np.exp(4 * 1j * beta)
    d2_d = e2jB * (-1 + 5 * rho)
    d2_e = cP
    d2_f = 1 / 2 * sr_cav_loss * e2jB * rho * cP

    # Calculate matrix element d2
    d2 = d2_a + d2_b * (d2_c + d2_d) * d2_e + d2_f

    # Calculate matrix elements p11, p22, p12, p21
    p11 = 0.5 * np.sqrt(sr_cav_loss) * tau * (
        -2 * rho * e2jB + 2 * c2P + Kappa * s2P)
    p22 = p11
    p12 = -np.sqrt(sr_cav_loss) * tau * sP * (2 * cP + Kappa * sP)
    p21 = np.sqrt(sr_cav_loss) * tau * cP * (2 * sP - Kappa * cP)

    # Set up matrix element q11
    q11_a = 1 / e2jB + pow(rho, 2) * e2jB - rho * (2 * c2P + Kappa * s2P)
    q11_b = 1 / 2 * epsilon * rho
    q11_c = 1 / e2jB * c2P
    q11_d = e2jB * (-2 * rho - 2 * rho * c2B + c2P + Kappa * s2P)
    q11_e = 2 * c2P + 3 * Kappa * s2P
    q11_f = 1 / 2 * sr_cav_loss * rho
    q11_g = 2 * rho * e2jB - 2 * c2P - Kappa * s2P

    # Calculate matrix element q11
    q11 = pow(q11_a + q11_b * (q11_c + q11_d + q11_e) - q11_f * q11_g, -1)

    # Set matrix elements q22, q12, q21
    q22 = q11
    q12 = 0
    q21 = 0

    # Set up matrix element n11
    n11_a = np.sqrt(epsilon / 2) * tau
    n11_b = Kappa * (1 + rho * e2jB) * sP
    n11_c = 2 * cB
    n11_ci = pow(ejB, -1) * cP
    n11_d = rho * ejB * (cP + Kappa * sP)

    # Calculate matrix element n11
    n11 = n11_a * (n11_b + n11_c * (n11_ci - n11_d))
    # Calculate matrix element n22
    n22 = -np.sqrt(2 * epsilon) * tau * (-pow(ejB, -1) + rho * ejB) * cB * cP
    # Calculate matrix element n12
    n12 = -np.sqrt(2 * epsilon) * tau * (pow(ejB, -1) + rho * ejB) * cB * sP

    # Set up matrix element n21
    n21_a = np.sqrt(2 * epsilon) * tau
    n21_b = -Kappa * (1 + rho) * cP
    n21_c = 2 * cB * (pow(ejB, -1) + rho * ejB) * cB * sP

    # Calculate matrix element n21
    n21 = n21_a * (n21_b + n21_c)

    # Overall coefficient
    coeff = pow(h_SQL, 2) / (2 * Kappa * pow(tau, 2))

    # Normalisation matrices
    M_q = transfer_matrix.calculate(q11, q12, q21, q22)
    M_p = transfer_matrix.calculate(p11, p12, p21, p22)
    M_n = transfer_matrix.calculate(n11, n12, n21, n22)
    M_c = transfer_matrix.calculate(c11, c12, c21, c22)
    M_d = np.array([d1, d2]).reshape(2, 1, f.size)
    # Combine
    M_noise = transfer_matrix_product.calculate(M_q, np.hstack((M_n, M_p)))

    # 3D transfer_matrix_s from element vectors
    M_ifo = transfer_matrix_product.calculate(M_q, M_c)
    M_signal = transfer_matrix_product.calculate(M_q, M_d)

    return coeff, M_ifo, M_signal, M_noise
