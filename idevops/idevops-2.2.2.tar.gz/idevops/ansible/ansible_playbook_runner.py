#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2018 jack <jack@bogon>
#
# Distributed under terms of the MIT license.

"""
custom ansible playbook runner using ansible python api
"""

import ansible.constants as C
from ansible.executor.playbook_executor import PlaybookExecutor
from ansible.inventory.manager import InventoryManager
from ansible.parsing.dataloader import DataLoader
from ansible.plugins.callback import CallbackBase
from ansible.vars.manager import VariableManager
from ansible.cli.playbook import PlaybookCLI

from idevops.utils import get_path

class AnsiblePlaybookRunner():

    def __init__(self, name, playbook, callback=None, extra={}, debug=False):

        loader = DataLoader()
        inventory = InventoryManager(loader=loader, sources=get_path(name, 'inventory'))
        variable_manager = VariableManager(loader=loader, inventory=inventory)
        variable_manager.extra_vars = extra
        passwords = {}

        cli = PlaybookCLI(['', playbook])
        cli.parse()

        self.__pbex = PlaybookExecutor(playbooks=[playbook], inventory=inventory, variable_manager=variable_manager, loader=loader, options=cli.options, passwords=passwords)
        if not debug and callback:
            self.__pbex._tqm._stdout_callback = callback

    def run(self):
        return self.__pbex.run()

