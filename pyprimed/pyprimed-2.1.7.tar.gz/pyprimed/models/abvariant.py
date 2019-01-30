from ..const import API_PATH
from .base import Resource


class Abvariant(Resource):
    PATH = API_PATH["abvariants.abvariant"]


class ControlAbvariant:
    """Describes a ControlAbvariant

        ```
        from pyprimed.models.abvariant import ControlAbvariant

        u = pio.universes.find(name='myuniverse').first
        c = u.campaigns.all().first
        e = c.experiments.all().first

        control = ControlAbvariant(label='C')

        e.abvariants.create({control: 1.0})
        ```

        :param label: `Abvariant` label, e.g.: 'A' or 'MySpecialVariant'
        :type label: str
        """
    def __init__(self, label):
        self.label = label
        self.type = "__CONTROL__"

    def toDict(self, exclude=["id"]):
        """Converts an object to a Python dictionary, optionally excluding fields such as "password" """
        state = self.__dict__.copy()

        for field in exclude:
            if field in state:
                del state[field]

        return state


class CustomAbvariant:
    def __init__(self, label, models, dithering=False, epsilon=1.5, recency=False):
        """Describes a CustomAbvariant

        ```
        from pyprimed.models.abvariant import CustomAbvariant

        u = pio.universes.find(name='myuniverse').first
        c = u.campaigns.all().first
        e = c.experiments.all().first

        m1 = pio.models.find(name='mymodel').first
        m2 = pio.models.find(name='myothermodel').first

        ab1 = CustomAbvariant(label='A', models={m1: 0.6, m2: 0.4})
        ab2 = CustomAbvariant(label='B', models={m1: 1.0})

        e.abvariants.create({ab1: 0.8, ab2: 0.1})
        ```

        :param label: `Abvariant` label, e.g.: 'A' or 'MySpecialVariant'
        :type label: str
        :param models: models and corresponding weights: {mymodel: 0.1, anothermodel: 0.9}
        :type models: dict
        :param dithering: should this Abvariant serve dithered results, defaults to False
        :type dithering: bool, optional
        :param recency: should this Abvariant apply recency, defaults to False
        :type recency: bool, optional
        """
        self.label = label
        self.dithering = dithering
        self.recency = recency
        self.type = "__CUSTOM__"

        assert isinstance(
            models, dict
        ), "models should be a dictionary with models as keys, and weights as values: `{mymodel: 0.3, anothermodel:0.7}`"
        self.models = models

    def toDict(self, exclude=["id"]):
        """Converts an object to a Python dictionary, optionally excluding fields such as "password" """
        state = self.__dict__.copy()

        for field in exclude:
            if field in state:
                del state[field]

        return state
