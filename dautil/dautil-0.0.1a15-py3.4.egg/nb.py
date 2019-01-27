from IPython.display import display
from IPython.display import Javascript
from IPython.display import Math
from IPython.html import widgets
from dautil import collect
from dautil import ts
import matplotlib as mpl
from matplotlib.colors import rgb2hex
import pprint


def create_month_widget(month, *args, **kwargs):
    return widgets.Dropdown(options=ts.short_months(),
                            selected_label=month, *args, **kwargs)


class RcWidget():

    def __init__(self):
        self.old = mpl.rcParams.copy()
        tab = widgets.Tab(children=[self.axes_page(), self.figure_page(),
                                    self.font_page(), self.grid_page(),
                                    self.lines_page()])
        tab.set_title(0, 'Axes')
        tab.set_title(1, 'Figure')
        tab.set_title(2, 'Font')
        tab.set_title(3, 'Grid')
        tab.set_title(4, 'Lines')
        display(tab)

        self.updates_text = widgets.HTML()
        display(self.updates_text)

        self.params_text = widgets.HTML()
        display(self.params_text)

        self.show_params = widgets.widget_button.Button()
        self.show_params.description = 'Show rcParams'
        self.show_params.on_click(self.print_params)
        display(self.show_params)

    def print_params(self, button_instance):
        html = '<textarea rows="5" cols="50" readonly>{}</textarea>'
        self.params_text.value = html.format(pprint.pformat(mpl.rcParams))

    def process(self, param, value):
        self.params_text.value = ''
        mpl.rcParams[param] = value
        updates = collect.dict_updates(self.old, mpl.rcParams)
        self.updates_text.value = ('<p>mpl.RcParams updates {}</p>'.
                                   format(updates))

    def axes_page(self):
        box = widgets.Accordion()
        linewidth = create_linewidth_slider(0)
        linewidth.description = 'axes.linewidth'

        edgecolor = self.color_chooser('axes.edgecolor')
        titlesize = create_size_slider(12)
        titlesize.description = 'axes.titlesize'

        box.children = [edgecolor, linewidth, titlesize]
        box.set_title(0, edgecolor.description)
        box.set_title(1, linewidth.description)
        box.set_title(2, titlesize.description)

        def update_axes_linewidth(name, value):
            self.process(linewidth.description, value)

        def update_titlesize(name, value):
            self.process(titlesize.description, value)

        linewidth.on_trait_change(update_axes_linewidth, 'value')
        titlesize.on_trait_change(update_titlesize, 'value')

        return box

    def font_page(self):
        box = widgets.Accordion()
        size = widgets.FloatSlider(min=0, max=20, value=10,
                                   description='font.size')
        box.children = [size]

        def update_font_size(name, value):
            self.process(size.description, value)

        size.on_trait_change(update_font_size, 'value')

        return box

    def figure_page(self):
        box = widgets.VBox()
        box.description = 'figure.figsize'
        height = widgets.FloatSlider(min=0, max=16, value=8,
                                     description='Height')
        width = widgets.FloatSlider(
            min=0, max=12, value=6, description='Width')
        box.children = [height, width]

        def update_fig_size(name, value):
            self.process(box.description, (height.value, width.value))

        height.on_trait_change(update_fig_size, 'value')
        width.on_trait_change(update_fig_size, 'value')

        return box

    def grid_page(self):
        linewidth = create_linewidth_slider(2)
        linewidth.description = 'grid.linewidth'

        color = self.color_chooser('grid.color')
        box = widgets.Accordion(children=[linewidth, color])
        box.set_title(0, linewidth.description)
        box.set_title(1, color.description)

        def update_linewidth(name, value):
            self.process(linewidth.description, value)

        linewidth.on_trait_change(update_linewidth, 'value')

        return box

    def lines_page(self):
        linewidth = create_linewidth_slider(1)
        linewidth.description = 'lines.linewidth'
        box = widgets.Accordion(children=[linewidth])
        box.set_title(0, linewidth.description)

        def update_linewidth(name, value):
            self.process(linewidth.description, value)

        linewidth.on_trait_change(update_linewidth, 'value')

        return box

    def color_chooser(self, property):
        r = widgets.FloatSlider(min=0, max=1, description='Red')
        r.border_color = 'red'

        g = widgets.FloatSlider(min=0, max=1, description='Green')
        g.border_color = 'green'

        b = widgets.FloatSlider(min=0, max=1, description='Blue')
        b.border_color = 'blue'

        h = widgets.widget_string.HTML(property)

        def update(name, value):
            hex = rgb2hex((r.value, g.value, b.value))
            h.value = '<p style="background-color: {0};">{0}</p>'.format(hex)
            self.process(property, hex)

        r.on_trait_change(update, 'value')
        g.on_trait_change(update, 'value')
        b.on_trait_change(update, 'value')

        box = widgets.VBox(children=(r, g, b, h))
        box.border_style = 'dotted'
        box.description = property

        return box


def create_linewidth_slider(value, *args, **kwargs):
    return widgets.IntSlider(min=0, max=9, value=value, *args, **kwargs)


def create_size_slider(value, *args, **kwargs):
    return widgets.FloatSlider(min=0, value=value, *args, **kwargs)


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
