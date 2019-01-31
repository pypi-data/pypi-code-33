import factory
from .models import Notification
from django.contrib.auth.models import User
from django.db.models.signals import post_save

@factory.django.mute_signals(post_save)
class NotificationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Notification

    type = factory.Faker('text', max_nb_chars=50)
    summary = factory.Faker('paragraph', nb_sentences=3, variable_nb_sentences=True)
    author_user = factory.Faker('url')
    user = factory.Iterator(User.objects.all())
    date = factory.Faker('past_datetime')
    read = factory.Faker('boolean')
    object = factory.Faker('url')