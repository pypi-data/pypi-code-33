"""Automatic differentiation variational inference in Numpy and JAX."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import matplotlib.pyplot as plt

from jax.api import jit, vmap
import jax.numpy as np


# Dopri5 Butcher tableaux
alpha=[1 / 5, 3 / 10, 4 / 5, 8 / 9, 1., 1.]
beta=[np.array([1 / 5]),
      np.array([3 / 40, 9 / 40]),
      np.array([44 / 45, -56 / 15, 32 / 9]),
      np.array([19372 / 6561, -25360 / 2187, 64448 / 6561, -212 / 729]),
      np.array([9017 / 3168, -355 / 33, 46732 / 5247, 49 / 176, -5103 / 18656]),
      np.array([35 / 384, 0, 500 / 1113, 125 / 192, -2187 / 6784, 11 / 84]),]
c_sol=np.array([35 / 384, 0, 500 / 1113, 125 / 192, -2187 / 6784, 11 / 84, 0])
c_error=np.array([35 / 384 - 1951 / 21600, 0, 500 / 1113 - 22642 / 50085,
    125 / 192 - 451 / 720, -2187 / 6784 - -12231 / 42400, 11 / 84 - 649 / 6300,
    -1. / 60.,])
dps_c_mid = np.array([
    6025192743 / 30085553152 / 2, 0, 51252292925 / 65400821598 / 2, -2691868925 / 45128329728 / 2,
    187940372067 / 1594534317056 / 2, -1776094331 / 19743644256 / 2, 11237099 / 235043384 / 2
])

@jit
def L2_norm(x):
    return np.sqrt(np.sum(x**2))

@jit
def interp_fit_dopri(y0, y1, k, dt):
    """Fit an interpolating polynomial to the results of a Runge-Kutta step."""
    y_mid = y0 + dt * np.dot(dps_c_mid, k)
    f0 = k[0]
    f1 = k[-1]
    return interp_fit(y0, y1, y_mid, f0, f1, dt)

@jit
def interp_fit(y0, y1, y_mid, f0, f1, dt):
    """Fit coefficients for 4th order polynomial interpolation.
    Args:
        y0: function value at the start of the interval.
        y1: function value at the end of the interval.
        y_mid: function value at the mid-point of the interval.
        f0: derivative value at the start of the interval.
        f1: derivative value at the end of the interval.
        dt: width of the interval.
    Returns:
        List of coefficients `[a, b, c, d, e]` for interpolating with the polynomial
        `p = a * x ** 4 + b * x ** 3 + c * x ** 2 + d * x + e` for values of `x`
        between 0 (start of interval) and 1 (end of interval).
    """
    v = np.stack([f0, f1, y0, y1, y_mid])
    a = np.dot(np.hstack([-2 * dt,  2 * dt, np.array([ -8., -8.,  16.])]), v)
    b = np.dot(np.hstack([ 5 * dt, -3 * dt, np.array([ 18., 14., -32.])]), v)
    c = np.dot(np.hstack([-4 * dt,      dt, np.array([-11., -5.,  16.])]), v)
    d = dt * f0
    e = y0
    return a, b, c, d, e

@jit
def polyval(p, x):   # Clone of np.polyval.
    y = np.zeros(np.shape(x))
    for i in range(len(p)):
        y = y * x + p[i]
    return y

def select_initial_step(fun, t0, y0, order, rtol, atol, f0):
    """Empirically choose an initial step size.  Algorithm from:
    E. Hairer, S. P. Norsett G. Wanner,
    Solving Ordinary Differential Equations I: Nonstiff Problems, Sec. II.4."""
    scale = atol + np.abs(y0) * rtol
    d0 = L2_norm(y0 / scale)
    d1 = L2_norm(f0 / scale)

    if d0 < 1e-5 or d1 < 1e-5:
        h0 = 1e-6
    else:
        h0 = 0.01 * d0 / d1

    y1 = y0 + h0 * f0
    f1 = fun(t0 + h0, y1)
    d2 = (L2_norm(f1 - f0) / scale) / h0

    if d1 <= 1e-15 and d2 <= 1e-15:
        h1 = np.maximum(1e-6, h0 * 1e-3)
    else:
        h1 = (0.01 / (d1 + d2))**(1. / float(order + 1))

    return np.minimum(100 * h0, h1)

def list_dot(xs, ys):
    return np.sum(np.array([a * b for a, b in zip(xs, ys)]))

def runge_kutta_step(func, y0, f0, t0, dt):
    """Take an arbitrary Runge-Kutta step and estimate error.
    Args:
        func: Function to evaluate like `func(t, y)` to compute the time derivative
            of `y`.
        y0: initial value for the state.
        f0: initial value for the derivative, computed from `func(t0, y0)`.
        t0: initial time.
        dt: desired time step.
        alpha, beta, c: Butcher tableau describing how to take the Runge-Kutta step.
    Returns:
        y1: estimated function at t1 = t0 + dt
        f1: derivative of the state at t1
        y1_error: estimated error at t1
        k: list of Runge-Kutta coefficients `k` used for calculating these terms.
    """
    k = [f0]
    for alpha_i, beta_i in zip(alpha, beta):
        ti = t0 + alpha_i * dt
        yi = y0 + dt * list_dot(beta_i, k)
        k.append(func(yi, ti))
    k = np.stack(k)  # TODO: Clean this up when append is supported.

    y1 = y0 + dt * np.dot(c_sol, k)
    f1 = k[-1]
    y1_error = dt * np.dot(c_error, k)
    return y1, f1, y1_error, k


#dopri_runge_kutta_step = jit(dopri_runge_kutta_step, static_argnums=(0,))

@jit
def error_ratio(error_estimate, rtol, atol, y0, y1):
    error_tol = atol + rtol * np.maximum(np.abs(y0), np.abs(y1))
    error_ratio = error_estimate / error_tol
    return np.mean(error_ratio**2)


def optimal_step_size(last_step, mean_error_ratio, safety=0.9, ifactor=10.0, dfactor=0.2, order=5):
    mean_error_ratio = np.max(mean_error_ratio)
    if mean_error_ratio == 0:
        return last_step * ifactor
    if mean_error_ratio < 1:
        dfactor = 1.0
    error_ratio = np.sqrt(mean_error_ratio)
    factor = np.maximum(1.0 / ifactor,
                    np.minimum(error_ratio**(1.0 / order) / safety, 1.0 / dfactor))
    return last_step / factor


def dopri_odeint(func, y0, t, rtol=1e-7, atol=1e-9):

    f0 = func(y0, t[0])
    dt = select_initial_step(func, t[0], y0, 4, rtol, atol, f0)
    interp_coeff = np.array([y0] * 5)

    solution = [y0]
    cur_t = t[0]
    cur_y = y0
    cur_f = f0

    for output_t in t[1:]:
        # Interpolate through to the next time point, integrating as necessary.
        while cur_t < output_t:
            next_t = cur_t + dt
            assert next_t > cur_t, 'underflow in dt {}'.format(dt)

            next_y, next_f, next_y_error, k = runge_kutta_step(func, cur_y, cur_f, cur_t, dt)
            error_ratios = error_ratio(next_y_error, atol=atol, rtol=rtol, y0=cur_y, y1=next_y)

            if np.all(error_ratios <= 1):
                # Accept the step.
                interp_coeff = interp_fit_dopri(cur_y, next_y, k, dt)
                cur_y = next_y
                cur_f = next_f
                last_t = cur_t
                cur_t = next_t

            dt = optimal_step_size(dt, error_ratios)

        relative_output_time = (output_t - last_t) / (cur_t - last_t)
        output_y = polyval(interp_coeff, relative_output_time)
        solution.append(output_y)
    return np.stack(solution)


def plot_gradient_field(ax, func, xlimits, ylimits, numticks=30):
    x = np.linspace(*xlimits, num=numticks)
    y = np.linspace(*ylimits, num=numticks)
    X, Y = np.meshgrid(x, y)
    zs = vmap(func)(Y.ravel(), X.ravel())
    Z = zs.reshape(X.shape)
    ax.quiver(X, Y, np.ones(Z.shape), Z)
    ax.set_xlim(xlimits)
    ax.set_ylim(ylimits)


if __name__ == "__main__":

    def f(y, t):
        return y - np.sin(t) - np.cos(t)

    t0 = 0.
    t1 = 5.
    ts = np.linspace(t0, t1, 100)
    y0 = np.array([1.])

    # Set up figure.
    fig = plt.figure(figsize=(8,8), facecolor='white')
    ax = fig.add_subplot(111, frameon=False)
    plt.ion()
    plt.show(block=False)

    plt.cla()
    plot_gradient_field(ax, f, xlimits=[t0, t1], ylimits=[-1, 3])

    ys = dopri_odeint(f, y0, ts)
    plt.plot(ts, ys, 'g-')
    plt.draw()
    plt.pause(60)

