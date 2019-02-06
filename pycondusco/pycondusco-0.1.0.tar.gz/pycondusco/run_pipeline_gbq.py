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
from google.cloud import bigquery
from run_pipeline import run_pipeline

def run_pipeline_gbq(pipeline, client, query):
    query_job = client.query(query)
    results = query_job.result()
    parameters = []
    for row in results:
        items = dict(row.items())
        parameters.append(items)

    run_pipeline(pipeline, parameters)
