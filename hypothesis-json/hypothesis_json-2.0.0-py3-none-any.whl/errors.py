from hypothesis.errors import InvalidArgument


class InvalidArgumentValue(InvalidArgument, ValueError):
    """Used to indicate that arguments passed to a Hypothesis strategy have a invalid value."""
