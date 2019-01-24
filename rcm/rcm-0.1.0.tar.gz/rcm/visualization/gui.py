import ipywidgets as widgets
from IPython.display import display

from .map import draw_map


def create_gui(model):
    def step_and_show(b):
        with w['log']:
            print("Stepping model by ", w['slider'].value, " steps")
            w['progress'].value = 0
            w['progress'].max = w['slider'].value + len(model.locations)
            for i in range(w['slider'].value):
                model.step()
                w['progress'].value = i+1
                w['step'].value = str(model.schedule.steps)
        draw_map(w['map'], model, w['progress'])

    w = {}
    w['map'] = widgets.Output(layout={'border': '1px solid black'})
    w['log'] = widgets.Output(layout={'border': '1px solid black'})

    w['slider'] = widgets.IntSlider(
        value=1,
        min=1,
        max=100,
        step=1,
        description='Step size:',
        disabled=False,
        continuous_update=False,
        orientation='horizontal',
        readout=True,
        readout_format='d'
    )

    w['progress'] = widgets.IntProgress(
        value=0,
        min=0,
        max=len(model.locations),
        step=1,
        description='calculating:',
        bar_style='info',  # 'success', 'info', 'warning', 'danger' or ''
        orientation='horizontal'
    )

    w['button'] = widgets.Button(
        description='Step',
        disabled=False,
        button_style='',
        tooltip='Click me',
        icon='check'
    )
    w['button'].on_click(step_and_show)

    w['step'] = widgets.Label(
        value=str(model.schedule.steps)
    )

    display(widgets.VBox([widgets.HBox([w['button'], w['slider'], w['progress'], widgets.Label(value='Current Step: '), w['step']]), w['map'], w['log']]))
    return w
