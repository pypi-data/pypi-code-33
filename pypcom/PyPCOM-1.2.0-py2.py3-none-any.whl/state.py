from pypcom import PC


class State(object):
    """The expected state of the object being checked.

    Instances of this class can be created with multiple expected attributes to
    be checked against the test subject object all at once when compared through
    ``__eq__``. For each expected attribute that is passed, each will be
    utilized even if others had problems. When all are used, the ``State``
    object will check their results and return ``True`` if all passed, or
    ``False`` if any had a problem.

    Each expected attribute is responsible for handling the logic for how to
    compare against the test subject. If they find a problem, they are
    responsible for storing that problem in their ``self._problems`` list
    through their ``self.add_problem`` method, which the ``State`` object will
    check through their ``self.get_problems`` method once it has used all of its
    expected attributes. The expected attributes can also just raise an
    ``AssertionError`` in their ``compare`` method, and the ``State`` object
    will catch it and include it in the reported problems.

    When the ``State`` has all the reported problems, it will bundle them up
    into a readable string accessed through ``self.get_report()``, so they can
    all be reported as one failure. This is meant for pytest to access during
    its ``pytest_assertrepr_compare`` hook, so that a readable representation of
    the failure can be provided.
    """

    def __init__(self, *expected_attributes):
        self._expected_attributes = expected_attributes
        self._problems = []
        self._other_class_name = None

    def __eq__(self, other):
        self._other_class_name = other.__class__.__name__
        for attr in self._expected_attributes:
            attr.safe_compare(other)
            self.add_problems_of_attr(attr)
        if self._problems:
            return False

    def add_problems_of_attr(self, attr):
        """Grab and store the reported problems of the ``ExpectedAttribute``."""
        problems = attr.get_problems()
        if problems:
            self._problems.append(
                {
                    "attribute": attr,
                    "problems": problems,
                },
            )

    def get_pytest_failure_report_repr(self):
        rep = []
        rep.append("Comparing {} State:".format(self._other_class_name))
        for problem_set in self._problems:
            attr_name = problem_set["attribute"].get_name()
            for problem in problem_set["problems"]:
                msg = "    {}: {}".format(
                    attr_name,
                    problem.args[0].split("\n")[0] or False,
                )
                rep.append(msg)
        return rep


class ExpectedAttribute(object):

    _problems = None
    name = None

    def get_name(self):
        """The name of the attribute to be used in the failure message."""
        return self.name or self.__class__.__name__

    def safe_compare(self, other):
        """Compares, but catches ``AssertionError`` to add to problems."""
        try:
            self.compare(other)
        except AssertionError as e:
            self.add_problem(e)

    def compare(self, other):
        raise NotImplementedError(
            "Must be overridden to define how to check the attribute.",
        )

    def add_problem(self, problem):
        """Add a problem to the list of problems for this attribute."""
        if self._problems is None:
            self._problems = []
        self._problems.append(problem)

    def get_problems(self):
        """Get all problems for this attribute."""
        return self._problems or ()
