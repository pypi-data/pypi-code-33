"""Reusable unique item gatherer. Returns unique values with optional list_in and blacklists"""


class GatherUnique:
    """
    Reusable unique item gatherer. Returns unique values with optional list_in and blacklists
    """

    def __init__(self):
        self._black_lists = []
        """list of items to verify against"""

        self._gathered = []
        """sorted and unique items"""

    def _clear_holds(self):
        """Clear hold attributes"""
        self._black_lists.clear()
        self._gathered.clear()

    def _not_in_args(self, check):
        """Check item against black lists"""
        for arg_list in self._black_lists:
            if check in arg_list:
                return False
        return True

    def _gather_stdin(self, header: str = '') -> None:
        """
        Gathers input from user, split by newline. Runs until blank line submitted.
        Sorts against blacklists into _gathered
        """
        print("\n" + header + "\n")

        prompt: str = None
        while prompt != '':
            prompt = input('> ').lower().strip()
            if prompt != '' and prompt not in self._gathered and self._not_in_args(prompt):
                self._gathered.append(prompt)

    def _gather_list_in(self, list_in):
        """
        Gathers items from given list_in, sorts against blacklists into _gathered
        """
        for item in list_in:
            if item not in self._gathered and self._not_in_args(item):
                self._gathered.append(item)

    def run(self, *args: list, list_in: list = None, header: str = '',) -> list:
        """
        Runs gathering and sorting procedures
        Calls appropriate _gatherer based on list_in presence
        Returns unique list _gatherd
        Checks input value against itself and optional provided lists in args to ensure unique and
        allowed values only
        """

        self._clear_holds()

        for arg in args:
            self._black_lists.append(arg)

        if list_in:
            self._gather_list_in(list_in)
        else:
            self._gather_stdin(header)

        return self._gathered
