import factory

from metagenomi.models.assembly import Assembly

from tests.factories.mapping_factory import MappingFactory
from tests.factories.megahit_factory import MegahitFactory


class AssemblyFactory(factory.Factory):
    mgid = factory.Faker('word')
    mgtype = 'assembly'
    Mapping = factory.List([
        factory.SubFactory(MappingFactory),
    ])
    megahit = factory.SubFactory(MegahitFactory)

    class Meta:
        model = Assembly
