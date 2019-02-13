"""Module to propagate a plasma from the center to the wall, in a One dimentional model"""

import numpy as np
import scipy
from scipy.integrate import ode as solveODE

# Graphic libraries

import matplotlib.pyplot as plt

import astropy.units as u
import plasmapy as ppy

from scipy.optimize import fsolve

m_e = ppy.constants.m_e
mi = ppy.constants.m_p * 40
qe = ppy.constants.e.si.value

from tqdm import tqdm_notebook as tqdm
import numba

import json
from scipy.stats import linregress


@numba.jit(nopython=True)
def _neFromPhi(phi, gamma):
    """The jited function for the Bolzmanian (or not) electrons"""
    if gamma == 1:
        ne = np.exp(-phi)
    else:
        ne = (1 - (gamma - 1) / gamma * phi) ** (1 / (gamma - 1))
    return ne


@numba.jit("f8[:](f8,f8[:],f8,f8)", nopython=True)
def _systemChim(t, x, gamma, epsVal):
    J, u, phi, phidot, T = x

    ne = _neFromPhi(phi, gamma)

    Siz = ne  # for Siz = v_iz * n_e(x)

    dT = - (gamma - 1) / gamma * phidot

    syst = np.array([Siz, phidot / u / T - u / J * ne, phidot, (J / u - ne) / epsVal ** 2 * T, dT])

    return syst


@numba.jit("f8[:](f8,f8[:],f8,f8)", nopython=True)
def _systemPIC(t, x, gamma, epsVal):
    J, u, phi, phidot, T = x

    ne = _neFromPhi(phi, gamma)

    Siz = 1  # for Siz = v_iz

    dT = - (gamma - 1) / gamma * phidot

    syst = np.array([Siz,
                     phidot / u / T - u / J * Siz,
                     phidot,
                     (J / u - ne) / epsVal ** 2 * T,
                     dT])

    return syst


