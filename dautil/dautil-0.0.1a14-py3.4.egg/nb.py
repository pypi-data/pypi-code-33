from IPython.display import display
from IPython.display import Math
from IPython.html import widgets
from dautil import collect
from dautil import log_api
from dautil import ts
import matplotlib as mpl
from matplotlib.colors import rgb2hex


def create_month_widget(month, *args, **kwargs):
    return widgets.Dropdown(options=ts.short_months(),
                            selected_label=month, *args, **kwargs)


class RcWidget():
    def __init__(self):
        self.old = mpl.rcParams.copy()
        display(widgets.Tab(children=[self.grid_page()]))

    def update(self, rc_params={}):
        logger = log_api.conf_logger('RcWidget')
        updates = collect.dict_updates(self.old, mpl.rcParams)
        logger.warning('mpl.RcParams updates {}'.
                       format(updates))
        self.old = mpl.rcParams.copy()

    def create(self):
        box = widgets.VBox()
        axes_linewidth = create_linewidth_slider(0)
        axes_linewidth.description = 'axes_linewidth'

        text = widgets.HTML()
        box.children = (text, axes_linewidth)
        box.description = text

        def update_axes_linewidth(name, value):
            mpl.rcParams['axes.linewidth'] = value

        axes_linewidth.on_trait_change(update_axes_linewidth, 'value')

        return box

    def grid_page(self):
        grid_linewidth = create_linewidth_slider(2)
        grid_linewidth.description = 'grid.linewidth'

        grid_color = ColorChooser()
        grid_color.description = 'grid.color'
        box = widgets.VBox(children=[grid_linewidth, grid_color])

        def update_grid_linewidth(name, value):
            mpl.rcParams['grid.linewidth'] = value

        def update_grid_color(name, value):
            mpl.rcParams['grid.color'] = value

        grid_linewidth.on_trait_change(update_grid_linewidth, 'value')
        grid_color.on_trait_change(update_grid_color, 'value')
        display(box)


def create_linewidth_slider(value, *args, **kwargs):
    return widgets.IntSlider(min=0, max=9, value=value, *args, **kwargs)


class ColorChooser():
    def __init__(self):
        self.r = widgets.FloatSlider(min=0, max=1, description='Red')
        self.r.border_color = 'red'

        self.g = widgets.FloatSlider(min=0, max=1, description='Green')
        self.g.border_color = 'green'

        self.b = widgets.FloatSlider(min=0, max=1, description='Blue')
        self.b.border_color = 'blue'

        self.h = widgets.widget_string.HTML('Color')

        self.r.on_trait_change(self.update, 'value')
        self.g.on_trait_change(self.update, 'value')
        self.b.on_trait_change(self.update, 'value')

        display(self.r)
        display(self.g)
        display(self.b)
        display(self.h)

    def update(self, name, value):
        hex = rgb2hex((self.r.value, self.g.value, self.b.value))
        self.h.value = '<p style="background-color: {0};">{0}</p>'.format(hex)
        self.value = self.h.value


class LatexRenderer():
    def __init__(self, chapter=None, start=1):
        self.chapter = chapter
        self.curr = start

    # DIY numbering because Python doesn't
    # support numbering
    def number_equation(self):
        number = '('

        if self.chapter:
            number += str(self.chapter) + '.'

        number += str(self.curr) + ')\hspace{1cm}'

        return number

    def render(self, equation):
        number = self.number_equation()
        display(Math(r'%s' % (number + equation)))
        self.curr += 1
