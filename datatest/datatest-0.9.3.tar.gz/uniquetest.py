from datatest import validate
from datatest.validation import validate2
from datatest import Extra
from datatest._required import Required


@group_requirement
def required_unique(iterable):
    previously_seen = set()
    for value in iterable:
        if value in previously_seen:
            yield Extra(value)
        else:
            previously_seen.add(value)



@group_requirement
def required_unique(iterable):
    previously_seen = set()
    extras = []
    for value in iterable:
        if value in previously_seen:
            extras.append(value)
        else:
            previously_seen.add(value)
    differences = (Extra(value) for value in extras)
    description = 'values are not unique, contains duplicates'
    return differences, description






class RequiredUnique(Required):
    """Values should be unique."""

    def filterfalse(self, iterable):
        """Returns Extra difference for each duplicate value."""
        previously_seen = set()

        for value in iterable:
            if value in previously_seen:
                yield Extra(value)
            else:
                previously_seen.add(value)


def test_is_unique():

    data = ['a', 'b', 'a', 'c']  # <- 'a' is not unique

    validate2(data, RequiredUnique())


class RequiredAscending(Required):
    def filterfalse(self, iterable):
        """Returns Extra difference for each duplicate value."""
        previously_seen = set()

        for value in iterable:
            if value in previously_seen:
                yield Extra(value)
            else:
                previously_seen.add(value)


class RequiredSorted(Required):
    def __init__(self, key=None, reversed=False):
        pass

    def failure_message(self):
        return 'sdf'

    failure_message = 'data is not sorted'


    def filterfalse(self, iterable):
        """Returns Extra difference for each duplicate value."""
        iterator = iter(iterable)  # Must be iterator.

        previous_value = next(iterator)
        for value in iterator:
            try:
                if value < previous_value:
                    yield Invalid(value)
            except:
                yield Invalid(value)
            previous_value = value