class Plasma:
    """A plasma classe, with dimentions and stuffs"""

    def __init__(self, Te0, ne0, L, mi, sigma, gamma=1, ionization=1, Niter=300):
        import plasmapy as ppy

        self.Te0 = Te0
        self.ne0 = ne0
        self.L = L.decompose()
        self.mi = mi
        self.me = ppy.constants.m_e
        self.qe = ppy.constants.e.si
        self.gamma = gamma

        if self.gamma == 1:
            self.dphi = np.log(np.sqrt(self.mi / (2 * np.pi * self.me)))
        else:
            self.dphi = dphi(self.gamma) * u.V
        self.sigma = sigma

        self.cs = (np.sqrt(self.Te0 / self.mi)).decompose()
        self.Lde = ppy.physics.Debye_length(self.Te0, self.ne0)
        self.ueth = np.sqrt(self.Te0 / (2 * np.pi * self.me)).decompose()
        self.uethVal = self.ueth.value
        self.csVal = self.cs.value
        self.normilize()

        self.Niter = Niter
        self.solved = False
        self.ionization = ionization

    def normilize(self):

        self.l = self.sigma * self.L / self.cs
        self.l = self.l.decompose()
        self.epsilon = self.l * self.Lde / self.L
        self.epsilon = self.epsilon.decompose()
        self.epsVal = self.epsilon.value

    def initialValues(self, dt):
        """returns the initial values for the solver in funtion of epsilon"""

        def interation(a0, a1, b0, b1, c0, c1, e):
            c0 = 1 + 2 * e / c0 ** 2
            b0 = 1 / c0
            a0 = b0 ** 2
            c1 = -a0 + 12 * e ** 2 * a1
            b1 = -(a0 + 3 * b0 * c1) / (3 * c0)
            a1 = b1 * b0 - (a0 * b0 + b0 * c1 / c0 - b1) / (4 * c0)
            return a0, a1, b0, b1, c0, c1

        a0, a1, b0, b1, c0, c1 = [1 for _ in range(6)]
        a0, a1, b0, b1, c0, c1 = interation(a0, a1, b0, b1, c0, c1, e=0)
        res = 1
        niter = 0
        while res > 1e-12 and niter < 50:
            a0n, a1n, b0n, b1n, c0n, c1n = interation(a0, a1, b0, b1, c0, c1, e=self.epsilon.decompose().value)

            res = sum([np.abs(a0 - a0n),
                       np.abs(a1 - a1n),
                       np.abs(b0 - b0n),
                       np.abs(b1 - b1n),
                       np.abs(c0 - c0n),
                       np.abs(c1 - c1n)])
            a0, a1, b0, b1, c0, c1 = a0n, a1n, b0n, b1n, c0n, c1n
            niter += 1

        if niter == 50:
            print("intrations di not converged !!")
            print("epsilon = ", self.epsilon.decompose())
            return 0, 0, 0, 0

        n0 = c0 + c1 * dt ** 2
        u0 = (b0 + b1 * dt ** 2) * dt
        phi0 = (a0 + a1 * dt ** 2) * dt ** 2
        phidot0 = 2 * dt * (a0 + 2 * a1 * dt ** 2)

        Te0 = 1
        # n0 = 1
        v = [n0, u0, phi0, phidot0, Te0]
        # print(v )
        return v
        # return n0, u0, phi0, phidot0

    def nefromphi(self, phi):
        return _neFromPhi(phi, self.gamma)

    def system(self, t, x):
        return _systemChim(t, x, self.gamma, self.epsVal)

    def solve(self):
        """the main function that solves everything !!"""

        epsilon = self.epsilon.decompose().value

        if self.ionization == 1:
            self.solver = solveODE(self.system)
        elif self.ionization == 2:
            self.solver = solveODE(lambda t, x: _systemPIC(t, x, self.gamma, self.epsVal))

        self.solver.set_integrator('dopri5', nsteps=1000)  # RK solver of 4rth order

        t1 = self.l.decompose().value
        t0 = 0
        dt = (t1 - t0) / (self.Niter + 1)

        n0, u0, phi0, phidot0, Te0 = self.initialValues(dt)

        # print(n0, u0, phi0, phidot0)
        y0 = [u0 * n0,
              u0,
              phi0,
              phidot0,
              Te0]

        self.solver.set_initial_value(y0, t0)

        self.tvect = [0]
        self.Jvect = [y0[0]]
        self.uvect = [y0[1]]
        self.phivect = [y0[2]]
        self.phidotvect = [y0[3]]
        self.Tevect = [y0[4]]
        self.index = 0

        continueRun = True
        while continueRun:
            self.index += 1
            self.solver.integrate(self.solver.t + dt)

            self.tvect.append(self.solver.t)
            self.Jvect.append(self.solver.y[0])
            self.uvect.append(self.solver.y[1])
            self.phivect.append(self.solver.y[2])
            self.phidotvect.append(self.solver.y[3])
            self.Tevect.append(self.solver.y[4])

            Gi = self.solver.y[0]
            Ge = self.nefromphi(self.solver.y[2]) * self.uethVal / self.csVal
            continueRun = self.solver.successful() and Gi < Ge

        self.tvect = np.array(self.tvect)
        self.Jvect = np.array(self.Jvect)
        self.uvect = np.array(self.uvect)
        self.phivect = np.array(self.phivect)
        self.phidotvect = np.array(self.phidotvect)
        self.Tevect = np.array(self.Tevect)

        self.solved = True
        # print("Solve finished !!")
        self.ne = self.ne0 * self.nefromphi(self.phivect)
        self.Te = self.Tevect * self.Te0
        self.phi = -self.phivect * (self.Te0.to(u.eV).value)
        self.vi = self.uvect * self.cs
        self.ni = self.ne0 * self.Jvect / (self.uvect + 1e-16)
        self.x = (self.tvect * self.cs / self.sigma).decompose()
        self.Gi = self.vi * self.ni
        self.Ge = self.ne * np.sqrt(self.Te / (2 * np.pi * self.me)).decompose()

        if not self.solver.successful():
            print("Error in the solver !!")
            print(self.index)
            print(self.solver.y)
            raise RuntimeError

    def denormilize(self):
        """The simulation finishes when the electron flux equal the ion flux"""

        self.scaling = self.x[-1] / self.L
        self.sigma *= np.sqrt(self.scaling)

    def returnparameters(self):
        params = {"Te0": self.Te0,
                  "ne0": self.ne0,
                  "L": self.L,
                  "mi": self.mi,
                  "sigma": self.sigma,
                  "gamma": self.gamma,
                  "Niter": self.Niter,
                  "ionization": self.ionization}
        return params

    def plotsummary(self):
        if not self.solved:
            return

        fig, axarr = plt.subplots(2, 3, figsize=(9, 6))
        axarr = axarr.flatten()
        xcm = self.x.to(u.cm).value

        ax1 = axarr[0]
        ax1.plot(xcm, self.phi - self.phi[-1], label="$\phi$")
        dphi = self.dphi.decompose().value * self.Te0.value
        phi1 = dphi
        phi2 = 0.5 * self.Te0.value + dphi

        ax1.hlines(phi1, 0, self.L.to(u.cm).value)
        ax1.hlines(phi2, 0, self.L.to(u.cm).value)
        x1, x2 = [self.L.to(u.cm).value * k for k in [0.7, 0.4]]

        ax1.plot(xcm, self.Te * self.dphi.decompose().value, label=f"$ {self.dphi.decompose().value:2.3}T_e$")

        ax1.text(x1, phi1 * 0.9, f"$ {self.dphi.decompose().value:2.3}T_e$")
        ax1.text(x2, phi2 * 1.05, f"$( {self.dphi.decompose().value:2.3}+1/2)T_e$")
        ax1.set_ylim(0, phi2 * 1.2)

        ax2 = axarr[1]
        ax2.plot(xcm, self.ne, label="electrons")
        ax2.plot(xcm, self.ni, label="ions")

        ax3 = axarr[2]
        ax3.plot(xcm, self.vi / 1e3, label="$v_i$")
        ub = self.cs.decompose().value
        ub = ub * np.sqrt(self.Te / self.Te0) * np.sqrt(self.gamma)
        ax3.plot(xcm, ub / 1e3, label="Bhom Velocity")

        if self.gamma != 0:
            ub0 = ub[0] / np.sqrt(self.gamma)
            ax3.hlines(ub0 / 1e3, 0, self.L.to(u.cm).value, label="$u_{b,0}$")
        ax3.set_ylabel("$v_i$ and $u_b$ [km/s]")

        ax4 = axarr[3]

        ax4.plot(xcm, self.Gi, label="ions flux")
        ax4.plot(xcm, self.Ge, label="electrons flux")
        ax4.set_ylim(bottom=self.Gi.value.min() * 0.5, top=self.Gi.value.max() * 1.5)
        ax4.set_ylabel("$\\Gamma_i, \\Gamma_e$")

        ax5 = axarr[4]
        ax5.plot(np.log(self.ne / self.ne0), np.log(self.ne * self.Te / (self.ne0 * self.Te0)), label="Polytropic")
        ax5.set_xlabel("ln($n_e$)")
        ax5.set_ylabel("ln($T_e n_e$)")

        for ax in axarr:
            ax.grid()
            if ax is not ax5:
                ax.set_xlabel("Position x [cm]")
                ax.set_xlim(0, self.L.to(u.cm).value)
            ax.legend()

        ax1.legend(loc="lower left")

        plt.tight_layout(h_pad=0.5, w_pad=0.2, rect=(0, 0, 1, 0.97))
        if self.gamma == 1:
            plt.suptitle("Ionisation: $S_{iz} = \\nu n_e(x)$, Isothermal model")
        else:
            plt.suptitle("Ionisation: $S_{iz} = \\nu n_e(x)$, $\gamma$=" + str(round(self.gamma, 2)))


