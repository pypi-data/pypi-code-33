import unittest
from unittest.mock import patch

from fake_ubersmith import main


class TestMain(unittest.TestCase):

    @patch('fake_ubersmith.main.Flask')
    @patch('fake_ubersmith.main.DataStore')
    @patch('fake_ubersmith.main.AdministrativeLocal')
    @patch('fake_ubersmith.main.UbersmithBase')
    @patch('fake_ubersmith.main.Uber')
    @patch('fake_ubersmith.main.Order')
    @patch('fake_ubersmith.main.Client')
    def test_app_runs(
            self, m_client, m_order, m_uber, m_uber_base, m_admin_local,
            m_data_store, m_flask
    ):
        main.run()

        m_flask.assert_called_once_with('fake_ubersmith')

        m_data_store.assert_called_once_with()

        m_uber_base.assert_called_once_with(m_data_store.return_value)

        m_admin_local.assert_called_once_with()
        m_admin_local.return_value.hook_to.assert_called_once_with(
            m_flask.return_value
        )

        m_uber.assert_called_once_with(m_data_store.return_value)
        m_uber.return_value.hook_to.assert_called_once_with(
            m_uber_base.return_value
        )

        m_order.assert_called_once_with(m_data_store.return_value)
        m_order.return_value.hook_to.assert_called_once_with(
            m_uber_base.return_value
        )

        m_client.assert_called_once_with(m_data_store.return_value)
        m_client.return_value.hook_to.assert_called_once_with(
            m_uber_base.return_value
        )

        m_flask.return_value.run.assert_called_once_with(
            host="0.0.0.0", port=9131
        )
