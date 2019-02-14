from __future__ import absolute_import

from python_state_machine.orm.base import BaseAdaptor


def get_adaptor(original_class):
    # if none, then just keep state in memory
    adaptor = NullAdaptor(original_class)
    return adaptor


class NullAdaptor(BaseAdaptor):
    def extra_class_members(self, initial_state):
        return {"aasm_state": initial_state.name}

    def update(self, document, state_name):
        document.aasm_state = state_name