class Plasma_ne:
    """As plasma, but we find sigma for a given n_e"""

    def __init__(self, Te0, ne0, L, mi, sigma, gamma=1, ionization=1, Niter=500, verbose=True):
        self.Te0 = Te0
        self.ne0 = ne0
        self.L = L.decompose()
        self.mi = mi
        self.me = ppy.constants.m_e
        self.sigma = sigma
        self.gamma = gamma
        self.ionization = ionization
        self.Niter = Niter

        self.verbose = verbose

        self.p = Plasma(Te0, ne0, L, mi, sigma, gamma, ionization, Niter=self.Niter)

    def solve(self):
        self.p.solve()

    def iterate(self):

        if not self.p.solved:
            self.solve()
            self.p.denormilize()

        self.p = Plasma(**self.p.returnparameters())
        self.solve()
        self.p.denormilize()

        if self.verbose:
            print(self.p.scaling)
            print(f"error over L : {(self.p.x[-1] - self.p.L) / self.p.L * 100:2.3f} %")

    def plotsummary(self):
        self.p.plotsummary()

    def phi_ps(self):
        self.p.x.to(u.cm)
        ub = self.p.cs
        vi = self.p.vi

        indexps = np.argmin(np.abs(vi - ub))

        xps = self.p.x[indexps]
        phips = self.p.phi[indexps]
        Eps = np.gradient(self.p.phi, self.p.x[1].decompose().value)[indexps] * u.V / u.m

        return indexps, xps, phips, Eps
