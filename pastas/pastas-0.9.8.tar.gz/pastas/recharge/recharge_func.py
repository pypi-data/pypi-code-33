"""recharge_func module

Author: R.A. Collenteur

Contains the classes for the different models that are available to calculate
the recharge from evaporation and precipitation data.

Each Recharge class contains at least the following:

Attributes
----------
nparam: int
    Number of parameters needed for this model.

Functions
---------
set_parameters(self, name)
    A function that returns a Pandas DataFrame of the parameters of the
    recharge function. Columns of the dataframe need to be ['value', 'pmin',
    'pmax', 'vary']. Rows of the DataFrame have names of the parameters. Input
    name is used as a prefix. This function is called by a Tseries object.
simulate(self, evap, prec, p=None)
    A function that returns an array of the simulated recharge series.

"""

import pandas as pd
import numpy as np
import numba


class Linear:
    """Linear recharge model

    The recharge to the groundwater is calculated as:
    R = P - f * E

    """

    def __init__(self):
        self.nparam = 1

    def set_parameters(self, name):
        parameters = pd.DataFrame(
            columns=['initial', 'pmin', 'pmax', 'vary', 'name'])
        parameters.loc[name + '_f'] = (-1.0, -5.0, 0.0, 1, name)
        return parameters

    def simulate(self, precip, evap, p=None):
        recharge = precip + p * evap
        return recharge


class Percolation:
    """
    Percolation flow recharge model

    Other water balance for the root zone s calculated as:

    dS/dt = Pe - Kp * (Sr / Srmax)**Gamma - Epu * min(1, Sr / (0.5 * Srmax))

    """

    def __init__(self):
        self.nparam = 4
        self.dt = 1
        self.solver = 1

    def set_parameters(self, name):
        parameters = pd.DataFrame(
            columns=['initial', 'pmin', 'pmax', 'vary', 'name'])
        parameters.loc[name + '_Srmax'] = (0.26, np.nan, np.nan, 0, name)
        parameters.loc[name + '_Kp'] = (1.0e-2, 0.0, np.nan, 1, name)
        parameters.loc[name + '_Gamma'] = (3.0, 0.0, np.nan, 1, name)
        parameters.loc[name + '_Imax'] = (1.5e-3, 0.0, np.nan, 0, name)
        return parameters

    def simulate(self, prec, evap, p=None):
        t = np.arange(len(prec))
        recharge = self.perc(t, prec.values, evap.values, p[0], p[1], p[2],
                             p[3], self.dt, self.solver)[0]
        return recharge

    @numba.jit
    def perc(self, t, P, E, Srmax=0.1, Kp=0.03, Gamma=2.0, Imax=0.001, dt=1.0,
             solver=0):
        n = int(len(t) / dt)
        error = 1.0e-5

        # Create an empty array to store the soil state in
        S = np.zeros(n)
        S[0] = 0.5 * Srmax  # Set the initial system state
        Si = np.zeros(n)
        Si[0] = 0.0
        Pe = np.zeros(n)
        Pe[0] = 0.0
        Ei = np.zeros(n)
        Ei[0] = 0.0
        Epu = np.zeros(n)
        Epu[0] = 0.0
        Ea = np.zeros(n)
        Ea[0] = 0.0

        for t in range(n - 1):
            # Fill intercEpution bucket with new rain
            Si[t + 1] = Si[t] + P[t + 1]
            # Calculate effective precipitation
            Pe[t + 1] = np.max([0.0, Si[t + 1] - Imax])
            Si[t + 1] = Si[t + 1] - Pe[t + 1]
            # Evaporation from intercEpution
            Ei[t + 1] = np.min([Si[t + 1], E[t + 1]])
            # Update intercEpution state
            Si[t + 1] = Si[t + 1] - Ei[t + 1]
            # Update potential evapotranspiration
            Epu[t + 1] = E[t + 1] - Ei[t + 1]
            Last_S = S[t]
            iteration = 0
            bisection = 1

            # Use explicit Euler scheme to find an initial estimate for the newton raphson-method
            S[t + 1] = np.max(
                [0.0, S[t] + dt * (Pe[t] - Kp * (S[t] / Srmax) ** Gamma -
                                   Epu[t] * np.min([1.0, (S[t] / (0.5 *
                                                                  Srmax))]))])

            if solver == 1:
                # Start the while loop for the newton-Raphson iteration
                while abs(Last_S - S[t + 1]) > error:
                    if iteration > 100:
                        break  # Check if the number of iterations is not too high
                    iteration += 1
                    Last_S = S[t + 1]

                    g = Last_S - S[t] - dt * (
                            Pe[t] - Kp * (Last_S / Srmax) ** Gamma -
                            Epu[t] * np.min([1, (Last_S / (0.5 *
                                                           Srmax))]))
                    # Derivative dEpuends on the state of the system
                    if Last_S > (0.5 * Srmax):
                        g_derivative = 1.0 - dt * (
                                -Gamma * Kp * (Last_S / Srmax) ** (Gamma - 1))
                    else:
                        g_derivative = 1.0 - dt * (
                                -Gamma * Kp * (Last_S / Srmax) ** (Gamma - 1) -
                                Epu[
                                    t] * (
                                        0.5 * Srmax))

                    # Check if there is no zero-division error
                    if np.isnan(g / g_derivative):
                        bisection = 0
                        break
                    # if there is no zero-division error
                    else:  # use newton raphson
                        S[t + 1] = Last_S - g / g_derivative

                if bisection == 0:
                    iteration = 0
                    a = S[t]
                    b = S[t + 1]
                    c = a + b / 2.0

                    while ((b - a) / 2.0) > error:
                        if iteration > 100:
                            print('iteration in bisection method exceeded 100',
                                  iteration)
                            break
                        iteration += 1  # increase the number of iterations by 1

                        if (c - S[t] - dt * (
                                Pe[t] - Kp * (c / Srmax) ** Gamma - Epu[t]
                                * np.min([1, (c / (0.5 * Srmax))]))) == 0.0:
                            return c  # Return the current value if it is correct
                        elif (a - S[t] - dt * (
                                Pe[t] - Kp * (a / Srmax) ** Gamma - Epu[
                            t] * np.min([1.0, (a / (0.5 * Srmax))]))) * (
                                c - S[t] - dt
                                * (Pe[t] - Kp * (c / Srmax) ** Gamma - Epu[
                            t] * np.min(
                            [
                                1.0, (c / (0.5 * Srmax))]))) > 0.0:
                            b = c
                        else:
                            a = c

                        c = a + b / 2.0

                    S[t + 1] = c

                assert ~np.isnan(
                    S[t + 1]), 'NaN-value calculated for soil state'

            # Make sure the solution is larger then 0.0 and smaller than Srmax
            S[t + 1] = np.min([Srmax, np.max([0.0, S[t + 1]])])
            Ea[t + 1] = Epu[t + 1] * np.min([1, (S[t + 1] / (0.5 * Srmax))])

        R = np.append(0.0, Kp * dt * 0.5 * (
                (S[:-1] ** Gamma + S[1:] ** Gamma) / (Srmax ** Gamma)))

        return R, S, Ea, Ei
