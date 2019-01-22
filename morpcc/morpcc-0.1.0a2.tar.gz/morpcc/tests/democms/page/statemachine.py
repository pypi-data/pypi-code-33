import morpfw
from .model import PageModel
from ..app import App


class PageStateMachine(morpfw.StateMachine):
    states = ['new', 'approved', 'rejected']

    transitions = [
        {'trigger': 'approve', 'source': 'new', 'dest': 'approved'},
        {'trigger': 'reject', 'source': 'new', 'dest': 'rejected'},
    ]


@App.statemachine(model=PageModel)
def get_dataasset_statemachine(obj):
    return PageStateMachine(obj)
