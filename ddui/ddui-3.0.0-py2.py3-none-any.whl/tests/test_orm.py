from unittest.mock import patch, ANY, Mock

import pandas as pd
from pandas.testing import *


def setup_function(function):
    import os
    os.environ['AIRFLOW__CORE__DAGS_FOLDER'] = 'dags'
    os.environ['AIRFLOW__CORE__UNIT_TEST_MODE'] = 'True'
    import airflow
    airflow.configuration.load_test_config()


@patch('pandas.read_sql')
@patch('airflow.models.DagBag')
def test_airflow_dags_should_return_dags_with_their_informations_without_outdated_dags(dagbag_mock, reaq_sql_mock):
    # Given
    from ddui.orm import airflow_dags
    reaq_sql_mock.return_value = pd.DataFrame(
        data=[
            ['test_dag', None, None, None, None, None, None, None, None, None, None],
            ['outdated_dag', None, None, None, None, None, None, None, None, None, None],
        ],
        columns=['dag_id', 'is_paused', 'is_subdag', 'is_active', 'last_scheduler_run',
                 'last_pickled', 'last_expired', 'scheduler_lock', 'pickle_id',
                 'fileloc', 'owners']
    )

    def get_dag(dag_id):
        d = Mock()
        if 'outdated' in dag_id:
            return setattr(d, 'roots', None)
        return d
    dagbag_mock.return_value.get_dag.side_effect = get_dag


    # When
    result = airflow_dags()


    # Then
    sql_statement_expected = "SELECT dag.dag_id, dag.is_paused, dag.is_subdag, dag.is_active, " \
                             "dag.last_scheduler_run, dag.last_pickled, dag.last_expired, dag.scheduler_lock, " \
                             "dag.pickle_id, dag.fileloc, dag.owners" \
                             " \nFROM dag"
    reaq_sql_mock.assert_called_once_with(sql_statement_expected,
                                          ANY)
    assert_series_equal(pd.Series(data=['test_dag'], name='dag_id'), result['dag_id'])
