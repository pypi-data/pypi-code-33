

class Parent:
    """
    Parent for all bare containers.

    Parameters
    ----------
        _dict : :class:`dict`
            Dictionary containing every specific container data.

    Attributes
    ----------
    digital
        :class:`str`
        Time in digital format
    name
        :class:`str`
        Name, example: 'Python' if os, 'Pycharm' if editor...
    hours
        :class:`int`
        hours
    minutes
        :class:`int`
        minutes
    seconds
        :class:`int`
        seconds
    percent
        :class:`float`
        Percentage
    text
        :class:`str`
        Time written in text format, ex: 5 minutes.
    total_time
        :class:`int`
        total time in seconds
    type
        Usually :class:`NoneType`

    """
    def __init__(self, _dict):
        self.digital = _dict.get('digital')
        self.hours = _dict.get('hours')
        self.minutes = _dict.get('minutes')
        self.name = _dict.get('name')
        self.percent = _dict.get('percent')
        self.seconds = _dict.get('seconds')
        self.text = _dict.get('text')
        self.total_time = _dict.get('total_seconds')
        self.type = _dict.get('type')

    def __repr__(self):

        return f"class <'{self.__class__.__name__}({self.name})'>"


class Project:
    """
    Represents a Project. It contains every container-bare plus three more.

    This class adds overall more accuracy in the timings within a  :class:`.Day`

    Parameters
    ----------
    _dict : :class:`dict`
        Dictionary that contains all the data.

    Attributes
    ----------
    name
        :class:`str`
        Name of the project
    num
        :class:`int`
        If a project is untitled, they are counted as <untitled-num>
    branches
        List[:class:`.Branch`]
        list of worked branches within the Project
    operative_systems
        List[:class:`.Os`]
        list containing every Os object, representing every s that was used this **date**.
    languages
        List[:class:`.Language`]
        list containing every Language object, representing every programming language that was used this **date**.
    entities
        List[:class:`.Dependency`]
        list containing every Dependency object, representing every dependency that was used this **date**.
    editors
        List[:class:`.Editor`]
        list containing every Editor object, representing every editor that was used this **date**.
    categories
        List[:class:`.Category`]
        list containing every Category object, representing every category that was used this **date**.
    dependencies
        List[:class:`.Dependency`]
        list containing every Dependency object, representing every dependency that was used this **date**.
    grand_total
        :class:`dict`
        Contains the total time data


    """
    untitled_counter = 0

    def __init__(self, _dict):
        self.name = _dict.get('name')

        self.is_untitled = False
        if self.name == 'untitled':
            Project.untitled_counter += 1
            self.is_untitled = True
        self.num = Project.untitled_counter

        self.branches = [Branch(i) for i in _dict.get('branches')]
        self.categories = [Category(i) for i in _dict.get('categories')]
        self.dependencies = [Dependency(i) for i in _dict.get('dependencies')]
        self.editors = [Editor(i) for i in _dict.get('editors')]
        self.entities = [Entity(i) for i in _dict.get('entities')]
        self.languages = [Language(i) for i in _dict.get('languages')]
        self.operative_systems = [Os(i) for i in _dict.get('operating_systems')]
        self.grand_total = GrandTotal(_dict.get('grand_total'))
        self.total_time = self.grand_total.total_time

        self.repr_string = f'-{self.num}' if self.is_untitled else ""

    def __repr__(self):
        return f"class <'{self.__class__.__name__}({self.name}{self.repr_string})'>"


class Os(Parent):
    """
    Class representing a wakatime Operative System data within a one day range.
    """
    def __init__(self, _dict):
        super().__init__(_dict=_dict)


class Language(Parent):
    """
    Class representing a wakatime Programming language data within a one day range.
    """

    def __init__(self, _dict):
        super().__init__(_dict=_dict)


class Entity(Parent):
    """
    Class representing a wakatime Entity data within a one day range.
    A entity can be a module, dependency.. it may vary from plugin to plugin.
    It's only present in :class:`.Project`
    """
    def __init__(self, _dict):
        super().__init__(_dict=_dict)


class Dependency(Parent):
    """
    Class representing a wakatime Entity data within a one day range.
    A entity can be a module, dependency.. it may vary from plugin to plugin.
    """
    def __init__(self, _dict):
        super().__init__(_dict=_dict)


class Category(Parent):
    """
    Class representing a wakatime Category data within a one day range, usually 'Coding'
    """

    def __init__(self, _dict):
        super().__init__(_dict=_dict)


class Editor(Parent):
    """
    Class representing a wakatime Editor data within a one day range, it does not distinguish
    between editors and IDEs
    """

    def __init__(self, _dict):
        super().__init__(_dict=_dict)


class Branch(Parent):

    """
    Class representing a wakatime Branch data within a one day range.
    It's only present in :class:`.Project`
    """

    def __init__(self, _dict):
        super().__init__(_dict=_dict)


class GrandTotal(Parent):
    """
    Class representing a wakatime Grand total data within a one day range.
        It's only present in :class:`.Project`
    """
    def __init__(self, _dict):
        super().__init__(_dict=_dict)
