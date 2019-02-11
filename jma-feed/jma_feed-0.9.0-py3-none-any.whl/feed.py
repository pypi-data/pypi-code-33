from jma_feed.xml import XmlDocument


class AtomFeed(XmlDocument):
    """Model class which represents Atom feed."""

    def __init__(self, target):
        super(AtomFeed, self).__init__(target, {'atom': 'http://www.w3.org/2005/Atom'})

    @property
    def title(self):
        return self._element_text('atom:title')

    @property
    def subtitle(self):
        return self._element_text('atom:subtitle')

    @property
    def updated(self):
        return self._element_text('atom:updated')

    @property
    def id(self):
        return self._element_text('atom:id')

    @property
    def rights(self):
        return self._element_text('atom:rights')

    @property
    def entries(self):
        elements = self._elements('atom:entry')
        return [AtomFeedEntry(element) for element in elements]


class AtomFeedEntry(XmlDocument):
    """Model class which represents Atom feed each entry."""

    def __init__(self, target):
        super(AtomFeedEntry, self).__init__(target, {'atom': 'http://www.w3.org/2005/Atom'})

    @property
    def title(self):
        return self._element_text('atom:title')

    @property
    def updated(self):
        return self._element_text('atom:updated')

    @property
    def id(self):
        return self._element_text('atom:id')

    @property
    def author(self):
        return self._element_text('atom:author/atom:name')

    @property
    def content(self):
        return self._element_text('atom:content')

    @property
    def link(self):
        return self._element_attr('atom:link', 'href')
