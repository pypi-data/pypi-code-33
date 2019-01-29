import csv
import os

from django.core.management.base import BaseCommand
from campaign.models import Campaign
from election.models import ElectionCycle, Race, Candidate
from entity.models import Person
from government.models import Office, Party
from tracker.models import (
    CandidateRatingCategory,
    CandidateWinRating,
    CampaignContent,
)


class Command(BaseCommand):
    def handle(self, *args, **options):
        new_cycle = ElectionCycle.objects.get_or_create(name="2020")[0]
        president = Office.objects.get(slug="president")
        presidential_race = Race.objects.get_or_create(
            cycle=new_cycle, office=president
        )[0]

        ratings = [
            {"label": "Contender", "order": 1},
            {"label": "Underdog", "order": 2},
            {"label": "Longshot", "order": 3},
        ]

        for rating in ratings:
            CandidateRatingCategory.objects.get_or_create(**rating)

        self.cmd_path = os.path.dirname(os.path.realpath(__file__))
        with open(
            os.path.join(self.cmd_path, "../../bin/candidates.csv")
        ) as f:
            reader = csv.DictReader(f)

            for row in reader:
                print(row)
                party = Party.objects.get(slug=row["party"])

                person_defaults = {
                    "gender": row["gender"][0].upper(),
                    "birth_date": row["birth_date"],
                }

                person = Person.objects.update_or_create(
                    first_name=row["first"],
                    last_name=row["last"],
                    defaults=person_defaults,
                )[0]
                candidate = Candidate.objects.get_or_create(
                    person=person, race=presidential_race, party=party
                )[0]
                campaign = Campaign.objects.get_or_create(candidate=candidate)[
                    0
                ]

                rating_category = CandidateRatingCategory.objects.get(
                    label=row["win_rating"]
                )

                CandidateWinRating.objects.get_or_create(
                    candidate=candidate, category=rating_category
                )
                CampaignContent.objects.get_or_create(
                    campaign=campaign, blurb=row["blurb"]
                )
