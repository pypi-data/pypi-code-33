#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2018 jack <jack@bogon>
#
# Distributed under terms of the MIT license.

"""
ansible adaptor
"""

from idevops.utils import *
from idevops.ansible.ansible_playbook_runner import AnsiblePlaybookRunner
from ansible.plugins.callback import CallbackBase
from prettytable import PrettyTable

class CallbackMyTest(CallbackBase):
    """A sample callback plugin used for performing an action as results come in

    If you want to collect all results into a single object for processing at
    the end of the execution, look into utilizing the ``json`` callback plugin
    or writing your own custom callback plugin
    """

    data = {
        'bandwidth': {
	    'name': u'Bandwidth test result',
            'canton': u'C\S(Mbps)',
            'var': 'bd_result'
        },
        'latency': {
            'canton': u'C\S(ms)',
            'name': u'Latency test result',
            'var': 'lt_result'
        },
        'io': {
            'canton': u'\\',
            'name': u'Disk IO test result',
            'var': 'io_result'
        }
    }

    def __init__(self, fields=['bandwidth', 'latency', 'io']):
        self.__data = {}
        for f in fields:
            if f in self.data:
                self.data[f]['enable'] = True
                self.__data[self.data[f]['name']] = {
                    'canton': self.data[f]['canton'],
                    'var': self.data[f]['var']
                }

    def v2_runner_on_ok(self, result, **kwargs):
        if result.task_name in self.__data:
            data = result._result[self.__data[result.task_name]['var']]
            pt = PrettyTable()
            pt.title = result.task_name
            rows = sorted(data, key=natural_key)
            cols = sorted(data[rows[0]], key=natural_key)
            pt.field_names = [self.__data[result.task_name]['canton']] + cols
            for i in rows:
                this_row = [i]
                for j in cols:
                    this_row.append(data[i][j] if j != i else '\\')
                pt.add_row(this_row)
            print(pt)

def run_test(name, fields=['bandwidth', 'latency', 'io'], debug=False):
    extra = {}
    for f in fields:
        extra[f] = True
    test_runner = AnsiblePlaybookRunner(name=name, playbook=find_playbook('perform_test'), callback=CallbackMyTest(fields), extra=extra, debug=debug)
    return test_runner.run()
