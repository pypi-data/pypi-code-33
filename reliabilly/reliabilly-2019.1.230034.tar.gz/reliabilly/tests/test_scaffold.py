from unittest import TestCase
from unittest.mock import MagicMock
from reliabilly.scaffold.generator import camelize, Generator, scaffold_up_service


class TestScaffold(TestCase):
    def test_camelcase(self):
        result = camelize('jared_test_example_item')
        self.assertEqual(result, 'JaredTestExampleItem')

    def test_generator(self):
        mock = MagicMock()
        generator = Generator(open=mock, mkdirs=mock)
        self.assertTrue(generator.scaffold_up_service('test_service', 1))

    def test_entrypoint(self):
        mock = MagicMock()
        self.assertTrue(scaffold_up_service('test_service', 5, mock))
        mock.scaffold_up_service.assert_called_once_with('test_service', 5)
