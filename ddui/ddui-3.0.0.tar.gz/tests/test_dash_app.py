from unittest.mock import mock_open, patch

from ddui.dash_app import _get_db_from_datadriver_dag


def setup_function():
    import os
    os.environ['AIRFLOW__CORE__DAGS_FOLDER'] = 'dags'
    os.environ['AIRFLOW__CORE__UNIT_TEST_MODE'] = 'True'
    import airflow
    airflow.configuration.load_test_config()

def test_get_db_from_datadriver_dag_should_return_db_object_when_DAGfile_contains_an_object_named_db():
    # Given
    dag_filepath = "/my/datadriver_dag.py"
    dag_python_src = "from mock import Mock \n" \
                     "db = Mock()"

    # When
    with patch("builtins.open", mock_open(read_data=dag_python_src)) as f_mock:
        result = _get_db_from_datadriver_dag(dag_filepath)

        # Then
        f_mock.assert_called_once_with(dag_filepath)


def test_get_db_from_datadriver_dag_should_return_db_object_when_DAGfile_contains_an_object_with_retrieve_table_method():
    # Given
    dag_filepath = "/my/datadriver_dag.py"
    dag_python_src = "from mock import Mock \n" \
                     "object_with_retrieve_table = Mock()"

    # When
    with patch("builtins.open", mock_open(read_data=dag_python_src)) as f_mock:
        result = _get_db_from_datadriver_dag(dag_filepath)

        # Then
        assert hasattr(result, "retrieve_table")

