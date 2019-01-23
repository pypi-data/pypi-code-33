from unittest import TestCase
from unittest.mock import MagicMock
from reliabilly.components.web.paged_requester import PagedRequester

DUMMY = "dummy"


class PagedRequesterTests(TestCase):
    def test_init(self):
        mock = MagicMock()
        paged_requester = PagedRequester(DUMMY, client=mock,
                                         circuit_breaker=mock)
        self.assertEqual(paged_requester.current_offset, 0)
        self.assertEqual(paged_requester.total, None)
        self.assertEqual(paged_requester.circuit_breaker, mock)
        self.assertEqual(paged_requester.client, mock)

    def test_has_next_with_none_total(self):
        paged_requester = PagedRequester(DUMMY)
        has_next = paged_requester.has_next()
        self.assertIsNone(has_next)

    def test_has_next_with_total(self):
        mock = MagicMock()
        json_mock = MagicMock()
        json_mock.json.return_value = {"dummy": [], "total": 0, "limit": 25}
        mock.request.return_value = json_mock
        paged_requester = PagedRequester(DUMMY, client=mock)
        paged_requester.get_next_page()
        self.assertIsNotNone(paged_requester.total)
        has_next = paged_requester.has_next()
        self.assertFalse(has_next)

    def test_has_next_true(self):
        mock = MagicMock()
        json_mock = MagicMock()
        json_mock.json.return_value = {"dummy": [{"item": 1, "item2": 2}], "total": 2, "limit": 1}
        mock.request.return_value = json_mock
        paged_requester = PagedRequester(DUMMY, client=mock)
        paged_requester.get_next_page()
        self.assertIsNotNone(paged_requester.total)
        self.assertTrue(paged_requester.has_next())
        self.assertEqual(paged_requester.current_offset, 1)

    def test_has_next_false_at_end(self):
        mock = MagicMock()
        json_mock = MagicMock()
        json_mock.json.return_value = {"dummy": [{"item": 1, "item2": 2}], "total": 2, "limit": 1}
        mock.request.return_value = json_mock
        paged_requester = PagedRequester(DUMMY, client=mock)
        paged_requester.get_next_page()
        paged_requester.get_next_page()
        self.assertIsNotNone(paged_requester.total)
        self.assertFalse(paged_requester.has_next())

    def test_get_all(self):
        mock = MagicMock()
        json_mock = MagicMock()
        json_mock.json.return_value = {"dummy": [{"item": 1, "item2": 2}], "total": 2, "limit": 1}
        mock.request.return_value = json_mock
        paged_requester = PagedRequester(DUMMY, client=mock)
        paged_requester.get_all()
        self.assertEqual(2, mock.request.call_count)

    def test_get_all_with_3(self):
        mock = MagicMock()
        json_mock = MagicMock()
        json_mock.json.return_value = {"dummy": [{"item": 1, "item2": 2}], "total": 3, "limit": 1}
        mock.request.return_value = json_mock
        paged_requester = PagedRequester(DUMMY, client=mock)
        paged_requester.get_all()
        self.assertEqual(3, mock.request.call_count)
