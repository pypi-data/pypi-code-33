class Registry(object):
    """Handles updating registered translators when the active locale needs to change"""

    def __init__(self):
        self._locales = None

        self.translators = set()
        self.locales = None

    @property
    def locales(self):
        return self._locales

    @locales.setter
    def locales(self, value):
        self._locales = value

        for translator in self.translators:
            translator.locales = self._locales

    def subscribe(self, translator):
        self.translators.add(translator)

    def unsubscribe(self, translator):
        self.translators.remove(translator)


# Create a default registry singleton
default_registry = Registry()
