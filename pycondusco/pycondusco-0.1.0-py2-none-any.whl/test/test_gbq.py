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
from google.cloud import bigquery

class TestGBQConn(unittest.TestCase):

    def test_gbq_conn(self):
        client = bigquery.Client()
        query_job = client.query("""
            SELECT
              10 AS hits
            FROM `bigquery-public-data.stackoverflow.posts_questions`
            LIMIT 1""")

        results = query_job.result()  # Waits for job to complete.

        for row in results:
            self.assertEqual(row.hits,10)


if __name__ == '__main__':
    unittest.main()

