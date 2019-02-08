import unittest
from .modelchoices import Choices


class ChoicesTest(unittest.TestCase):

    def test_not_tuple_error(self):
        with self.assertRaises(AssertionError):

            class Animals(Choices):
                CAT = [1, 'cat']  # a list, not a tuple
                DOG = [2, 'dog']  # a list, not a tuple

    def test_wrong_tuple_length_error(self):
        with self.assertRaises(AssertionError):

            class Animals(Choices):
                CAT = 1, 'cat', 45  # three members instead of two
                DOG = 2, 'dog', 45  # three members instead of two

    def test_success(self):
        class Animals(Choices):
            CAT = 1, 'cat'
            DOG = 2, 'dog'

        self.assertEqual(Animals.CAT, 1)  # Test that choices variable's value is the db value, not the original tuple.
        self.assertEqual(Animals.CHOICES, ((1, 'cat'), (2, 'dog')))  # This format is acceptable for Django Field.


if __name__ == '__main__':
    unittest.main()
