from datetime import datetime

import time
import re

class Formatter():
    """
    This class represents the formatters.
    Formatter is a special object with main purpose to format the strings
    according to the pattern and the forms listed. The string may include
    datetime and variables forms.
    Parameters:
    pattern
        string that must be formatted.
    kwargs
        collection of variables used in string formatting.
    """
    def __init__(self, pattern, **kwargs):
        self.forms = {}
        self._set_all(pattern, **kwargs)
        pass

    def __str__(self):
        return self.format()

    __repr__ = __str__

    def format(self, **kwargs):
        """Main method that returns the formatted string from pattern."""
        forms = self.forms.copy()
        forms.update(kwargs)
        return self.pattern.format(**forms)
        # return time.strftime(self.pattern.format(**forms))

    def copy(self, pattern=None, **kwargs):
        """Copy current formatter to the new instance."""
        pattern = self.pattern if pattern is None else pattern
        forms = self.forms.copy()
        forms.update(kwargs)
        return Formatter(pattern, **forms)

    def modify(self, pattern=None, **kwargs):
        """Modify the pattern or modify/add new forms."""
        self._set_all(pattern=pattern, **kwargs)
        pass

    def _set_all(self, pattern=None, **kwargs):
        """Initialize all attributes in right order."""
        self._set_forms(**kwargs)
        self._set_pattern(pattern)
        pass

    def _set_pattern(self, pattern=None):
        """Initialize the pattern."""
        if pattern is not None:
            self.pattern = str(pattern)
            # Test pattern on unknown forms.
            used_forms = re.findall(r'{.*?[}|:]', self.pattern)
            for form in used_forms:
                name_form = form[1:-1]
                str_w_form = f'{{{name_form}}}'
                try:
                    str_w_form.format(**self.forms)
                except KeyError:
                    self._set_forms(name_form)
        elif hasattr(self, 'pattern') is False:
            self.pattern = ''
        pass

    def _set_forms(self, *args, **kwargs):
        """
        Initialize the forms.
        If the variable is ordered then add it with "None" value.
        Used mostly for the cases when the pattern include unknown forms to
        prevent errors.
        """
        if args:
            for arg in args:
                self.forms[arg] = 'NONE'
        if kwargs:
            for key, value in kwargs.items():
                if value is None:
                    value = 'NONE'
                self.forms[key] = value
        pass
