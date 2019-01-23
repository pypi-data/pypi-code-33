from wakapy.containers import Os, Language, Dependency, Category, Editor, Project


class Day:
    """
    Represents a day. It contains all the data regarding a specific day. Every date is unique.

    Parameters
    -----------
        _dict : :class:`dict`
            A dictionary containing all the data within a one day range.

    Attributes
    -----------
        date
            :class:`str`
            The day's date, main identifier of each instance, Unique.
        is_empty
            :class:`bool`
            True if the day doesn't contain any data.
        year
            :class:`str`
            date's year.
        month
            :class:`str`
            date's month.
        day
            :class:`str`
            date's day.

        container_dict
            :class:`dict`
            shortcut reference to the class containers.

            * os: operative_systems
            * lan: languages
            * ent: entities
            * edit: editors
            * cat: categories
            * proj: projects

        operative_systems
            List[:class:`.Os`]
            List containing every Os object, representing every s that was used this **date**.
        languages
            List[:class:`.Language`]
            List containing every Language object, representing every programming language that was used this **date**.
        entities
            List[:class:`.Dependency`]
            List containing every Dependency object, representing every dependency that was used this **date**.
        editors
            List[:class:`.Editor`]
            List containing every Editor object, representing every editor that was used this **date**.
        categories
            List[:class:`.Category`]
            List containing every Category object, representing every category that was used this **date**.
        projects
            List[:class:`.Project`]
            List containing every Project object, representing every project that was worked on this **date**.



    """
    def __init__(self, _dict: dict):

        self.date = _dict.get('date')
        self.operative_systems = [Os(i) for i in _dict.get('operating_systems')]
        self.languages = [Language(i) for i in _dict.get('languages')]
        self.entities = [Dependency(i) for i in _dict.get('dependencies')]
        self.editors = [Editor(i) for i in _dict.get('editors')]
        self.categories = [Category(i) for i in _dict.get('categories')]
        self.projects = [Project(i) for i in _dict.get('projects')]

        self.year, self.month, self.day = self.date.split('-')

        self.is_empty = bool(not self.operative_systems)
        # This is necessarily true since you cannot work without an Os.

        self.container_dict = {'os': self.operative_systems,
                               'lan': self.languages,
                               'ent': self.entities,
                               'edit': self.editors,
                               'cat': self.categories,
                               'proj': self.projects
                               }

    def split(self, splitwith: str) -> str:
        """
        Allows the direct **date** split.

        :param splitwith: :class:`str`
            str.split(splitwith)

        Note
        ----
        This is the same as:
        day.date.split('')


        :return: :class:`str`
        """
        return self.date.split(splitwith)

    def __repr__(self):
        return f"<class '{self.__class__.__name__}({self.date})'>"
