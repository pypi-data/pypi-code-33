import factory
from .models import Circle
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from djangoldp_account.factories import ChatConfigFactory

@factory.django.mute_signals(post_save)
class CircleFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Circle

    name = factory.Faker('word')
    description = factory.Faker('text', max_nb_chars=250)
    owner = factory.Iterator(User.objects.all())

    chatConfig = factory.SubFactory(ChatConfigFactory)

    @factory.post_generation
    def members(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for member in extracted:
                self.team.add(member)
