#!/usr/bin/env python

from __future__ import absolute_import

import cement.core.foundation

import achso.controller
from achso.commands.languages import Languages
from achso.commands.sample import Sample
from achso.commands.submissions import Submissions
from achso.commands.submit import Submit
from achso.commands.tasks import Tasks
from achso.commands.test import Test

class AchSo(cement.core.foundation.CementApp):
    class Meta:
        label = 'achso'
        base_controller = 'base'
        handlers = [
            achso.controller.Controller,
            Languages,
            Sample,
            Submissions,
            Submit,
            Tasks,
            Test,
        ]
        exit_on_close = True
        extensions = ['json']
        config_handler = 'json'
        output_handler = 'json'

def main():
    with AchSo() as app:
        try:
            app.run()
        except Exception as e:
            app.render({'error': {
                'type': e.__class__.__name__,
                'body': str(e)
            }})
            app.exit_code = 1
