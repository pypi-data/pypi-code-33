from IPython.display import display
from IPython.display import Math
from IPython.html import widgets
from dautil import collect
from dautil import conf
from dautil import ts
from dautil import log_api
import matplotlib as mpl
from matplotlib.colors import rgb2hex
import pprint
from matplotlib.colors import ColorConverter


def create_month_widget(month, *args, **kwargs):
    return widgets.Dropdown(options=ts.short_months(),
                            selected_label=month, *args, **kwargs)


# TODO mix DIY widgets with WidgetFactory calls
class RcWidget():

    def __init__(self, context=None):
        self.context = context

        if self.context:
            rc = self.context.read_rc()

            if rc:
                mpl.rcParams.update(rc)

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

        if self.context:
            self.context.update_rc(updates)

        self.updates_text.value = ('<p>mpl.RcParams updates {}</p>'.
                                   format(updates))

    def axes_page(self):
        box = widgets.Accordion()
        linewidth = create_linewidth_slider('axes.linewidth')

        edgecolor = self.color_chooser('axes.edgecolor')
        titlesize = create_size_slider('axes.titlesize')

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
        size = create_size_slider('font.size')
        box.children = [size]

        def update_font_size(name, value):
            self.process(size.description, value)

        size.on_trait_change(update_font_size, 'value')

        return box

    def figure_page(self):
        box = widgets.VBox()
        box.description = 'figure.figsize'
        height = widgets.FloatSlider(min=0, max=16,
                                     value=mpl.rcParams[box.description][0],
                                     description='Height')
        width = widgets.FloatSlider(
            min=0, max=12, value=mpl.rcParams[box.description][1],
            description='Width')
        box.children = [height, width]

        def update_fig_size(name, value):
            self.process(box.description, (height.value, width.value))

        height.on_trait_change(update_fig_size, 'value')
        width.on_trait_change(update_fig_size, 'value')

        return box

    def grid_page(self):
        logger = log_api.env_logger('grid_page')
        logger.debug('Created grid page')
        linewidth = create_linewidth_slider('grid.linewidth')

        color = self.color_chooser('grid.color')
        box = widgets.Accordion(children=[linewidth, color])
        box.set_title(0, linewidth.description)
        box.set_title(1, color.description)

        def update_linewidth(name, value):
            self.process(linewidth.description, value)

        linewidth.on_trait_change(update_linewidth, 'value')

        return box

    def lines_page(self):
        linewidth = create_linewidth_slider('lines.linewidth')
        box = widgets.Accordion(children=[linewidth])
        box.set_title(0, linewidth.description)

        def update_linewidth(name, value):
            self.process(linewidth.description, value)

        linewidth.on_trait_change(update_linewidth, 'value')

        return box

    # TODO allow ‘rgbcmykw’
    # TODO allow standard names like 'aqua'
    def color_chooser(self, property):
        cc = ColorConverter()
        rgb = cc.to_rgb(mpl.rcParams[property])
        logger = log_api.env_logger('color_chooser')
        logger.debug('{0} {1}'.format(property, rgb))

        r = widgets.FloatSlider(min=0, max=1, value=rgb[0], description='Red')
        r.border_color = 'red'

        g = widgets.FloatSlider(min=0, max=1, value=rgb[1], description='Green')
        g.border_color = 'green'

        b = widgets.FloatSlider(min=0, max=1, value=rgb[2], description='Blue')
        b.border_color = 'blue'

        h = widgets.widget_string.HTML(property)
        # TODO put this in a func
        hex = rgb2hex((rgb[0], rgb[1], rgb[2]))
        h.value = '<p style="background-color: {0};">{0}</p>'.format(hex)

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


def create_linewidth_slider(desc, *args, **kwargs):
    return widgets.IntSlider(min=0, max=9, value=mpl.rcParams[desc],
                             description=desc, *args, **kwargs)


def create_size_slider(desc, *args, **kwargs):
    return widgets.FloatSlider(min=0, value=mpl.rcParams[desc],
                               description=desc, *args, **kwargs)


class LatexRenderer():

    # TODO do something with the context
    def __init__(self, chapter=None, start=1, context=None):
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


# TODO store key/id information in sql lite db in CONF_DIR
# with key mnemonic, creation time etc
class Context():
    def __init__(self, fname):
        self.fname = fname
        self.labels = fname + '.labels'

    def read_rc(self):
        rc = conf.read_rc()

        if rc:
            rc = rc.get(self.fname, {})

        return rc

    def update_rc(self, updates):
        conf.update_rc(self.fname, updates)

    def read_labels(self):
        rc = conf.read_rc()

        if rc:
            rc = rc.get(self.labels, None)

        return rc

    def update_labels(self, updates):
        conf.update_rc(self.labels, updates)


class LabelWidget():
    def __init__(self, nrows, ncols, context):
        self.context = context
        self.labels = collect.GridList(nrows, ncols, {})
        self.read_old_labels()

        for i in range(nrows):
            children = []

            for j in range(ncols):
                labels_box = self.create_mpl_labels_box(i, j,
                                                        self.labels.grid[i][j])
                children.append(labels_box)

            display(widgets.HBox(children=children))
            display(widgets.HTML('<br/>'))

    def read_old_labels(self):
        old = self.context.read_labels()

        if old:
            self.labels.fill(old)

    def update(self, name, value, row, col):
        self.labels.update(row, col, {name: value})
        self.context.update_labels(self.labels.grid)

    def create_mpl_labels_box(self, row, col, old):
        box = widgets.VBox()
        box.border_color = 'red'
        coord = ' [{0}][{1}]'.format(row, col)
        title = widgets.widget_string.Text(old.get('title', ''),
                                           description='title' + coord)
        xlabel = widgets.widget_string.Text(old.get('xlabel', ''),
                                            description='xlabel' + coord)
        ylabel = widgets.widget_string.Text(old.get('ylabel', ''),
                                            description='ylabel' + coord)
        box.children = [title, xlabel, ylabel]

        def update_title(name, value):
            self.update('title', value, row, col)

        title.on_trait_change(update_title, 'value')

        def update_xlabel(name, value):
            self.update('xlabel', value, row, col)

        xlabel.on_trait_change(update_xlabel, 'value')

        def update_ylabel(name, value):
            self.update('ylabel', value, row, col)

        ylabel.on_trait_change(update_ylabel, 'value')

        return box
