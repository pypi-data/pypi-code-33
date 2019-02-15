from empatican import cli
from empatican.interface import connect
import io
import os
import shlex
import shutil
import sys
from unittest import TestCase

FIXTURES_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), 'fixtures')


class ConnectTest(TestCase):
    '''LIVE Interact with Empatica Connect'''

    def setUp(self):
        self.assignment_csv = os.path.join(FIXTURES_DIR, 'assignments.csv')

    def test_list_cli(self):
        '''Basic list / search'''
        args = shlex.split('list --n-recent 2')
        parser = cli.add_parser()
        options = parser.parse_args(args)

        saved_stdout = sys.stdout
        try:
            out = io.StringIO()
            sys.stdout = out
            connect.search_or_download(vars(options))
            output = out.getvalue().strip()
            self.assertIn('device', output)
        finally:
            sys.stdout = saved_stdout

    def test_list_withassignment_cli(self):
        '''Search using device assignment table'''

        # With filenames, shlex isn't good with filenames including spaces
        # so skip it and explicilty use a list
        args = [
            'list', '--device-assignment', self.assignment_csv,
            '--participant-id', 'xyz003'
        ]

        parser = cli.add_parser()
        options = parser.parse_args(args)

        saved_stdout = sys.stdout
        try:
            out = io.StringIO()
            sys.stdout = out
            connect.search_or_download(vars(options))
            output = out.getvalue().strip()
            self.assertIn('device', output)
        finally:
            sys.stdout = saved_stdout

    def test_download_cli(self):
        '''Download small session with default filename'''
        # Download a 1 minute session
        args = shlex.split('download --empatica-id 565082')
        parser = cli.add_parser()
        options = parser.parse_args(args)

        zipfile = '1539959313_A01468.zip'
        if os.path.exists(zipfile):
            os.remove(zipfile)

        try:
            with self.assertLogs(level='INFO') as cm:
                connect.search_or_download(vars(options))
                self.assertRegex(''.join(cm.output), 'Success')
                self.assertTrue(os.path.exists(zipfile))

        finally:
            if os.path.exists(zipfile):
                os.remove(zipfile)

    def test_download_withassignment_cli(self):
        '''Download small session with study template'''

        template = 'study1/{participant_id}/{start_time}_{device_id}.zip'
        participant_id = 'xyz004'
        zipfile = template.format(
            participant_id=participant_id,
            start_time='1539959313',
            device_id='849318')
        # Download a 1 minute session
        args = [
            'download', '--empatica-id', '565082', '--device-assignment',
            self.assignment_csv, '--participant-id', participant_id,
            '--template', template
        ]
        parser = cli.add_parser()
        options = parser.parse_args(args)

        try:
            with self.assertLogs(level='INFO') as cm:
                connect.search_or_download(vars(options))
                self.assertRegex(''.join(cm.output), 'Success')
                self.assertTrue(os.path.exists(zipfile))
        finally:
            if os.path.exists('study1'):
                shutil.rmtree('study1')
            if os.path.exists(zipfile):
                os.remove(zipfile)
