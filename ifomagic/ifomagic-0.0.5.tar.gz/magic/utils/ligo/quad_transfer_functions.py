'''
Suspension for quadruple pendulum with violin modes included. h_force and 
v_force are the transfer functions from the force on the test mass to the 
test mass motion. h_table and v_table are transfer functions from the 
support motion to the test mass motion.

References:

MAGIC
@author: Isobel
'''
from copy import deepcopy
from magic import constants
from magic.utils.transfer_functions import table_motion_to_mass_motion
from magic.utils.transfer_functions import force_to_mass_motion
from magic.utils.transfer_functions import equations_of_motion
import numpy as np


def calculate(ifo):

    # Assign constants
    g = constants.g
    kB = constants.kb

    # Assign parameters
    params = deepcopy(ifo.parameters)
    temp = params['suspension_temperature']
    f = params['frequency']

    M_s = params['suspension_fiber_material']
    M_c = params['materials']['suspension']['c70steel']
    M_m = params['materials']['suspension']['marsteel']

    # Assign lists of constants for each material
    materials = {'s': M_s, 'c': M_c, 'm': M_m}
    p = {}

    for mat in materials:
        for prop in materials[mat].properties:
            p[prop + '_' + mat] = materials[mat].properties[prop]

    ds = p['dissipation_depth_s']
    Y = p['Y_s']

    theta = params['suspension_VH_coupling_theta']

    m = params['mirror_mass'][::-1]
    n_stages = len(m)

    M1 = sum(m)
    M2 = sum(m[1:])
    M3 = sum(m[2:])
    M = [M1, M2, M3]

    L = params['suspension_length'][::-1]

    dil = params['suspension_dilution'][::-1]

    kv_0 = params['suspension_k'][::-1]

    kh_0 = [M[i] * g / L[i] for i in range(0, len(M))]
    kh_0.append(m[-1] * g / L[-1])

    r = params['suspension_wire_rad'][::-1]
    t = params['suspension_blade_thickness'][::-1]
    N = params['suspension_Nwires'][::-1]
    '''
   -- 'Proposal for Baseline Change from Ribbons to Fibres in AdvLIGO
   Test Mass Suspension Monolithic Stage', Barton, M. et al, LIGO
   Scientific Collaboration, p6 (2008), accessed 13.10.17 at
   [https://dcc.ligo.org/public/0027/T080091/000/T080091-00.pdf]
   '''
    const = 7.372e-2

    if params['suspension_fiber_type'] == 'round':

        # These calculations are for a CYLINDRICAL fiber.
        r_fib = params['fiber_radius']
        # Cross-sectional area
        xsec = np.pi * pow(r_fib, 2)
        # Moment of inertia
        I = pow(r_fib, 4) * np.pi / 4
        # Vertical and horizontal motion, (S/V)
        mu_v = 2 / r_fib
        mu_h = 4 / r_fib
        # [1] eq. 3
        const2 = const * p['rho_s'] * p['C_s'] / p['k_s']
        tau = const2 * (4 * xsec / np.pi)

    elif params['suspension_fiber_type'] == 'ribbon':

        # These calculations are for a RIBBON-LIKE fiber.
        W = params['suspension_ribbon_width']
        th = params['suspension_ribbon_thickness']
        # Cross-sectional area
        xsec = W * th
        # Moment of inertia
        I = W * pow(th, 3) / 12
        # Vertical and horizontal motion, (S/V)
        mu_v = 2 * (W + th) / (W * th)
        mu_h = (3 * N[-1] * W + th) / (N[-1] * W + th) * 2 * (W + th) / (
            W * th)
        tau = p['rho_s'] * p['C_s'] * pow(th, 2) / (p['k_s'] * pow(np.pi, 2))

    # Loss factor
    phi_v = p['phi_s'] * (1 + mu_v * ds)
    Y_sv = p['Y_s'] * (1 + 1j * phi_v)
    # Tension in the last stage
    T = m[-1] * g / N[-1]

    # TE time constant for c70steel
    def tauSteel(r):
        return const * p['rho_c'] * p['C_c'] * pow(2 * r, 2) / p['k_c']

    p['tau_c'] = [tauSteel(r[0]), tauSteel(r[1]), tauSteel(r[2])]

    # TE time constant for maraging blades
    def tauMarag(t):
        return p['rho_m'] * p['C_m'] * pow(t, 2) / (p['k_m'] * pow(np.pi, 2))

    p['tau_m'] = [tauMarag(t[0]), tauMarag(t[1]), tauMarag(t[2])]

    # Deltas: Horizontal, c70steel
    def horizontalDelta(index, mat):
        delta = p['alpha_' + mat]
        delta = delta - p['dlnE_dT_' + mat]*g*M[index]/\
                (N[index]*np.pi*pow(r[index], 2)*p['Y_' + mat])
        delta = p['Y_' + mat] * pow(delta, 2)
        delta = delta * temp[index] / (p['rho_' + mat] * p['C_' + mat])
        return delta

    del_h1 = horizontalDelta(0, 'c')
    del_h2 = horizontalDelta(1, 'c')
    del_h3 = horizontalDelta(2, 'c')
    del_h = [del_h1, del_h2, del_h3]

    # Deltas: Vertical, maraging
    del_v1 = p['Y_m'] * pow(p['alpha_m'], 2) * temp[0] / (
        p['rho_m'] * p['C_m'])
    del_v = [del_v1, del_v1, del_v1]

    # Equations of motion: Solutions
    B = np.array([0, 0, 0, 1]).T

    # Angular frequency
    w = 2 * np.pi * f

    # Silica thermoelastic correction factor
    del_s = p['alpha_s'] - p['dlnE_dT_s'] * T / (xsec * p['Y_s'])
    del_s = pow(del_s, 2) * temp[-1] / p['rho_s'] / p['C_s']
    del_s = p['Y_s'] * del_s

    # Loss factors:
    def lossFactors(mat, delta, tau):
        indices = range(0, len(delta))
        return [p['phi_' + mat] + delta[i]*tau[i]*w/(1 + pow(w*tau[i], 2)) \
          for i in indices]

    # Vertical, maraging
    phi_v = lossFactors('m', del_v, p['tau_m'])

    # Horizontal, steel
    phi_h = lossFactors('c', del_h, p['tau_c'])

    # Horizontal, last stage suspension
    phi_h4 = p['phi_s'] * (1 + mu_h * ds)
    phi_h4 += del_s * tau * w / (1 + pow(tau * w, 2))

    # Spring constants:
    # Vertical
    kv = [kv_0[i] * (1 + 1j * phi_v[i]) for i in range(0, len(phi_v))]
    # Horizontal
    kh = [kh_0[i] * (1 + 1j * phi_h[i] / dil[i]) for i in range(0, len(phi_h))]

    Y_sh = p['Y_s'] * (1 + 1j * phi_h4)

    # Simplification factors
    simp1 = np.sqrt(p['rho_s'] / Y_sh) * w
    simp2 = np.sqrt(p['rho_s'] * xsec * pow(w, 2) / T)
    simp3 = np.sqrt(T * (1 + I * xsec * Y_sh * pow(w / T, 2)) / (Y_sh * I))
    a = simp3 * np.cos(simp2 * L[-1])
    b = np.sin(simp2 * L[-1])

    # Vertical spring constant, last stage
    kv_4 = N[-1] * Y_sv * xsec * simp1 / np.tan(simp1 * L[-1])

    # IRS TODO: This is a copy of a guess from GWINC
    # (suspensionthermal.py, around line 380)
    kv_4 /= p['div_fact_s']

    # Horizontal spring constant, last stage
    kh_4 = N[-1] * I * Y_sh * simp2 * simp3 * (
        pow(simp2, 2) + pow(simp3, 2)) * (a + simp2 * b)
    kh_4 = -kh_4 / (2 * simp2 * a + (pow(simp2, 2) - pow(simp3, 2)) * b)

    kv.append(kv_4)
    kh.append(kh_4)

    # Equations of motion
    # Specifically oriented lists
    m_ = np.hstack(m)
    kv_ = np.vstack(kv)
    kh_ = np.vstack(kh)

    # TFs turning on loss of each individual stage
    h_force = {}
    v_force = {}
    forces = [h_force, v_force]
    k_lists = [kh_, kv_]
    tables = [0, 0]

    for F in forces:
        F['singly_lossy'] = np.zeros((n_stages, f.size), dtype=complex)

    for i, F in enumerate(forces):
        for ii in range(n_stages):
            k_list = k_lists[i]
            # On_ly use imaginary part of stage ii
            k_list = np.real(k_list) + 1j*np.imag(np.vstack((k_list[0,:]*(ii==0),\
                 k_list[1,:]*(ii==1),\
                 k_list[2,:]*(ii==2),\
                 k_list[3,:]*(ii==3))))
            A = equations_of_motion.calculate(k_list, m_, f)
            F['singly_lossy'][ii, :] = force_to_mass_motion.calculate(A, B, f)
            tables[i] = table_motion_to_mass_motion.calculate(A, B, k_list, f)

    for j, k in enumerate(k_lists):
        A = equations_of_motion.calculate(k, m_, f)
        # Transfer function calculation
        forces[j]['fully_lossy'] = force_to_mass_motion.calculate(A, B, f)
        tables[j] = table_motion_to_mass_motion.calculate(A, B, k, f)

    h_table = tables[0]
    v_table = tables[1]

    return h_table, v_table, h_force, v_force
