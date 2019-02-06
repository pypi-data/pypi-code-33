#    Copyright (C) 2018 Roland Stevenson
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.
#==============================================================================
import unittest
import pytest
import pystache
import pycondusco
from pycondusco.run_pipeline import run_pipeline

class TestRunPipeline(unittest.TestCase):

    def test_run_pipeline(self):
        json_string = '{"first_name": "First", "last_name":"Last"}'

        params = [
            {
                'k1':'v1',
                'k2':'v2',
            },
            {
                'k1':'v1',
                'k2': json_string,
            },
        ]

        def pipeline(params):
            print pystache.render('k1 value is {{k1}}, k2 is {{k2}}',params)

        run_pipeline(pipeline,params)


if __name__ == '__main__':
    unittest.main()

