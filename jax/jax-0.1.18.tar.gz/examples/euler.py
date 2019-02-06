"""Automatic differentiation variational inference in Numpy and JAX."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import matplotlib.pyplot as plt

from jax.api import jit, vmap
from jax import lax
import jax.numpy as np

from jax.config import config
config.update("jax_enable_x64", True)

@jit
def linear_interp(t0, y0, t1, y1, t):
    return y0 + (y1 - y0) * (t - t0) / (t1 - t0)

def simple_euler_odeint(func, y0, t, dt=1.0):

    solution = [y0]
    cur_t = t[0]
    cur_y = y0

    for output_t in t[1:]:
        # Integrate until we're past the next time point, then interpolate.
        while cur_t < output_t:
            last_t = cur_t
            last_y = cur_y
            cur_y = cur_y + dt * func(cur_y, cur_t)
            cur_t = cur_t + dt

        output_y = linear_interp(last_t, last_y, cur_t, cur_y, output_t)
        solution.append(output_y)
    return np.stack(solution)


def jax_euler_odeint(func, y0, t, dt=1.0):

    solution = [y0]
    cur_t = np.array([t[0]])
    cur_y = y0

    def euler_step((last_t, last_y, cur_t, cur_y, output_t)):
        last_t = cur_t
        last_y = cur_y
        cur_y = cur_y + dt * func(cur_y, cur_t)
        cur_t = cur_t + dt
        return last_t, last_y, cur_y, cur_t, output_t

    def loop_cond((last_t, last_y, cur_t, cur_y, output_t)):
        return lax.lt(cur_t, output_t)[0]

    for output_t in t[1:]:
        # Integrate until we're past the next time point, then interpolate.
        init_state = (np.array([0.]), np.array([0.]), cur_t, cur_y, output_t)
        state = lax._while_loop(loop_cond, euler_step, init_state)
        output_y = linear_interp(*state)
        solution.append(output_y)
    return np.stack(solution)

jax_euler_odeint = jit(jax_euler_odeint, static_argnums=(0,))


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

    fig = plt.figure(figsize=(8,8), facecolor='white')
    ax = fig.add_subplot(111, frameon=False)

    plot_gradient_field(ax, f, xlimits=[t0, t1], ylimits=[-1, 3])

    ys = simple_euler_odeint(f, y0, ts, dt=0.01)
    plt.plot(ts, ys, 'b-')

    ys2 = jax_euler_odeint(f, y0, ts, dt=0.01)
    plt.plot(ts, ys2, 'g-')

    plt.show()
    plt.savefig("/google/data/rw/users/ma/mattjj/www/euler.png")

