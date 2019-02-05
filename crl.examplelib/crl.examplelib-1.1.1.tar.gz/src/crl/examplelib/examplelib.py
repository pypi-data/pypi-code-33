from __future__ import print_function
from crl.examplelib.examplelib_implementation import (
    other_example_implementation)


__copyright__ = 'Copyright (C) 2019, Nokia'


def example():
    """Just an example which prints 'example called'.

    Example:

    +---------+
    | example |
    +---------+

    See also \'Other Example\'.

    """

    print('example called')


def other_example(example_output):
    """Another example which prints either 'other_example_called' or the value
    of *example_output* if it is not empty.

    Example:

    +---------------+-------------+
    | Other Example | example     |
    |               | output      |
    +---------------+-------------+
    """
    other_example_implementation(example_output)


def new_example():
    """New example keyword which just returns 'new example'.
    """
    return 'new example in demo'


class Example(object):

    def __init__(self, example_output):
        self.example_output = example_output

    def example(self):
        """ Example library prints argument passed to the library
        initialization.

        Example:

        +-----------------+--------------+-----------------+
        | Library         | Example      | example_output  |
        +-----------------+--------------+-----------------+
        | Example.example |              |                 |
        +-----------------+--------------+-----------------+

        """
        other_example(self.example_output)
