

from kabaret.flow import (
    values,
    Object, Map, Action, ConnectAction,
    ChoiceValueSetAction, ChoiceValueSelectAction,
    Child, Parent, Computed, Connection,
    Param, IntParam, BoolParam, HashParam
)

from .icon_browser import IconBrowserGroup
from .showcase import ValuesGroup, MapsGroup, EditorsGroup, RelationsGroup, ActionsGroup


class UnittestProject(Object):

    values = Child(ValuesGroup)
    maps = Child(MapsGroup)
    relations = Child(RelationsGroup)
    editors = Child(EditorsGroup)
    actions = Child(ActionsGroup)

    icons = Child(IconBrowserGroup)
