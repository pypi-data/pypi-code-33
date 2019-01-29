from django.db import models
from election.models import Candidate
from .candidate_rating_category import CandidateRatingCategory


class CandidateWinRating(models.Model):
    """
    Rating the likelihood a candidate will run
    """

    candidate = models.ForeignKey(
        Candidate, on_delete=models.PROTECT, related_name="win_ratings"
    )
    date = models.DateTimeField(auto_now=True)
    category = models.ForeignKey(
        CandidateRatingCategory,
        on_delete=models.PROTECT,
        related_name="win_ratings",
    )
