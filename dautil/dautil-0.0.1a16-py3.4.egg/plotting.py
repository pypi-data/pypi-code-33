from itertools import cycle
from matplotlib.colors import rgb2hex
import matplotlib.pyplot as plt
import numpy as np
from dautil import collect


def scatter_with_bar(ax, bar_label, *args, **kwargs):
    sc = ax.scatter(*args, **kwargs)
    plt.colorbar(sc, ax=ax, label=bar_label)


def sample_cmap(name='Reds', start=0.1, end=0.9, ncolors=9):
    cmap = plt.cm.get_cmap(name)

    return cmap(np.linspace(start, end, ncolors))


def sample_hex_cmap(name='Reds', start=0.1, end=0.9, ncolors=9):
    cmap = sample_cmap(name, start, end, ncolors)

    return [rgb2hex(c) for c in cmap]


def embellish(axes, legends=None):
    for i, ax in enumerate(axes):
        ax.grid(True)

        if legends is None:
            ax.legend(loc='best')
        elif i in legends:
            ax.legend(loc='best')


def hide_axes(axes):
    flat_axes = axes

    if len(axes) > 0:
        flat_axes = axes.ravel()

    for ax in flat_axes:
        ax.get_xaxis().set_visible(False)
        ax.get_yaxis().set_visible(False)


class Cycler():
    def __init__(self, styles=["-", "--", "-.", ":"], lw=[1, 2]):
        self.STYLES = cycle(styles)
        self.LW = cycle(lw)
        self.colors = cycle(sample_hex_cmap(name='hot'))

    def style(self):
        return next(self.STYLES)

    def lw(self):
        return next(self.LW)

    def color(self):
        return next(self.colors)


class CyclePlotter():
    def __init__(self, ax):
        self.ax = ax
        self.cycler = Cycler()

    def plot(self, x, y, *args, **kwargs):
        self.ax.plot(x, y, self.cycler.style(),
                     lw=self.cycler.lw(), *args, **kwargs)


class Subplotter():
    def __init__(self, nrows=1, ncols=1, context=None):
        self.context = context
        self.old = None
        self.index = -1

        if context:
            self.old = self.context.read_labels()
            self.old = collect.flatten(self.old)

        # TODO turn off squeeze
        self.fig, self.axes = plt.subplots(nrows, ncols)

        if nrows > 1 and ncols > 1:
            self.axes = collect.flatten(self.axes)

        if nrows == 1 and ncols == 1:
            self.ax = self.axes
            self.index = 0
        else:
            self.ax_iter = iter(self.axes)
            self.next_ax()

    def next_ax(self):
        self.index += 1

        self.ax = next(self.ax_iter)

    def get_string(self, old, key, params):
        astr = old.get(key, '')

        if params:
            if isinstance(params, str):
                astr = astr.format(params)
            else:
                astr = astr.format(*params)

        return astr

    def label(self, title_params=None, xlabel_params=None, ylabel_params=None):
        # Cowardly refusing to continue
        if self.old is None:
            return

        old = self.old[self.index]

        title = self.get_string(old, 'title', title_params)
        self.ax.set_title(title)
        xlabel = self.get_string(old, 'xlabel', xlabel_params)
        self.ax.set_xlabel(xlabel)
        ylabel = self.get_string(old, 'ylabel', ylabel_params)
        self.ax.set_ylabel(ylabel)
