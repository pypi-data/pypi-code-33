from django.db import models
from election.models import Candidate
from .candidate_ranking_set import CandidateRankingSet


class CandidateRanking(models.Model):
    candidate = models.ForeignKey(
        Candidate,
        on_delete=models.PROTECT,
        related_name="rankings",
        limit_choices_to={
            "race__cycle__slug": "2020",
            "race__office__slug": "president",
        },
    )
    value = models.PositiveSmallIntegerField()
    explanation = models.TextField()
    ranking_set = models.ForeignKey(
        CandidateRankingSet, on_delete=models.CASCADE, related_name="rankings"
    )

    def __str__(self):
        return "{} {} {}".format(
            self.candidate.person.full_name,
            self.value,
            self.ranking_set.date.strftime("%m-%d-%y"),
        )

    class Meta:
        unique_together = (("ranking_set", "candidate"),)
