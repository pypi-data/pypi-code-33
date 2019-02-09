from pyquilted.quilted.heading import Heading
from pyquilted.quilted.contacts_list import ContactsList
from pyquilted.quilted.style import Style


class Resume:
    def __init__(self, heading=None, contacts=None, sections=None, style=None):
        self.heading = heading
        self.contacts = contacts or []
        self.sections = sections or []
        self.style = style or vars(Style())

    def add_section(self, section):
        if type(section) is Heading:
            self._set_heading(section.serialize())
        elif type(section) is ContactsList:
            self._set_contacts(section.serialize())
        else:
            self.sections.append(section.serialize())

    def _set_heading(self, heading):
        self.heading = heading

    def _set_contacts(self, contacts):
        self.contacts = contacts
