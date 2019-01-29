from django.db.models.signals import post_save
from django.dispatch import receiver

from entity.models import Person
from campaign.models import Campaign, Endorsement
from tracker.models import CandidateWinRating, Quote, Story, Tweet, Video
from tracker.celery import get_candidate, homepage, feed


@receiver(post_save, sender=Person)
@receiver(post_save, sender=Campaign)
@receiver(post_save, sender=Endorsement)
@receiver(post_save, sender=CandidateWinRating)
@receiver(post_save, sender=Quote)
@receiver(post_save, sender=Story)
@receiver(post_save, sender=Tweet)
@receiver(post_save, sender=Video)
def rebake_candidate(sender, instance, **kwargs):
    if sender == Person:
        person = instance

    if sender == Campaign:
        person = instance.candidate.person

    if sender == Endorsement:
        person = instance.endorsee.candidate.person

    if sender == CandidateWinRating:
        person = instance.candidate.person

    if sender == Quote:
        person = instance.candidate.person

    if sender == Story:
        person = instance.candidate.person

    if sender == Tweet:
        candidate = instance.candidate
        if not candidate:
            return
        person = instance.candidate.person

    if sender == Video:
        person = instance.candidate.video

    get_candidate.delay(person.pk)
    homepage.delay()
    feed.delay()
