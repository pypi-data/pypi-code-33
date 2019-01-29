from django.core.management.base import BaseCommand
from election.models import Candidate
from tracker.utils.bakeries import bake_feed_summary


class Command(BaseCommand):
    def handle(self, *args, **options):
        candidates = Candidate.objects.filter(
            race__cycle__slug="2020",
            race__office__slug="president",
            party__ap_code="Dem",
        )
        bake_feed_summary(candidates)
