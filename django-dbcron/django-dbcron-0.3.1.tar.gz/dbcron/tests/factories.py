from faker import Faker
import factory
from factory import fuzzy

faker = Faker()


class Fuzzy(fuzzy.FuzzyInteger):
    def __init__(self, low=None, high=None, *args, **kwargs):
        super().__init__(low=self.low, high=self.high, *args, **kwargs)

    def fuzz(self):
        value = super().fuzz()
        return str(value)


class FuzzyMinute(Fuzzy):
    low = 0
    high = 59


class FuzzyHour(Fuzzy):
    low = 0
    high = 23


class JobFactory(factory.django.DjangoModelFactory):
    name = factory.Faker('job')
    tag = factory.Faker('name')
    func = 'django.utils.timezone.now'

    sec = '0'
    min = FuzzyMinute(0, 59)
    hou = FuzzyHour(0, 23)
    dom = '*'
    mon = '*'
    dow = '*'
    yea = '*'

    class Meta:
        model = 'dbcron.Job'
