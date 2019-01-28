# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Handler object."""


class HandlersStore:
    """Stores handlers."""

    handlers = []

    def __init__(self):
        """init."""
        self.handlers = []

    def prepend_handler(self, new_handler):
        """Prepend handler.

        :param new_handler:
        :return:
        """
        for handler in self.handlers:
            if handler.name == new_handler.name:
                raise Exception(
                    "Handler with name already exists: {}".format(handler.name))
        self.handlers.insert(0, new_handler)

    def append_handler(self, new_handler):
        """Append handler.

        :param new_handler:
        :return:
        """
        for handler in self.handlers:
            if handler.name == new_handler.name:
                raise Exception(
                    "Handler with name already exists: {}".format(handler.name))
        self.handlers.append(new_handler)

    def remove_handler(self, name):
        """Remove handler by name.

        :param name:
        :return:
        """
        updated_handlers = []
        found = False
        for hh in self.handlers:
            if hh.name == name:
                found = True
            else:
                updated_handlers.append(hh)
        self.handlers = updated_handlers
        return found

    def find_handler_by_name(self, name):
        """Find handler by name.

        :param name:
        :return:
        """
        handler = next(hh for hh in self.handlers if hh.name == name)
        return handler

    def find_handler_by_model(self, model):
        """Find handler by testing model.

        :param model:
        :return:
        """
        handler = next(hh for hh in self.handlers if hh.can_save(model))
        return handler


class Handler(object):
    """Handler."""

    def __init__(self, name):
        """init.

        :param name:
        """
        self.name = name


class ModelHandler(Handler):
    """Model Handler."""

    def __init__(self, name, can_save, save, load):
        """init.

        :param name:
        :param can_save:
        :param save:
        :param load:
        """
        super(ModelHandler, self).__init__(name)
        self.can_save = can_save
        self.save = save
        self.load = load


class ModeldataHandler(Handler):
    """Model data handler."""

    def __init__(self, name, can_save, save):
        """init.

        :param name:
        :param can_save:
        :param save:
        """
        super(ModeldataHandler, self).__init__(name)
        self.can_save = can_save
        self.save = save
