from election.models import Candidate
from entity.models import Person
from tracker.utils.bakeries import bake_candidate, bake_homepage, bake_feed
from celery import shared_task


@shared_task(acks_late=True)
def get_candidate(pk):
    person = Person.objects.get(pk=pk)
    try:
        candidacy = person.candidacies.get(
            race__cycle__slug="2020", race__office__slug="president"
        )
    except:
        return

    bake_candidate(candidacy)


@shared_task(acks_late=True)
def homepage():
    candidates = Candidate.objects.filter(
        race__cycle__slug="2020", race__office__slug="president"
    )
    bake_homepage(candidates)


@shared_task(acks_late=True)
def feed():
    candidates = Candidate.objects.filter(
        race__cycle__slug="2020", race__office__slug="president"
    )
    bake_feed(candidates)
