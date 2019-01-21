import inspect
import os

from openlego.api import AbstractDiscipline


class SsbjDiscipline(AbstractDiscipline):

    @property
    def name(self):
        # type: () -> str
        """:obj:`str`: Name of this discipline."""
        return self.__class__.__name__

    @property
    def creator(self):
        return u'S. Dubreuil and R. Lafage'

    @property
    def owner(self):
        return u'J. Sobieszczanski-Sobieski'

    @property
    def operator(self):
        return u'I. van Gent'

    @property
    def description(self):
        return u'Discipline of the SSBJ test case.'

    @property
    def version(self):
        return u'1.0'

    @property
    def path(self):
        # type: () -> str
        """:obj:`str`: Path at which this discipline resides."""
        return os.path.dirname(inspect.getfile(self.__class__))

    def generate_input_xml(self):
        raise NotImplementedError

    def generate_output_xml(self):
        raise NotImplementedError
