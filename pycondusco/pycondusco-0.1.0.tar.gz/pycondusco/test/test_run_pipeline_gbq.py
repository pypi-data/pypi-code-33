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
from google.cloud import bigquery
import pycondusco
from pycondusco.run_pipeline_gbq import run_pipeline_gbq

class TestRunPipelineGBQ(unittest.TestCase):


    def test_run_pipeline_gqb(self):
        client = bigquery.Client()

        def pipeline(params):
            query = """
              SELECT
                {{#list}}
                  SUM(CASE WHEN author.name ='{{name}}' THEN 1 ELSE 0 END) as n_{{name_clean}},
                {{/list}}
                repo_name
              FROM `bigquery-public-data.github_repos.sample_commits`
              GROUP BY repo_name
            """

            query_job = client.query(pystache.render(query, params))
            results = query_job.result()  # Waits for job to complete.
            for row in results:
                print(dict(row.items()))


        query = """
           SELECT CONCAT('[',
           STRING_AGG(
             CONCAT('{\"name\":\"',name,'\",'
               ,'\"name_clean\":\"', REGEXP_REPLACE(name, r'[^[:alpha:]]', ''),'\"}'
             )
           ),
           ']') as list
           FROM (
             SELECT author.name,
               COUNT(commit) n_commits
             FROM `bigquery-public-data.github_repos.sample_commits`
             GROUP BY 1
             ORDER BY 2 DESC
             LIMIT 10
           )
        """

        run_pipeline_gbq(pipeline, client, query)


    def test_run_pipeline_gqb_multirow(self):
        client = bigquery.Client()

        def pipeline(params):
            query = """
                SELECT {{{value}}} AS value
                FROM `{{table_name}}`
                LIMIT {{limit_size}}
            """

            query_job = client.query(pystache.render(query, params))
            results = query_job.result()  # Waits for job to complete.
            for row in results:
                print(dict(row.items()))


        query = """
            SELECT
              100 AS value,
              'bigquery-public-data.samples.shakespeare' AS table_name,
              5 AS limit_size
            UNION ALL
            SELECT
              200 AS value,
              'bigquery-public-data.samples.shakespeare' AS table_name,
              2 AS limit_size
        """

        run_pipeline_gbq(pipeline, client, query)



if __name__ == '__main__':
    unittest.main()

