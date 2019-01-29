from django.db import models


class CandidateRatingCategory(models.Model):
    """
    Tier of ranking
    """

    label = models.CharField(max_length=50)
    order = models.PositiveSmallIntegerField()

    def __str__(self):
        return self.label
