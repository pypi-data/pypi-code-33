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
import json
import sys

def run_pipeline(pipeline, parameters):
    assert(len(parameters)>0)
    for p in parameters:
        for k,v in p.iteritems() :
            try:
                p[k] = json.loads(p[k])
            except ValueError as err:
                pass
            except TypeError as err:
                pass
            except:
                print "Unexpected error:", sys.exc_info()[0]
        pipeline(p)

